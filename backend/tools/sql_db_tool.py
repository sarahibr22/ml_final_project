from __future__ import annotations

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncGenerator, Callable

from dotenv import load_dotenv

from llm.open_router_llm import make_openrouter_call
from utils.connection_manager import async_connect, async_disconnect
from utils.schema_inspector import get_full_database_schema


# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logger = logging.getLogger(__name__)


class SchemaFormatter:
    """Turns schema inspector output into text context for LLM prompts."""

    def to_text(self, schema_items: List[Dict[str, Any]]) -> str:
        blocks: List[str] = []

        for item in schema_items:
            t = item["table"]
            table_name = f"{t['schema']}.{t['name']}"

            col_lines: List[str] = []
            for col in t["columns"]:
                line = f"  {col['name']} {col['type']}"
                if not col.get("nullable", True):
                    line += " NOT NULL"
                if col.get("is_primary_key"):
                    line += " PRIMARY KEY"
                if "foreign_key" in col:
                    line += f" REFERENCES {col['foreign_key']['references']}"
                col_lines.append(line)

            ddl = f"CREATE TABLE {table_name} (\n" + ",\n".join(col_lines) + "\n);"

            if t.get("description"):
                ddl = f"-- {t['description']}\n{ddl}"

            ddl += f"\n-- Row count: {t.get('row_count')}"

            # Index hints (non-primary)
            idx_lines: List[str] = []
            for idx in (t.get("indexes") or []):
                if not idx.get("is_primary"):
                    idx_lines.append(f"-- Index: {idx['name']} on {', '.join(idx['columns'])}")
            if idx_lines:
                ddl += "\n" + "\n".join(idx_lines)

            blocks.append(ddl)

        return "\n\n".join(blocks)

    def table_names(self, schema_items: List[Dict[str, Any]]) -> List[str]:
        return [item["table"]["name"] for item in schema_items]


class SchemaReducer:
    """Filters schema inspector output to only specific tables."""

    def filter_by_tables(self, schema_items: List[Dict[str, Any]], tables: List[str]) -> List[Dict[str, Any]]:
        if not tables:
            return schema_items
        wanted = {t.lower() for t in tables}
        return [item for item in schema_items if item["table"]["name"].lower() in wanted]


class PromptFactory:
    """Builds the two prompts used in the pipeline."""

    def __init__(self, formatter: SchemaFormatter):
        self.formatter = formatter

    def table_selection_prompt(self, user_query: str, schema_items: List[Dict[str, Any]]) -> str:
        available = self.formatter.table_names(schema_items)
        schema_text = self.formatter.to_text(schema_items)

        return f"""The current date is {datetime.now().strftime('%Y-%m-%d')}.
You are an intelligent database analyst. Determine which tables are required to answer the user query.

Instructions:
1) Select only from the available tables list.
2) Return ONLY JSON in this form: {{"tables": ["table1", "table2"]}}
3) Do not output explanations, markdown, or extra text.

Database Schema:
{schema_text}

Available Tables: {", ".join(available) if available else "No tables found"}

User Query: {user_query}
"""

    def sql_generation_prompt(
        self,
        user_query: str,
        schema_text: str,
        previous_sql: Optional[str] = None,
        previous_error: Optional[str] = None,
        explain_json: Optional[str] = None,
    ) -> str:
        prompt = f"""You are an expert PostgreSQL database query assistant.

Task:
- Convert the natural language query into an optimized PostgreSQL query
- Use JOINs, filters, and aggregations correctly
- Prefer explicit columns (avoid SELECT *)
- Add LIMIT where large results may occur
- End with a semicolon
- If case-insensitive matching is appropriate, use ILIKE or LOWER()

Database Schema Context:
```json
{schema_text}"""