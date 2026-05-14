import asyncio
from collections import Counter

from app.ai.relationships.cooccurrence import SkillCooccurrenceCounter
from app.ai.relationships.scoring import RelationshipScorer
from app.ai.relationships.graph_builder import RelationshipGraphBuilder
from app.ai.relationships.utils import extract_unknown_tokens
from app.services.skill_relationship_service import SkillRelationshipService


class StubCollection:
    def __init__(self):
        self.documents = []
        self.indexes = []

    async def create_index(self, *args, **kwargs):
        self.indexes.append((args, kwargs))

    async def find_one(self, filter_, projection=None):
        for doc in self.documents:
            if all(doc.get(key) == value for key, value in filter_.items()):
                return doc
        return None

    async def find_one_and_update(self, filter_, update, return_document=None):
        doc = await self.find_one(filter_)
        if doc is None:
            return None
        if '$inc' in update:
            for key, value in update['$inc'].items():
                doc[key] = doc.get(key, 0) + value
        if '$set' in update:
            doc.update(update['$set'])
        return doc

    async def update_one(self, filter_, update, upsert=False):
        doc = await self.find_one(filter_)
        if doc is None and upsert:
            base = {k: v for k, v in filter_.items()}
            self.documents.append(base)
            doc = base
        if doc is None:
            return None
        if '$inc' in update:
            for key, value in update['$inc'].items():
                doc[key] = doc.get(key, 0) + value
        if '$set' in update:
            doc.update(update['$set'])
        if '$setOnInsert' in update and upsert:
            for key, value in update['$setOnInsert'].items():
                if key not in doc:
                    doc[key] = value
        if '$push' in update:
            for key, value in update['$push'].items():
                doc.setdefault(key, []).append(value)
        if '$addToSet' in update:
            for key, value in update['$addToSet'].items():
                if key not in doc:
                    doc[key] = []
                for item in value.get('$each', []):
                    if item not in doc[key]:
                        doc[key].append(item)
        return doc

    async def delete_many(self, filter_):
        self.documents = []

    async def insert_many(self, docs):
        self.documents.extend(docs)

    async def find(self, filter_):
        for doc in self.documents:
            yield doc


class StubCVCollection(StubCollection):
    def __init__(self, documents):
        super().__init__()
        self.documents = documents


class StubJobCollection(StubCollection):
    def __init__(self, documents):
        super().__init__()
        self.documents = documents


def test_cooccurrence_counter_avoids_duplicate_pairs() -> None:
    skill_lists = [
        ['React', 'Next.js', 'Tailwind CSS', 'React'],
        ['React', 'Next.js'],
    ]
    pair_counts, skill_counts = SkillCooccurrenceCounter.count_pairs(skill_lists)

    assert pair_counts[tuple(sorted(('React', 'Next.js')))] == 2
    assert pair_counts[('React', 'Tailwind CSS')] == 1
    assert skill_counts['React'] == 2


def test_relationship_scorer_normalizes_weights() -> None:
    pair_counts = Counter({('React', 'Next.js'): 4, ('React', 'Tailwind CSS'): 2})
    skill_counts = Counter({'React': 3, 'Next.js': 4, 'Tailwind CSS': 2})
    scores = RelationshipScorer.score_relationships(pair_counts, skill_counts, min_pair_count=1)

    assert scores['React']['Next.js'] == round(4 / 3, 4)
    assert scores['Next.js']['React'] == round(4 / 4, 4)
    assert scores['React']['Tailwind CSS'] == round(2 / 3, 4)


def test_extract_unknown_tokens_tracks_unmapped_phrases() -> None:
    raw_text = 'Experience with ASP.NET Core, SignalR, Team collaboration, AWS.'
    known_skills = ['ASP.NET Core', 'AWS']

    unknown_tokens = extract_unknown_tokens(raw_text, known_skills)

    assert 'SignalR' in unknown_tokens
    assert 'Team collaboration' not in unknown_tokens


def test_rebuild_graph_constructs_relationship_documents() -> None:
    cv_data = [
        {'normalized_content': {'skills': ['React', 'Next.js']}, 'normalized_text': 'React, Next.js'},
    ]
    job_data = [
        {'skills': ['React', 'Tailwind CSS'], 'raw_description': 'React, Tailwind CSS'},
    ]

    service = SkillRelationshipService(
        relationship_collection=StubCollection(),
        observation_collection=StubCollection(),
        cv_collection=StubCVCollection(cv_data),
        job_collection=StubJobCollection(job_data),
    )

    summary = asyncio.run(service.rebuild_graph())
    assert summary['documents_processed'] == 2
    assert summary['relationships_created'] >= 2


def test_observation_service_records_unknown_tokens() -> None:
    observation_collection = StubCollection()
    service = SkillRelationshipService(
        relationship_collection=StubCollection(),
        observation_collection=observation_collection,
        cv_collection=StubCVCollection([]),
        job_collection=StubJobCollection([]),
    )

    asyncio.run(service._record_unknown_tokens('React, SignalR, Express.js', ['React'], 'job'))
    record = asyncio.run(observation_collection.find_one({'token': 'SignalR', 'source': 'job'}))

    assert record is not None
    assert record['frequency'] == 1
    assert 'React' in record['context_skills']
