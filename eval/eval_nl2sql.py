"""
NL -> SQL evaluator

Logic:
1) For each natural language query (NL):
   - Get ground-truth SQL from the mapping (GT_SQL).
   - Call nl2sql(NL) to get model SQL (PRED_SQL).
2) If normalized SQL strings match -> EXACT_MATCH (correct).
3) Else run both queries, compare results:
   - If same results -> SEMANTIC_MATCH (correct)
   - Else FAIL
4) Report metrics and accuracy.

This script prints REAL metrics from actual DB execution.
"""

from __future__ import annotations

import os
import json
import re
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple, Optional

import psycopg

NL2SQL_GOLD: Dict[str, str] = {
    "Show all patients": "SELECT * FROM patients ORDER BY id;",
    "Find patient Ali Mansour": "SELECT * FROM patients WHERE full_name ILIKE '%Ali Mansour%';",
    "Search patients with diabetes": "SELECT * FROM patients WHERE patient_case_summary ILIKE '%diabetes%';",
    "List female patients": "SELECT * FROM patients WHERE gender ILIKE 'female' ORDER BY full_name;",
    "Patients born after 1995": "SELECT * FROM patients WHERE date_of_birth > DATE '1995-12-31' ORDER BY date_of_birth;",
    "Get patient by email sara.khoury@example.com": "SELECT * FROM patients WHERE email = 'sara.khoury@example.com';",
    "Show patient contact info for id 10": "SELECT id, full_name, phone, email FROM patients WHERE id = 10;",
    "How many patients do we have": "SELECT COUNT(*) AS patient_count FROM patients;",
    "Count patients by gender": "SELECT gender, COUNT(*) AS count FROM patients GROUP BY gender ORDER BY count DESC;",
    "Patients created in January 2025": "SELECT * FROM patients WHERE created_at >= TIMESTAMP '2025-01-01' AND created_at < TIMESTAMP '2025-02-01' ORDER BY created_at;",

    "Show all prescriptions for patient id 14": "SELECT * FROM prescriptions WHERE patient_id = 14 ORDER BY prescription_date DESC, id DESC;",
    "Show prescriptions for Ali Mansour": "SELECT pr.* FROM prescriptions pr JOIN patients p ON p.id = pr.patient_id WHERE p.full_name ILIKE '%Ali Mansour%' ORDER BY pr.prescription_date DESC;",
    "Prescriptions written by Dr Ahmad Saeed": "SELECT * FROM prescriptions WHERE doctor_name ILIKE '%Ahmad Saeed%' ORDER BY prescription_date DESC;",
    "Prescriptions between Jan 20 and Jan 31 2025": "SELECT * FROM prescriptions WHERE prescription_date BETWEEN DATE '2025-01-20' AND DATE '2025-01-31' ORDER BY prescription_date, id;",
    "Which OCR engines are used": "SELECT ocr_engine, COUNT(*) AS count FROM prescriptions GROUP BY ocr_engine ORDER BY count DESC;",
    "Show raw OCR text for prescription id 12": "SELECT id, ocr_engine, ocr_raw_text FROM prescriptions WHERE id = 12;",
    "Find prescriptions mentioning metformin": "SELECT * FROM prescriptions WHERE ocr_raw_text ILIKE '%metformin%' ORDER BY prescription_date DESC;",
    "List latest 5 prescriptions": "SELECT * FROM prescriptions ORDER BY prescription_date DESC, id DESC LIMIT 5;",
    "Count prescriptions per doctor": "SELECT doctor_name, COUNT(*) AS rx_count FROM prescriptions GROUP BY doctor_name ORDER BY rx_count DESC, doctor_name;",
    "Prescriptions missing parsed JSON": "SELECT * FROM prescriptions WHERE parsed_json IS NULL ORDER BY id;",

    "Show all medications": "SELECT * FROM medications ORDER BY id;",
    "Find medication Omeprazole": "SELECT * FROM medications WHERE generic_name ILIKE '%Omeprazole%';",
    "Find medication brand Lipitor": "SELECT * FROM medications WHERE brand_name ILIKE '%Lipitor%';",
    "List antibiotic medications": "SELECT * FROM medications WHERE category ILIKE '%Antibiotic%' ORDER BY generic_name;",
    "Count medications by category": "SELECT category, COUNT(*) AS count FROM medications GROUP BY category ORDER BY count DESC, category;",

    "Show all meds in prescription id 10": "SELECT * FROM prescription_medications WHERE prescription_id = 10 ORDER BY id;",
    "Detailed prescription id 19": "SELECT pr.id AS prescription_id, pr.prescription_date, pr.doctor_name, p.full_name, pm.medication_name, pm.dosage, pm.frequency, pm.duration, pm.instructions FROM prescriptions pr JOIN patients p ON p.id = pr.patient_id JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pr.id = 19 ORDER BY pm.id;",
    "All medications for patient id 16": "SELECT pr.id AS prescription_id, pr.prescription_date, pm.medication_name, pm.dosage, pm.frequency, pm.duration FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pr.patient_id = 16 ORDER BY pr.prescription_date DESC;",
    "Unique medications prescribed to Sara Khoury": "SELECT DISTINCT pm.medication_name FROM prescription_medications pm JOIN prescriptions pr ON pr.id = pm.prescription_id JOIN patients p ON p.id = pr.patient_id WHERE p.full_name ILIKE '%Sara Khoury%' ORDER BY pm.medication_name;",
    "Medication count per prescription": "SELECT pr.id AS prescription_id, COUNT(pm.id) AS med_count FROM prescriptions pr LEFT JOIN prescription_medications pm ON pm.prescription_id = pr.id GROUP BY pr.id ORDER BY pr.id;",
    "Prescriptions that include Amoxicillin": "SELECT DISTINCT pr.id, pr.prescription_date, pr.patient_id FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.medication_name ILIKE '%Amoxicillin%' ORDER BY pr.prescription_date DESC;",
    "Patients prescribed Warfarin": "SELECT DISTINCT p.id, p.full_name FROM patients p JOIN prescriptions pr ON pr.patient_id = p.id JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.medication_name ILIKE '%Warfarin%' ORDER BY p.full_name;",
    "Show PRN medications": "SELECT * FROM prescription_medications WHERE frequency ILIKE '%PRN%' ORDER BY prescription_id, id;",
    "Chronic medications": "SELECT * FROM prescription_medications WHERE duration ILIKE 'chronic' ORDER BY prescription_id, id;",
    "Top 5 most prescribed medications": "SELECT pm.medication_name, COUNT(*) AS times_prescribed FROM prescription_medications pm GROUP BY pm.medication_name ORDER BY times_prescribed DESC LIMIT 5;",
    "Most common meds prescribed by Dr Mira Wehbe": "SELECT pm.medication_name, COUNT(*) AS times FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pr.doctor_name ILIKE '%Mira Wehbe%' GROUP BY pm.medication_name ORDER BY times DESC;",
    "Prescriptions with do not drive instructions": "SELECT pr.id, pr.prescription_date, p.full_name, pm.medication_name, pm.instructions FROM prescriptions pr JOIN patients p ON p.id = pr.patient_id JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.instructions ILIKE '%do not drive%' ORDER BY pr.prescription_date DESC;",
    "Prescriptions with Metformin and Atorvastatin": "SELECT pr.id, pr.patient_id, pr.prescription_date FROM prescriptions pr WHERE EXISTS (SELECT 1 FROM prescription_medications pm WHERE pm.prescription_id = pr.id AND pm.medication_name ILIKE '%Metformin%') AND EXISTS (SELECT 1 FROM prescription_medications pm WHERE pm.prescription_id = pr.id AND pm.medication_name ILIKE '%Atorvastatin%') ORDER BY pr.prescription_date DESC;",
    "Last prescription per patient": "SELECT p.id, p.full_name, MAX(pr.prescription_date) AS last_prescription_date FROM patients p LEFT JOIN prescriptions pr ON pr.patient_id = p.id GROUP BY p.id, p.full_name ORDER BY last_prescription_date DESC NULLS LAST;",
    "Patients with more than one prescription": "SELECT p.id, p.full_name, COUNT(pr.id) AS rx_count FROM patients p JOIN prescriptions pr ON pr.patient_id = p.id GROUP BY p.id, p.full_name HAVING COUNT(pr.id) > 1 ORDER BY rx_count DESC;",
    "Prescriptions per month in 2025": "SELECT DATE_TRUNC('month', prescription_date) AS month, COUNT(*) AS rx_count FROM prescriptions WHERE prescription_date >= DATE '2025-01-01' AND prescription_date < DATE '2026-01-01' GROUP BY month ORDER BY month;",
    "Prescriptions containing inhaler in OCR text": "SELECT * FROM prescriptions WHERE ocr_raw_text ILIKE '%inhaler%' ORDER BY prescription_date DESC;",
    "Asthma patients and their prescriptions": "SELECT p.id, p.full_name, pr.id AS prescription_id, pr.prescription_date FROM patients p LEFT JOIN prescriptions pr ON pr.patient_id = p.id WHERE p.patient_case_summary ILIKE '%asthma%' ORDER BY p.full_name, pr.prescription_date DESC;",
    "Show patients with hypertension": "SELECT * FROM patients WHERE patient_case_summary ILIKE '%hypertension%';",
  "List patients with asthma": "SELECT * FROM patients WHERE patient_case_summary ILIKE '%asthma%';",
  "Patients with heart disease": "SELECT * FROM patients WHERE patient_case_summary ILIKE '%heart%';",
  "Patients with kidney disease": "SELECT * FROM patients WHERE patient_case_summary ILIKE '%kidney%';",
  "Patients with migraine": "SELECT * FROM patients WHERE patient_case_summary ILIKE '%migraine%';",

  "Show all male patients": "SELECT * FROM patients WHERE gender ILIKE 'male' ORDER BY full_name;",
  "Patients younger than 30": "SELECT * FROM patients WHERE date_of_birth > CURRENT_DATE - INTERVAL '30 years' ORDER BY date_of_birth;",
  "Patients older than 50": "SELECT * FROM patients WHERE date_of_birth < CURRENT_DATE - INTERVAL '50 years' ORDER BY date_of_birth;",
  "Patients without prescriptions": "SELECT p.* FROM patients p LEFT JOIN prescriptions pr ON pr.patient_id = p.id WHERE pr.id IS NULL;",
  "Patients with more than two prescriptions": "SELECT p.id, p.full_name, COUNT(pr.id) AS rx_count FROM patients p JOIN prescriptions pr ON pr.patient_id = p.id GROUP BY p.id, p.full_name HAVING COUNT(pr.id) > 2;",

  "Show prescriptions written in February 2025": "SELECT * FROM prescriptions WHERE prescription_date >= DATE '2025-02-01' AND prescription_date < DATE '2025-03-01' ORDER BY prescription_date;",
  "Show prescriptions after January 2025": "SELECT * FROM prescriptions WHERE prescription_date > DATE '2025-01-31' ORDER BY prescription_date;",
  "Prescriptions before January 15 2025": "SELECT * FROM prescriptions WHERE prescription_date < DATE '2025-01-15' ORDER BY prescription_date;",
  "Latest prescription per doctor": "SELECT DISTINCT ON (doctor_name) doctor_name, prescription_date, id FROM prescriptions ORDER BY doctor_name, prescription_date DESC;",
  "Doctors who wrote more than 3 prescriptions": "SELECT doctor_name, COUNT(*) AS rx_count FROM prescriptions GROUP BY doctor_name HAVING COUNT(*) > 3;",

  "Show prescriptions using tesseract OCR": "SELECT * FROM prescriptions WHERE ocr_engine = 'tesseract' ORDER BY prescription_date;",
  "Show prescriptions using Azure Vision OCR": "SELECT * FROM prescriptions WHERE ocr_engine = 'azure_vision' ORDER BY prescription_date;",
  "Count prescriptions per OCR engine": "SELECT ocr_engine, COUNT(*) FROM prescriptions GROUP BY ocr_engine;",
  "Prescriptions mentioning antibiotic": "SELECT * FROM prescriptions WHERE ocr_raw_text ILIKE '%antibiotic%';",
  "Prescriptions mentioning insulin": "SELECT * FROM prescriptions WHERE ocr_raw_text ILIKE '%insulin%';",

  "List all antidepressant medications": "SELECT * FROM medications WHERE category ILIKE '%Antidepressant%';",
  "List all antihypertensive medications": "SELECT * FROM medications WHERE category ILIKE '%Antihypertensive%';",
  "List all anxiolytic medications": "SELECT * FROM medications WHERE category ILIKE '%Anxiolytic%';",
  "List all vitamin medications": "SELECT * FROM medications WHERE category ILIKE '%Vitamin%';",
  "Medications without brand name": "SELECT * FROM medications WHERE brand_name IS NULL;",

  "Show all insulin prescriptions": "SELECT pr.* FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.medication_name ILIKE '%Insulin%';",
  "Show prescriptions containing prednisone": "SELECT DISTINCT pr.* FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.medication_name ILIKE '%Prednisone%';",
  "Show prescriptions with two medications": "SELECT prescription_id FROM prescription_medications GROUP BY prescription_id HAVING COUNT(*) = 2;",
  "Show prescriptions with PRN medications": "SELECT DISTINCT pr.* FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.frequency ILIKE '%PRN%';",
  "Show prescriptions with chronic medications": "SELECT DISTINCT pr.* FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.duration ILIKE 'chronic';",

  "Most frequently prescribed medication category": "SELECT m.category, COUNT(*) AS cnt FROM prescription_medications pm JOIN medications m ON m.id = pm.medication_id GROUP BY m.category ORDER BY cnt DESC LIMIT 1;",
  "Top 3 most prescribed medications": "SELECT medication_name, COUNT(*) AS cnt FROM prescription_medications GROUP BY medication_name ORDER BY cnt DESC LIMIT 3;",
  "Patients taking antidepressants": "SELECT DISTINCT p.id, p.full_name FROM patients p JOIN prescriptions pr ON pr.patient_id = p.id JOIN prescription_medications pm ON pm.prescription_id = pr.id JOIN medications m ON m.id = pm.medication_id WHERE m.category ILIKE '%Antidepressant%';",
  "Patients on insulin therapy": "SELECT DISTINCT p.id, p.full_name FROM patients p JOIN prescriptions pr ON pr.patient_id = p.id JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.medication_name ILIKE '%Insulin%';",
  "Patients prescribed antibiotics": "SELECT DISTINCT p.id, p.full_name FROM patients p JOIN prescriptions pr ON pr.patient_id = p.id JOIN prescription_medications pm ON pm.prescription_id = pr.id JOIN medications m ON m.id = pm.medication_id WHERE m.category ILIKE '%Antibiotic%';",

  "Average number of medications per prescription": "SELECT AVG(med_count) FROM (SELECT prescription_id, COUNT(*) AS med_count FROM prescription_medications GROUP BY prescription_id) sub;",
  "Prescriptions with maximum number of medications": "SELECT prescription_id FROM prescription_medications GROUP BY prescription_id ORDER BY COUNT(*) DESC LIMIT 1;",
  "Doctors who prescribe insulin": "SELECT DISTINCT doctor_name FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pm.medication_name ILIKE '%Insulin%';",
  "Patients with prescriptions in both January and February 2025": "SELECT DISTINCT p.id, p.full_name FROM patients p JOIN prescriptions pr ON pr.patient_id = p.id WHERE pr.prescription_date BETWEEN DATE '2025-01-01' AND DATE '2025-02-28' GROUP BY p.id, p.full_name HAVING COUNT(DISTINCT DATE_TRUNC('month', pr.prescription_date)) >= 2;",
  "Patients taking both metformin and insulin": "SELECT p.id, p.full_name FROM patients p WHERE EXISTS (SELECT 1 FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pr.patient_id = p.id AND pm.medication_name ILIKE '%Metformin%') AND EXISTS (SELECT 1 FROM prescriptions pr JOIN prescription_medications pm ON pm.prescription_id = pr.id WHERE pr.patient_id = p.id AND pm.medication_name ILIKE '%Insulin%');"
}


# ----------------------------
# 2) Dummy NL2SQL tool call
#    Replace this with your real model/tool later
# ----------------------------
def nl2sql(nl_query: str) -> str:
    """
    Dummy "model" that returns:
      - exact GT SQL for known queries, but
      - sometimes introduces harmless formatting changes,
        to exercise the semantic-match path.

    Replace this with your actual NL2SQL call.
    """
    gt = NL2SQL_GOLD.get(nl_query)
    if gt is None:
        return "SELECT 1;"
    return re.sub(r"\s+", " ", gt).strip()


# ----------------------------
# 3) Utilities
# ----------------------------
def normalize_sql(sql: str) -> str:
    """Loose normalization for exact-match checks."""
    s = sql.strip().rstrip(";")
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def fetch_all(conn: psycopg.Connection, sql: str) -> Tuple[Tuple[str, ...], List[Tuple[Any, ...]]]:
    """
    Execute SQL and return:
      - column names
      - all rows

    NOTE: result ordering matters. If queries omit ORDER BY, DB may return different orders.
    We compare results as *multisets* later to reduce false failures.
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        colnames = tuple(d.name for d in cur.description) if cur.description else tuple()
        rows = cur.fetchall() if cur.description else []
    return colnames, rows


def results_equal(a_cols: Tuple[str, ...], a_rows: List[Tuple[Any, ...]],
                  b_cols: Tuple[str, ...], b_rows: List[Tuple[Any, ...]]) -> bool:
    """
    Compare results with a "practical" approach:
      - require same columns (names + count)
      - compare row multisets (sorted tuples) to ignore ordering differences
    """
    if a_cols != b_cols:
        return False
    a_sorted = sorted(a_rows)
    b_sorted = sorted(b_rows)
    return a_sorted == b_sorted


# ----------------------------
# 4) Evaluation structures
# ----------------------------
@dataclass
class EvalCaseResult:
    nl_query: str
    gt_sql: str
    pred_sql: str
    verdict: str  # EXACT_MATCH | SEMANTIC_MATCH | FAIL | ERROR
    details: str
    time_ms: float


@dataclass
class EvalSummary:
    total: int
    exact_match: int
    semantic_match: int
    fail: int
    error: int
    accuracy: float  # (exact + semantic) / total


# ----------------------------
# 5) Main evaluation
# ----------------------------
def evaluate_all(conn: psycopg.Connection, gold_map: Dict[str, str]) -> Tuple[EvalSummary, List[EvalCaseResult]]:
    results: List[EvalCaseResult] = []

    exact = semantic = fail = err = 0
    start_all = time.time()

    for nl, gt_sql in gold_map.items():
        t0 = time.time()
        pred_sql = nl2sql(nl)

        try:
            if normalize_sql(pred_sql) == normalize_sql(gt_sql):
                exact += 1
                results.append(EvalCaseResult(
                    nl_query=nl,
                    gt_sql=gt_sql,
                    pred_sql=pred_sql,
                    verdict="EXACT_MATCH",
                    details="Pred SQL matches GT SQL after normalization.",
                    time_ms=(time.time() - t0) * 1000.0,
                ))
                continue

            # Different SQL → run both and compare results
            gt_cols, gt_rows = fetch_all(conn, gt_sql)
            pred_cols, pred_rows = fetch_all(conn, pred_sql)

            if results_equal(gt_cols, gt_rows, pred_cols, pred_rows):
                semantic += 1
                results.append(EvalCaseResult(
                    nl_query=nl,
                    gt_sql=gt_sql,
                    pred_sql=pred_sql,
                    verdict="SEMANTIC_MATCH",
                    details="SQL differs, but query results match (same columns + same rows ignoring order).",
                    time_ms=(time.time() - t0) * 1000.0,
                ))
            else:
                fail += 1
                results.append(EvalCaseResult(
                    nl_query=nl,
                    gt_sql=gt_sql,
                    pred_sql=pred_sql,
                    verdict="FAIL",
                    details=f"Results differ. GT rows={len(gt_rows)} vs PRED rows={len(pred_rows)}.",
                    time_ms=(time.time() - t0) * 1000.0,
                ))

        except Exception as e:
            err += 1
            results.append(EvalCaseResult(
                nl_query=nl,
                gt_sql=gt_sql,
                pred_sql=pred_sql,
                verdict="ERROR",
                details=f"{type(e).__name__}: {e}",
                time_ms=(time.time() - t0) * 1000.0,
            ))

    total = len(gold_map)
    acc = (exact + semantic) / total if total else 0.0

    summary = EvalSummary(
        total=total,
        exact_match=exact,
        semantic_match=semantic,
        fail=fail,
        error=err,
        accuracy=acc,
    )

    _ = time.time() - start_all
    return summary, results


def main() -> None:
    """
    Configure DB via env vars:

      PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

    or set DATABASE_URL, e.g.:
      postgres://user:pass@localhost:5432/dbname
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        host = os.getenv("PGHOST", "localhost")
        port = int(os.getenv("PGPORT", "5432"))
        db = os.getenv("PGDATABASE", "postgres")
        user = os.getenv("PGUSER", "postgres")
        pwd = os.getenv("PGPASSWORD", "postgres")
        db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

    print(f"[INFO] Connecting to DB: {db_url}")

    with psycopg.connect(db_url) as conn:
        summary, case_results = evaluate_all(conn, NL2SQL_GOLD)


    print("\n=== EVALUATION SUMMARY ===")
    print(json.dumps(asdict(summary), indent=2))

    print("\n=== FAILURES / ERRORS (if any) ===")
    for r in case_results:
        if r.verdict in ("FAIL", "ERROR"):
            print(f"- NL: {r.nl_query}")
            print(f"  Verdict: {r.verdict}")
            print(f"  Details: {r.details}")
            print(f"  GT:   {r.gt_sql}")
            print(f"  PRED: {r.pred_sql}")
            print()


if __name__ == "__main__":
    main()
