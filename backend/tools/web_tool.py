from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import httpx


LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class DuckDuckGoConfig:
    endpoint: str = "https://api.duckduckgo.com/"
    timeout_seconds: float = 10.0
    max_related_topics: int = 3
    date_formats: tuple[str, ...] = ("%Y_%m_%d", "%Y-%m-%d")


class DateWindow:
    def __init__(self, cfg: DuckDuckGoConfig):
        self.cfg = cfg

    def _parse(self, raw: str) -> str:
        for fmt in self.cfg.date_formats:
            try:
                dt = datetime.strptime(raw, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError(f"Invalid date format '{raw}'")

    def build_df(self, start: Optional[str], end: Optional[str]) -> Optional[str]:
        if not start and not end:
            return None

        today = date.today().strftime("%Y-%m-%d")
        start_norm = self._parse(start) if start else None
        end_norm = self._parse(end) if end else None

        if start_norm and end_norm:
            if start_norm > end_norm:
                raise ValueError("from_date must be <= to_date")
            return f"{start_norm}..{end_norm}"

        if start_norm and not end_norm:
            return f"{start_norm}..{today}"

        if end_norm and not start_norm:
            end_dt = datetime.strptime(end_norm, "%Y-%m-%d").date()
            try:
                start_guess = end_dt.replace(year=end_dt.year - 1)
            except ValueError:
                start_guess = end_dt.replace(year=end_dt.year - 1, day=28)
            start_norm = start_guess.strftime("%Y-%m-%d")
            if start_norm > end_norm:
                start_norm, end_norm = end_norm, start_norm
            return f"{start_norm}..{end_norm}"

        return None


class DuckDuckGoClient:
    def __init__(self, cfg: DuckDuckGoConfig, http: Optional[httpx.Client] = None):
        self.cfg = cfg
        self.http = http or httpx.Client(timeout=self.cfg.timeout_seconds)

    def fetch(self, query: str, df: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
        }
        if df:
            params["df"] = df
        resp = self.http.get(self.cfg.endpoint, params=params)
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        try:
            self.http.close()
        except Exception:
            pass


class DuckDuckGoFormatter:
    def __init__(self, cfg: DuckDuckGoConfig):
        self.cfg = cfg

    def format(self, query: str, payload: Dict[str, Any]) -> str:
        lines: List[str] = []

        if payload.get("Answer"):
            lines.append(f"Answer: {payload['Answer']}")

        if payload.get("AbstractText"):
            lines.append(f"Summary: {payload['AbstractText']}")
            if payload.get("AbstractURL"):
                lines.append(f"Source: {payload['AbstractURL']}")

        topics = payload.get("RelatedTopics") or []
        count = 0
        for topic in topics:
            if count >= self.cfg.max_related_topics:
                break
            if isinstance(topic, dict) and topic.get("Text"):
                count += 1
                lines.append(f"{count}. {topic['Text']}")
                if topic.get("FirstURL"):
                    lines.append(f"   URL: {topic['FirstURL']}")

        if not lines:
            return f"No web search results found for: {query}"

        return f"Web search results for '{query}':\n" + "\n".join(lines)


class WebSearchService:
    def __init__(
        self,
        cfg: Optional[DuckDuckGoConfig] = None,
        client: Optional[DuckDuckGoClient] = None,
        formatter: Optional[DuckDuckGoFormatter] = None,
        window: Optional[DateWindow] = None,
    ):
        self.cfg = cfg or DuckDuckGoConfig()
        self.window = window or DateWindow(self.cfg)
        self.client = client or DuckDuckGoClient(self.cfg)
        self.formatter = formatter or DuckDuckGoFormatter(self.cfg)

    def search(
        self,
        query: str,
        num_results: int = 10,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> str:
        try:
            df = self.window.build_df(from_date, to_date)
            payload = self.client.fetch(query, df=df)
            return self.formatter.format(query, payload)
        except Exception as e:
            return f"[Web Search Error] {str(e)}"

    def close(self) -> None:
        self.client.close()


_default_search = WebSearchService()


def web_search_tool(
    query: str,
    num_results: int = 10,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> str:
    return _default_search.search(
        query=query,
        num_results=num_results,
        from_date=from_date,
        to_date=to_date,
    )
