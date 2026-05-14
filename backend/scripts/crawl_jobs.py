import argparse
import asyncio
import logging

from app.services.job_crawling_service import get_job_crawling_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Crawl job descriptions and store normalized job intelligence.')
    parser.add_argument('--sources', nargs='*', help='Optional list of sources to crawl (ITviec, TopCV, VietnamWorks).')
    parser.add_argument('--limit', type=int, default=20, help='Maximum job links to collect per source.')
    parser.add_argument('--rate-limit', type=float, default=1.0, help='Seconds to wait between job page requests.')
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    service = get_job_crawling_service()
    await service.ensure_ready()

    summary = await service.crawl(
        sources=args.sources,
        limit_per_source=args.limit,
        rate_limit_seconds=args.rate_limit,
    )

    print('Crawl completed')
    print('sources:', summary['sources'])
    print('attempted_jobs:', summary['attempted_jobs'])
    print('saved_jobs:', summary['saved_jobs'])
    print('duplicate_jobs:', summary['duplicate_jobs'])
    print('failed_jobs:', summary['failed_jobs'])
    if summary['errors']:
        print('errors:')
        for error in summary['errors']:
            print('-', error)


if __name__ == '__main__':
    asyncio.run(main())
