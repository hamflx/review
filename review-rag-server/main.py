from datetime import datetime
from json import dumps
import os
import hashlib

from mayim import Mayim
from sanic import Sanic, Request, json
from mayim.sql.postgres.executor import PostgresExecutor
from mayim.sql.postgres.interface import PostgresPool
from models.max_kb_file import MaxKbFile
from snowflake import SnowflakeGenerator
from marker.convert import convert_single_pdf
from marker.models import load_all_models

gen = SnowflakeGenerator(100)

class ReviewRagPostgresExecutor(PostgresExecutor):
    async def select_all_files(
        self, limit: int = 20, offset: int = 0
    ) -> list[MaxKbFile]:
        ...
    async def insert_file(
        self,
        id,
        md5,
        filename,
        file_size,
        user_id,
        platform,
        region_name,
        bucket_name,
        file_id,
        target_name,
        tags,
        creator,
        create_time,
        updater,
        update_time,
        deleted,
        tenant_id
    ) -> None:
        ...
    async def delete_file_item(self, id) -> None:
        ...
    async def initialize_database(self) -> None:
        ...

app = Sanic("ReviewRagServer")

DATABASE_USER = os.getenv("DATABASE_USER") or 'postgres'
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD") or 'she4waeJ_uquahg7goh4aewu'
DATABASE_HOST = os.getenv("DATABASE_HOST") or '127.0.0.1'
DATABASE_PORT = os.getenv("DATABASE_PORT") or '5666'

@app.before_server_start
async def setup_mayim(app: Sanic):
    executor = ReviewRagPostgresExecutor()
    app.ctx.pool = PostgresPool(dsn="postgres://%s:%s@%s:%s" % (DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT))
    await app.ctx.pool.open()
    Mayim(executors=[executor], pool=app.ctx.pool)
    app.ext.dependency(executor)
    await executor.initialize_database()

@app.after_server_stop
async def shutdown_mayim(app: Sanic):
    await app.ctx.pool.close()

@app.get("/api/files")
async def fetch_all_files(request: Request, executor: ReviewRagPostgresExecutor):
    files = await executor.select_all_files()
    list = []
    for f in files:
        file_dict = f.__dict__.copy()
        file_dict['id'] = str(file_dict['id'])
        list.append(file_dict)
    return json(list, default=str)

@app.delete("/api/files")
async def delete_files(request: Request, executor: ReviewRagPostgresExecutor):
    ids = tuple(request.json)
    for id in ids:
        await executor.delete_file_item(int(id))
    return json({"success": True})

@app.post("/api/files/create")
async def create_new_file_handler(request: Request, executor: ReviewRagPostgresExecutor):
    file = request.files.get('file')
    if not file:
        json({"error": "没有文件"})
    file = request.files['file'][0]
    hash = hashlib.md5()
    hash.update(file.body)
    md5 = hash.hexdigest()

    kb_file = MaxKbFile(
        id = next(gen),
        md5 = md5,
        filename = file.name,
        file_size = len(file.body),
        user_id = '',
        platform = '',
        region_name = '',
        bucket_name = '',
        file_id = '',
        target_name = '',
        tags = {},
        creator = '',
        create_time = datetime.now(),
        updater = '',
        update_time = datetime.now(),
        deleted = 0,
        tenant_id = 0
    )
    await executor.insert_file(
        kb_file.id,
        kb_file.md5,
        kb_file.filename,
        kb_file.file_size,
        kb_file.user_id,
        kb_file.platform,
        kb_file.region_name,
        kb_file.bucket_name,
        kb_file.file_id,
        kb_file.target_name,
        dumps(kb_file.tags),
        kb_file.creator,
        kb_file.create_time,
        kb_file.updater,
        kb_file.update_time,
        kb_file.deleted,
        kb_file.tenant_id
    )
    with open('test.pdf', 'wb+') as f:
        f.write(file.body)
    model_lst = load_all_models()
    full_text, images, out_meta = convert_single_pdf('test.pdf', model_lst)
    print(full_text)
    return json({"success": True})

if __name__ == "__main__":
    app.run(single_process=True)
