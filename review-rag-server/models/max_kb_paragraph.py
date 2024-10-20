import datetime
from pydantic import BaseModel

class MaxKbParagraph(BaseModel):
    id: int
    content: str
    title: str
    status: str
    hit_num: int
    is_active: bool
    dataset_id: int
    document_id: int
    creator: str
    create_time: datetime.datetime
    updater: str
    update_time: datetime.datetime
    deleted: int
    tenant_id: int
