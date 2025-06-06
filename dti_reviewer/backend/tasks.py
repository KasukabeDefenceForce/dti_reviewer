from celery_app import celery
from similarity_engine import SimilarityEngine

engine = SimilarityEngine()
engine.load_index_or_build()

@celery.task(bind=True)
def query_experts_task(self, query_text: str, top_n: int = 25):
    try:
        df = engine.query_experts(query_text, top_n=top_n)
        return df.to_dict(orient="records")
    except Exception as e:
        raise self.retry(exc=e, countdown=10, max_retries=2)