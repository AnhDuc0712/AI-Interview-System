import argparse
import asyncio
import logging

from app.services.skill_relationship_service import get_skill_relationship_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Rebuild the skill relationship graph from existing CV and job data.')
    parser.add_argument('--min-pair-count', type=int, default=1, help='Minimum co-occurrence count to include a relationship.')
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    service = get_skill_relationship_service()
    service.min_pair_count = args.min_pair_count
    await service.ensure_ready()

    summary = await service.rebuild_graph()
    logging.info('Graph rebuilt: %s', summary)
    print('Rebuild completed')
    print('CV documents processed:', summary['cv_documents'])
    print('Job documents processed:', summary['job_documents'])
    print('Relationships created:', summary['relationships_created'])


if __name__ == '__main__':
    asyncio.run(main())
