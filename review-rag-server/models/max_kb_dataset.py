import datetime
from pydantic import BaseModel

class MaxKbDataset(BaseModel):
    id: int
    name: str
    description: str
    type: str
    meta: dict
    user_id: str
    remark: str
    creator: str
    create_time: datetime.datetime
    updater: str
    update_time: datetime.datetime
    deleted: int
    tenant_id: int
    completed: int
    total: int
