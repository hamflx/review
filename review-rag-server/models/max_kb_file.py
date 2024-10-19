import datetime
from pydantic import BaseModel

class MaxKbFile(BaseModel):
    id: int
    md5: str
    filename: str
    file_size: int
    user_id: str
    platform: str
    region_name: str
    bucket_name: str
    file_id: str
    target_name: str
    tags: dict
    creator: str
    create_time: datetime.datetime
    updater: str
    update_time: datetime.datetime
    deleted: int
    tenant_id: int
