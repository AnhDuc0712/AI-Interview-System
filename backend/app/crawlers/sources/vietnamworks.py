from __future__ import annotations

from urllib.parse import urljoin

from app.crawlers.base import JobCrawlerBase
from app.crawlers.parser import clean_text, merge_description_and_requirements, parse_experience_level
from app.models.crawled_job import CrawledJob


class VietnamWorksCrawler(JobCrawlerBase):
    source_name = 'VietnamWorks'
    base_url = 'https://www.vietnamworks.com'
    listing_url = 'https://www.vietnamworks.com/viec-lam/cntt-software'

    def collect_job_urls(self, limit: int = 20) -> list[str]:
        page = self.client.new_page()
        try:
            self.client.safe_goto(page, self.listing_url)
            raw_links = self._collect_links(page, ['/viec-lam/', '/job/'], limit)
            return [urljoin(self.base_url, href) for href in raw_links]
        finally:
            page.close()

    def extract_job_details(self, url: str) -> CrawledJob:
        page = self.client.new_page()
        try:
            self.client.safe_goto(page, url)
            title = self._safe_text_for_selectors(page, ['h1', '.job-title', '.job-detail__title'])
            company = self._safe_text_for_selectors(page, ['.company-name', '.job-detail__company', '.company-name__link'])
            location = self._safe_text_for_selectors(page, ['.location', '.job-location', '.job-detail__location'])
            description = self._safe_text_for_selectors(page, ['.job-description', '.job-detail__description', '.job-description-content'])
            requirements = self._safe_text_for_selectors(page, ['.requirements', '.job-requirement', '.job-requirements'])
            skills_raw = merge_description_and_requirements(description, requirements)
            experience_level = parse_experience_level(skills_raw)

            return CrawledJob(
                title=clean_text(title),
                company=clean_text(company),
                location=clean_text(location),
                experience_level=experience_level,
                description=description,
                requirements=requirements,
                skills_raw=skills_raw,
                source=self.source_name,
                url=url,
                raw_description=skills_raw,
            )
        finally:
            page.close()
