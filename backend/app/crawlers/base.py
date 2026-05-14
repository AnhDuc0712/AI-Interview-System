from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Iterable

from playwright.sync_api import ElementHandle, Page

from app.crawlers.playwright_client import PlaywrightClient
from app.models.crawled_job import CrawledJob

logger = logging.getLogger(__name__)


class JobCrawlerBase(ABC):
    source_name: str
    base_url: str

    def __init__(self, client: PlaywrightClient) -> None:
        self.client = client

    @abstractmethod
    def collect_job_urls(self, limit: int = 20) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def extract_job_details(self, url: str) -> CrawledJob:
        raise NotImplementedError

    def _normalize_url(self, href: str) -> str:
        if href.startswith('http'):
            return href
        return f'{self.base_url.rstrip("/")}/{href.lstrip("/")}'

    def _safe_text_for_selectors(self, page: Page, selectors: Iterable[str]) -> str:
        for selector in selectors:
            element = page.query_selector(selector)
            if element:
                try:
                    text = element.inner_text().strip()
                except Exception:
                    continue
                if text:
                    return text
        return ''

    def _safe_attribute_for_selectors(
        self,
        page: Page,
        selectors: Iterable[str],
        attribute: str = 'href'
    ) -> str:
        for selector in selectors:
            element = page.query_selector(selector)
            if element:
                try:
                    value = element.get_attribute(attribute)
                except Exception:
                    continue
                if value:
                    return value.strip()
        return ''

    def _collect_links(self, page: Page, allowed_patterns: Iterable[str], limit: int) -> list[str]:
        anchors = page.query_selector_all('a')
        found: list[str] = []
        for anchor in anchors:
            try:
                href = anchor.get_attribute('href')
            except Exception:
                continue
            if not href:
                continue
            normalized = href.strip()
            if any(pattern in normalized for pattern in allowed_patterns):
                if normalized not in found:
                    found.append(normalized)
            if len(found) >= limit:
                break
        return found
