
# tools/templated_query_tool.py
"""
Provides templated SQL queries for common database operations and generates charts based on query results.
"""

import matplotlib.pyplot as plt
import io
import base64

QUERIES = {
	"get_patient_by_id": {
		"sql": "SELECT * FROM patients WHERE id = %(patient_id)s;",
		"chart": None  
	},
	"get_prescriptions_for_patient": {
		"sql": "SELECT * FROM prescriptions WHERE patient_id = %(patient_id)s ORDER BY prescription_date DESC;",
		"chart": "prescription_dates"
	},
	"get_medications_for_prescription": {
		"sql": "SELECT m.* FROM prescription_medications pm JOIN medications m ON pm.medication_id = m.id WHERE pm.prescription_id = %(prescription_id)s;",
		"chart": "medication_types"
	},
	"search_patients_by_name": {
		"sql": "SELECT * FROM patients WHERE full_name ILIKE %(name)s;",
		"chart": "age_distribution"
	},
	"get_recent_prescriptions": {
		"sql": "SELECT * FROM prescriptions ORDER BY created_at DESC LIMIT 10;",
		"chart": "recent_prescriptions"
	},
	"patient_age_distribution_by_gender": {
		"sql": "SELECT gender, EXTRACT(YEAR FROM AGE(date_of_birth)) AS age FROM patients;",
		"chart": "age_gender_stacked"
	},
	"top_prescribed_medication_categories": {
		"sql": "SELECT m.category, COUNT(*) AS count FROM prescription_medications pm JOIN medications m ON pm.medication_id = m.id GROUP BY m.category ORDER BY count DESC;",
		"chart": "category_pie"
	},
	"monthly_prescription_trends": {
		"sql": "SELECT TO_CHAR(prescription_date, 'YYYY-MM') AS month, COUNT(*) FROM prescriptions WHERE prescription_date > CURRENT_DATE - INTERVAL '1 year' GROUP BY month ORDER BY month;",
		"chart": "monthly_line"
	},
	"doctor_prescription_frequency": {
		"sql": "SELECT doctor_name, COUNT(*) AS count FROM prescriptions GROUP BY doctor_name ORDER BY count DESC LIMIT 10;",
		"chart": "doctor_bar"
	},
	"medication_dosage_patterns": {
		"sql": "SELECT medication_name, dosage, COUNT(*) AS count FROM prescription_medications GROUP BY medication_name, dosage ORDER BY count DESC;",
		"chart": "dosage_grouped_bar"
	}
}

def execute_query_and_chart(query_name, db_conn, params):
	if query_name not in QUERIES:
		raise ValueError(f"Unknown query name: {query_name}")
	sql = QUERIES[query_name]["sql"]
	chart_type = QUERIES[query_name]["chart"]
	with db_conn.cursor() as cur:
		cur.execute(sql, params)
		results = cur.fetchall()
		columns = [desc[0] for desc in cur.description]
	overview = {
		"row_count": len(results),
		"columns": columns,
		"sample": results[:3]
	}
	chart_img = None
	if chart_type:
		chart_img = generate_chart(chart_type, results, columns)
	return overview, chart_img

def generate_chart(chart_type, results, columns):
	plt.figure(figsize=(6,4))
	if chart_type == "prescription_dates":
		dates = [r[columns.index("prescription_date")] for r in results]
		plt.hist(dates, bins=10)
		plt.title("Prescription Dates Distribution")
		plt.xlabel("Date")
		plt.ylabel("Count")
	elif chart_type == "medication_types":
		meds = [r[columns.index("name")] for r in results]
		plt.barh(list(set(meds)), [meds.count(m) for m in set(meds)])
		plt.title("Medication Types")
		plt.xlabel("Count")
	elif chart_type == "age_distribution":
		if "age" in columns:
			ages = [r[columns.index("age")] for r in results]
			plt.hist(ages, bins=10)
			plt.title("Patient Age Distribution")
			plt.xlabel("Age")
			plt.ylabel("Count")
	elif chart_type == "recent_prescriptions":
		dates = [r[columns.index("created_at")] for r in results]
		plt.plot(dates, range(len(dates)), marker='o')
		plt.title("Recent Prescriptions Timeline")
		plt.xlabel("Date")
		plt.ylabel("Index")
	elif chart_type == "age_gender_stacked":
		import pandas as pd
		df = pd.DataFrame(results, columns=columns)
		df['age_bucket'] = (df['age']//10)*10
		pivot = df.pivot_table(index='age_bucket', columns='gender', aggfunc='size', fill_value=0)
		pivot.plot(kind='bar', stacked=True, colormap='coolwarm')
		plt.title("Patient Age Distribution by Gender")
		plt.xlabel("Age Bucket")
		plt.ylabel("Count")
	elif chart_type == "category_pie":
		cats = [r[columns.index("category")] for r in results]
		counts = [r[columns.index("count")] for r in results]
		plt.pie(counts, labels=cats, autopct='%1.1f%%', colors=plt.cm.Pastel1.colors)
		plt.title("Top Prescribed Medication Categories")
	elif chart_type == "monthly_line":
		months = [r[columns.index("month")] for r in results]
		counts = [r[1] for r in results]
		plt.plot(months, counts, marker='o', color='navy')
		plt.xticks(rotation=45)
		plt.title("Monthly Prescription Trends")
		plt.xlabel("Month")
		plt.ylabel("Prescriptions")
	elif chart_type == "doctor_bar":
		doctors = [r[columns.index("doctor_name")] for r in results]
		counts = [r[columns.index("count")] for r in results]
		plt.barh(doctors, counts, color='limegreen')
		plt.title("Top Doctors by Prescription Frequency")
		plt.xlabel("Prescriptions")
	elif chart_type == "dosage_grouped_bar":
		import pandas as pd
		df = pd.DataFrame(results, columns=columns)
		pivot = df.pivot_table(index='medication_name', columns='dosage', values='count', fill_value=0)
		pivot.plot(kind='bar', colormap='viridis')
		plt.title("Medication Dosage Patterns")
		plt.xlabel("Medication Name")
		plt.ylabel("Count")
	else:
		plt.text(0.5, 0.5, "No chart available", ha='center')
	buf = io.BytesIO()
	plt.tight_layout()
	plt.savefig(buf, format='png')
	plt.close()
	buf.seek(0)
	img_base64 = base64.b64encode(buf.read()).decode('utf-8')
	return img_base64
