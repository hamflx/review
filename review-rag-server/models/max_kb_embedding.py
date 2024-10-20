from pydantic import BaseModel
from datetime import datetime

class MaxKbEmbedding(BaseModel):
    id: int
    source_id: int
    source_type: str
    is_active: bool
    embedding: list[float]
    meta: dict
    dataset_id: int
    document_id: int
    paragraph_id: int
    search_vector: str
    creator: str
    create_time: datetime
    updater: str
    update_time: datetime
    deleted: int
    tenant_id: int