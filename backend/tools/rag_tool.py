from __future__ import annotations

import os
import json
from typing import Optional, List
import httpx


class QwenEmbedder:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 60.0):
        self.base_url = (base_url or os.getenv("QWEN_EMBEDDING_URL", "http://localhost:9977")).rstrip("/")
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json"}

    def _post(self, url: str, text: str):
        payload = {"inputs": [text]}
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    def embed(self, text: str) -> Optional[List[float]]:
        try:
            try:
                result = self._post(self.base_url, text)
            except httpx.HTTPStatusError:
                result = self._post(f"{self.base_url}/embed", text)

            if isinstance(result, dict) and "embeddings" in result:
                return result["embeddings"][0] if result["embeddings"] else None

            if isinstance(result, list):
                return result[0] if result and isinstance(result[0], list) else None

            if isinstance(result, dict) and "data" in result and result["data"]:
                item = result["data"][0]
                return item.get("embedding") if isinstance(item, dict) else item

        except Exception:
            return None

        return None


class RAGService:
    def __init__(self, embedder: Optional[QwenEmbedder] = None):
        self.embedder = embedder or QwenEmbedder()

    def embed_query(self, query: str) -> Optional[List[float]]:
        return self.embedder.embed(query)


class PatientSemanticSearch:
    def __init__(self, rag: Optional[RAGService] = None, db_conn=None):
        self.rag = rag or RAGService()
        self.db_conn = db_conn

    def _get_conn(self):
        if self.db_conn:
            return self.db_conn
        from db import get_db_conn
        return get_db_conn()

    def search(self, query: str, top_k: int = 5):
        vector = self.rag.embed_query(query)
        if not vector:
            return []

        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    patient_case_summary,
                    patient_case_embedding <#> %s AS similarity
                FROM patients
                WHERE patient_case_embedding IS NOT NULL
                ORDER BY similarity ASC
                LIMIT %s;
                """,
                (vector, top_k),
            )
            rows = cur.fetchall()

        return [
            {
                "id": r[0],
                "summary": r[1],
                "similarity": r[2],
            }
            for r in rows
        ]


_rag_instance = RAGService()
_search_instance = PatientSemanticSearch(_rag_instance)


def rag_tool(query: str) -> Optional[List[float]]:
    return _rag_instance.embed_query(query)


def semantic_search_patient_cases(query: str, k: int = 5):
    return _search_instance.search(query, top_k=k)


from __future__ import annotations

import os
from typing import Optional, List
import httpx
import openai


class VectorEncoder:
    def encode(self, text: str) -> Optional[List[float]]:
        raise NotImplementedError


class QwenVectorEncoder(VectorEncoder):
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = (endpoint or os.getenv("QWEN_EMBEDDING_URL", "http://localhost:9977")).rstrip("/")
        self.headers = {"Content-Type": "application/json"}

    def _send(self, url: str, text: str):
        with httpx.Client(timeout=60.0) as client:
            res = client.post(url, headers=self.headers, json={"inputs": [text]})
            res.raise_for_status()
            return res.json()

    def encode(self, text: str) -> Optional[List[float]]:
        try:
            try:
                data = self._send(self.endpoint, text)
            except httpx.HTTPStatusError:
                data = self._send(f"{self.endpoint}/embed", text)

            if isinstance(data, dict) and "embeddings" in data:
                return data["embeddings"][0]

            if isinstance(data, list):
                return data[0]

            if isinstance(data, dict) and "data" in data:
                item = data["data"][0]
                return item.get("embedding") if isinstance(item, dict) else item

        except Exception:
            return None

        return None


class OpenAIVectorEncoder(VectorEncoder):
    def __init__(self, model: str = "text-embedding-3-large"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model

    def encode(self, text: str) -> Optional[List[float]]:
        try:
            res = openai.embeddings.create(
                model=self.model,
                input=text
            )
            return res.data[0].embedding
        except Exception:
            return None


class RAGKernel:
    def __init__(self, provider: str = "qwen"):
        if provider == "openai":
            self.encoder = OpenAIVectorEncoder()
        else:
            self.encoder = QwenVectorEncoder()

    def embed(self, query: str) -> Optional[List[float]]:
        return self.encoder.encode(query)


class PatientVectorSearch:
    def __init__(self, rag: Optional[RAGKernel] = None, conn=None):
        self.rag = rag or RAGKernel()
        self.conn = conn

    def _conn(self):
        if self.conn:
            return self.conn
        from db import get_db_conn
        return get_db_conn()

    def run(self, query: str, k: int = 5):
        vec = self.rag.embed(query)
        if not vec:
            return []

        conn = self._conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    patient_case_summary,
                    patient_case_embedding <#> %s AS similarity
                FROM patients
                WHERE patient_case_embedding IS NOT NULL
                ORDER BY similarity ASC
                LIMIT %s;
                """,
                (vec, k)
            )
            rows = cur.fetchall()

        return [
            {"id": r[0], "summary": r[1], "similarity": r[2]}
            for r in rows
        ]


_rag_qwen = RAGKernel(provider="qwen")
_rag_openai = RAGKernel(provider="openai")

_search_qwen = PatientVectorSearch(_rag_qwen)
_search_openai = PatientVectorSearch(_rag_openai)


def rag_tool(query: str, provider: str = "qwen") -> Optional[List[float]]:
    return (_rag_openai if provider == "openai" else _rag_qwen).embed(query)


def semantic_search_patient_cases(query: str, k: int = 5, provider: str = "qwen"):
    engine = _search_openai if provider == "openai" else _search_qwen
    return engine.run(query, k)
