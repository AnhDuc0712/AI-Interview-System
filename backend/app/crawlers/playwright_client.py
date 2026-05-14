from __future__ import annotations

import logging
import time
from typing import Any

from playwright.sync_api import Browser, Page, Playwright, TimeoutError as PlaywrightTimeoutError, sync_playwright

from app.core.config import settings

logger = logging.getLogger(__name__)


class PlaywrightClient:
    def __init__(
        self,
        headless: bool | None = None,
        timeout_ms: int | None = None,
        user_agent: str | None = None,
        browser_type: str = 'chromium',
        max_retries: int | None = None,
    ) -> None:
        self.headless = settings.playwright_headless if headless is None else headless
        self.timeout_ms = settings.playwright_timeout_ms if timeout_ms is None else timeout_ms
        self.user_agent = settings.playwright_user_agent if user_agent is None else user_agent
        self.browser_type = browser_type
        self.max_retries = settings.crawler_max_retries if max_retries is None else max_retries
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    def __enter__(self) -> PlaywrightClient:
        self.playwright = sync_playwright().start()
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = browser_launcher.launch(headless=self.headless)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def close(self) -> None:
        if self.browser is not None:
            try:
                self.browser.close()
            except Exception as exc:
                logger.warning('Failed to close browser: %s', exc)
            finally:
                self.browser = None

        if self.playwright is not None:
            try:
                self.playwright.stop()
            except Exception as exc:
                logger.warning('Failed to stop Playwright: %s', exc)
            finally:
                self.playwright = None

    def new_page(self) -> Page:
        if self.browser is None:
            raise RuntimeError('Browser is not initialized')

        page = self.browser.new_page(user_agent=self.user_agent or None, timeout=self.timeout_ms)
        page.set_viewport_size({'width': 1280, 'height': 900})
        return page

    def safe_goto(
        self,
        page: Page,
        url: str,
        wait_until: str = 'domcontentloaded',
        timeout: int | None = None,
        retries: int | None = None,
    ) -> None:
        timeout = timeout if timeout is not None else self.timeout_ms
        retries = retries if retries is not None else self.max_retries

        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                page.goto(url, wait_until=wait_until, timeout=timeout)
                return
            except PlaywrightTimeoutError as exc:
                last_error = exc
                logger.warning('Timeout loading %s on attempt %s/%s', url, attempt, retries)
            except Exception as exc:
                last_error = exc
                logger.warning('Error loading %s on attempt %s/%s: %s', url, attempt, retries, exc)
            if attempt < retries:
                time.sleep(1)

        error_message = f'Unable to navigate to {url} after {retries} attempts'
        logger.error(error_message)
        raise RuntimeError(error_message) from last_error
