import datetime
from pydantic import BaseModel

class MaxKbDocument(BaseModel):
    id: int
    name: str
    char_length: int
    status: str
    is_active: bool
    type: str
    meta: dict
    dataset_id: int
    hit_handling_method: str
    directly_return_similarity: float
    files: dict
    creator: str
    create_time: datetime.datetime
    updater: str
    update_time: datetime.datetime
    deleted: int
    tenant_id: int
