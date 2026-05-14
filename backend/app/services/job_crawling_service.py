from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from app.ai.skills.extractor import SkillExtractionEngine
from app.crawlers import JobStorage, PlaywrightClient
from app.crawlers.sources.itviec import ITviecCrawler
from app.crawlers.sources.topcv import TopCVCrawler
from app.crawlers.sources.vietnamworks import VietnamWorksCrawler
from app.models.crawled_job import CrawledJob
from app.crawlers.parser import merge_description_and_requirements

logger = logging.getLogger(__name__)


class JobCrawlingService:
    def __init__(
        self,
        repository: JobStorage | None = None,
        playwright_client: PlaywrightClient | None = None,
        skill_engine: SkillExtractionEngine | None = None,
        crawlers: list[Any] | None = None,
    ) -> None:
        self.repository = repository or JobStorage()
        self.playwright_client = playwright_client or PlaywrightClient()
        self.skill_engine = skill_engine or SkillExtractionEngine()
        self.crawlers = crawlers or [
            ITviecCrawler(self.playwright_client),
            TopCVCrawler(self.playwright_client),
            VietnamWorksCrawler(self.playwright_client),
        ]

    async def ensure_ready(self) -> None:
        await self.repository.ensure_ready()

    async def crawl(
        self,
        sources: list[str] | None = None,
        limit_per_source: int = 20,
        rate_limit_seconds: float = 1.0,
    ) -> dict[str, int | list[str]]:
        summary = {
            'sources': 0,
            'attempted_jobs': 0,
            'saved_jobs': 0,
            'duplicate_jobs': 0,
            'failed_jobs': 0,
            'errors': []
        }

        allowed_sources = {name.lower() for name in sources} if sources else None

        with self.playwright_client as client:
            for crawler in self.crawlers:
                if allowed_sources and crawler.source_name.lower() not in allowed_sources:
                    continue
                summary['sources'] += 1

                try:
                    urls = await asyncio.to_thread(crawler.collect_job_urls, limit_per_source)
                except Exception as exc:
                    logger.exception('Failed to collect URLs from %s', crawler.source_name)
                    summary['failed_jobs'] += 1
                    summary['errors'].append(f'{crawler.source_name}: collect failed')
                    continue

                for url in urls:
                    summary['attempted_jobs'] += 1
                    try:
                        if await self.repository.exists(url):
                            summary['duplicate_jobs'] += 1
                            continue

                        job = await asyncio.to_thread(crawler.extract_job_details, url)
                        cleaned_description = merge_description_and_requirements(job.description, job.requirements or '')
                        job.raw_description = cleaned_description
                        job.skills_raw = cleaned_description
                        extraction = self.skill_engine.extract(cleaned_description, section_lines=[cleaned_description])
                        job.skills = extraction.skills
                        job.categorized_skills = extraction.categorized_skills

                        await self.repository.save_job_if_new(job)
                        summary['saved_jobs'] += 1
                    except Exception as exc:
                        logger.exception('Failed to process job from %s (%s)', crawler.source_name, url)
                        summary['failed_jobs'] += 1
                        summary['errors'].append(f'{crawler.source_name}: {url}')

                    if rate_limit_seconds > 0:
                        time.sleep(rate_limit_seconds)

        return summary


def get_job_crawling_service() -> JobCrawlingService:
    return JobCrawlingService()
