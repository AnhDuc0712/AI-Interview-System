from app.services.cv_ingestion import CVIngestionService, get_cv_ingestion_service
from app.services.cv_query import CVQueryService, get_cv_query_service


def get_cv_ingestion_dependency() -> CVIngestionService:
    return get_cv_ingestion_service()


def get_cv_query_dependency() -> CVQueryService:
    return get_cv_query_service()
