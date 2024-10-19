import os

from mayim import Mayim
from sanic import Sanic, Request, json
from mayim.sql.postgres.executor import PostgresExecutor
from mayim.sql.postgres.interface import PostgresPool
from models.max_kb_file import MaxKbFile

class ReviewRagPostgresExecutor(PostgresExecutor):
    async def select_all_files(
        self, limit: int = 4, offset: int = 0
    ) -> list[MaxKbFile]:
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

@app.get("/")
async def handler(request: Request, executor: ReviewRagPostgresExecutor):
    files = await executor.select_all_files()
    print(files)
    return json({"countries": [country.dict() for country in files]})

if __name__ == "__main__":
    app.run(single_process=True)
