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
    tags: str
    creator: str
    create_time: str
    updater: str
    update_time: str
    deleted: bool
    tenant_id: int
