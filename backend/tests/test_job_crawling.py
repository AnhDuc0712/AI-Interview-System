import asyncio
from datetime import datetime

from app.models.crawled_job import CrawledJob
from app.services.job_crawling_service import JobCrawlingService
from app.ai.skills.extractor import SkillExtractionEngine
import pytest
from app.services.job_crawling_service import JobCrawlingService
from app.ai.skills.extractor import SkillExtractionEngine

class StubPlaywrightClient:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class StubCrawler:
    source_name = 'Stub'

    def __init__(self, urls, jobs):
        self.urls = urls
        self.jobs = jobs

    def collect_job_urls(self, limit: int = 20):
        return self.urls[:limit]

    def extract_job_details(self, url: str):
        return self.jobs[url]


class StubStorage:
    def __init__(self, existing_urls=None):
        self.existing_urls = set(existing_urls or [])
        self.saved_jobs = []

    async def ensure_ready(self):
        return None

    async def exists(self, url: str) -> bool:
        return url in self.existing_urls

    async def save_job_if_new(self, job: CrawledJob):
        if job.url in self.existing_urls:
            return {'url': job.url}
        self.existing_urls.add(job.url)
        self.saved_jobs.append(job)
        return job.model_dump()


@pytest.mark.asyncio
async def test_crawling_service_processes_skills_and_creates_records() -> None:
    raw_description = 'Experience with ReactJS, Next.js, TailwindCSS.'
    job = CrawledJob(
        title='Frontend Engineer',
        company='Example Co',
        location='Hanoi',
        experience_level='',
        description=raw_description,
        requirements='',
        skills_raw='',
        source='Stub',
        url='https://example.com/job1',
        raw_description='',
    )

    service = JobCrawlingService(
        repository=StubStorage(),
        playwright_client=StubPlaywrightClient(),
        skill_engine=SkillExtractionEngine(),
        crawlers=[StubCrawler(['https://example.com/job1'], {'https://example.com/job1': job})],
    )

    summary = await service.crawl()  # bỏ asyncio.run, dùng await

    assert summary['saved_jobs'] == 1
    assert summary['duplicate_jobs'] == 0
    assert summary['failed_jobs'] == 0
    saved_job = service.repository.saved_jobs[0]
    assert saved_job.skills == ['React', 'Next.js', 'Tailwind CSS']
    assert 'frontend' in saved_job.categorized_skills


@pytest.mark.asyncio
async def test_crawling_service_skips_duplicate_urls() -> None:
    raw_description = 'Experience with Python, Django.'
    job = CrawledJob(
        title='Backend Engineer',
        company='Example Co',
        location='Hanoi',
        experience_level='',
        description=raw_description,
        requirements='',
        skills_raw='',
        source='Stub',
        url='https://example.com/job1',
        raw_description='',
    )

    storage = StubStorage(existing_urls=['https://example.com/job1'])
    service = JobCrawlingService(
        repository=storage,
        playwright_client=StubPlaywrightClient(),
        skill_engine=SkillExtractionEngine(),
        crawlers=[StubCrawler(['https://example.com/job1'], {'https://example.com/job1': job})],
    )

    summary = await service.crawl()

    assert summary['saved_jobs'] == 0
    assert summary['duplicate_jobs'] == 1
    assert summary['failed_jobs'] == 0


@pytest.mark.asyncio
async def test_job_parser_handles_empty_page_safe() -> None:
    job = CrawledJob(
        title='Something',
        company='Corp',
        location='',
        experience_level='',
        description='',
        requirements='',
        skills_raw='',
        source='Stub',
        url='https://example.com/job-empty',
        raw_description='',
    )

    service = JobCrawlingService(
        repository=StubStorage(),
        playwright_client=StubPlaywrightClient(),
        skill_engine=SkillExtractionEngine(),
        crawlers=[StubCrawler(['https://example.com/job-empty'], {'https://example.com/job-empty': job})],
    )

    summary = await service.crawl()

    assert summary['saved_jobs'] == 1
    assert summary['failed_jobs'] == 0
    assert service.repository.saved_jobs[0].skills == []