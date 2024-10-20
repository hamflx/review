import os
import hashlib
import asyncio

from datetime import datetime
from json import dumps
from typing import List, Optional
from threading import Thread
from os.path import splitext

from mayim import Mayim
from sanic import Sanic, Request, json
from mayim.sql.postgres.executor import PostgresExecutor
from mayim.sql.postgres.interface import PostgresPool
from models.max_kb_dataset import MaxKbDataset
from models.max_kb_document import MaxKbDocument
from models.max_kb_embedding import MaxKbEmbedding
from models.max_kb_file import MaxKbFile
from models.max_kb_paragraph import MaxKbParagraph
from snowflake import SnowflakeGenerator
from sentence_splitter import SentenceSplitter, split_text_into_sentences
from oss2 import ProviderAuthV4, Bucket
from oss2.credentials import EnvironmentVariableCredentialsProvider
from llama_index.readers.pdf_marker import PDFMarkerReader
from utils.markdown import extract_elements, group_elements_by_title
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.indices.utils import embed_nodes
from llama_index.core.schema import TextNode

id_gen = SnowflakeGenerator(100)

class ReviewRagPostgresExecutor(PostgresExecutor):
    async def select_all_files(
        self, limit: int = 20, offset: int = 0
    ) -> list[MaxKbFile]:
        ...
    async def insert_dataset(self, id, name, description, type, meta, user_id, remark, creator, create_time, updater, update_time, deleted, tenant_id) -> None:
        ...
    async def insert_file(self, id, md5, filename, file_size, user_id, platform, region_name, bucket_name, file_id, target_name, tags, creator, create_time, updater, update_time, deleted, tenant_id) -> None:
        ...
    async def insert_document(self, id, name, char_length, status, is_active, type, meta, dataset_id, hit_handling_method, directly_return_similarity, files, creator, create_time, updater, update_time, deleted, tenant_id) -> None:
        ...
    async def insert_paragraph(self, id, content, title, status, hit_num, is_active, dataset_id, document_id, creator, create_time, updater, update_time, deleted, tenant_id) -> None:
        ...
    async def insert_embedding(self, id, source_id, source_type, is_active, embedding, meta, dataset_id, document_id, paragraph_id, search_vector, creator, create_time, updater, update_time, deleted, tenant_id) -> None:
        ...
    async def update_dataset_info(self, name, description, updater, update_time, id) -> None:
        ...
    async def update_document_content(self, status, char_length, files, meta, id) -> None:
        ...
    async def update_paragraph_status(self, status, id) -> None:
        ...
    async def update_dataset_mark_deleted(self, deleted, id) -> None:
        ...
    async def delete_file_item(self, id) -> None:
        ...
    async def select_all_dataset(self, limit: int = 20, offset: int = 0) -> List[MaxKbDataset]:
        ...
    async def select_dataset_by_id(self, id) -> Optional[MaxKbDataset]:
        ...
    async def select_file_by_md5(self, md5, file_size) -> Optional[MaxKbFile]:
        ...
    async def initialize_database(self) -> None:
        ...

app = Sanic("ReviewRagServer")
oss_auth = ProviderAuthV4(EnvironmentVariableCredentialsProvider())
endpoint = 'https://oss-cn-nanjing.aliyuncs.com'
region = 'cn-nanjing'
bucket = Bucket(oss_auth, endpoint=endpoint, bucket_name='review-rag', region=region)

DATABASE_USER = os.getenv("DATABASE_USER") or 'postgres'
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD") or 'she4waeJ_uquahg7goh4aewu'
DATABASE_HOST = os.getenv("DATABASE_HOST") or '127.0.0.1'
DATABASE_PORT = os.getenv("DATABASE_PORT") or '5666'

EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME') or 'BAAI/bge-base-zh-v1.5'

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

@app.get("/api/dataset")
async def fetch_all_dataset_handler(request: Request, executor: ReviewRagPostgresExecutor):
    kb_datasets = await executor.select_all_dataset()
    dict_list = []
    for item in kb_datasets:
        copy = item.__dict__.copy()
        copy['id'] = str(item.id)
        dict_list.append(copy)
    return json(dict_list, default=str)

@app.post("/api/dataset/create")
async def create_dataset_handler(request: Request, executor: ReviewRagPostgresExecutor):
    name = request.json['name']
    description = request.json['description']
    kb_dataset = MaxKbDataset(
        id=next(id_gen),
        name=name,
        description=description,
        type='',
        meta={},
        user_id='',
        remark='',
        creator='',
        create_time=datetime.now(),
        updater='',
        update_time=datetime.now(),
        deleted=0,
        tenant_id=0,
    )
    await executor.insert_dataset(
        kb_dataset.id,
        kb_dataset.name,
        kb_dataset.description,
        kb_dataset.type,
        dumps(kb_dataset.meta),
        kb_dataset.user_id,
        kb_dataset.remark,
        kb_dataset.creator,
        kb_dataset.create_time,
        kb_dataset.updater,
        kb_dataset.update_time,
        kb_dataset.deleted,
        kb_dataset.tenant_id,
    )
    return json(kb_dataset.__dict__, default=str)

@app.put("/api/dataset/<id>")
async def update_dataset_info_handler(request: Request, executor: ReviewRagPostgresExecutor, id: str):
    kb_dataset = await executor.select_dataset_by_id(id)
    if kb_dataset is None:
        return json({"error": "知识库不存在"})

    name = request.json['name']
    description = request.json['description']
    await executor.update_dataset_info(name, description, '', datetime.now(), id)

    kb_dataset.name = name
    kb_dataset.description = description
    return json(kb_dataset.__dict__, default=str)

@app.delete("/api/dataset")
async def delete_dataset_handler(request: Request, executor: ReviewRagPostgresExecutor):
    for id in request.json:
        await executor.update_dataset_mark_deleted(1, id)
    return json({})

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
        return json({"error": "没有文件"})
    file = request.files['file'][0]
    hash = hashlib.md5()
    hash.update(file.body)
    md5 = hash.hexdigest()

    exists_file = await executor.select_file_by_md5(md5, len(file.body))
    if exists_file:
        return json({"error": "文件已存在，请勿重复上传"})

    kb_file_id = next(id_gen)

    bucket.put_object(str(kb_file_id), file.body)

    filename, file_ext = splitext(file.name)
    local_file = '%d%s' % (kb_file_id, file_ext)
    with open(local_file, 'wb+') as f:
        f.write(file.body)

    kb_file = MaxKbFile(
        id = kb_file_id,
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
        kb_file_id,
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

    md_filename = '%s.md' % filename
    kb_document = MaxKbDocument(
        id = next(id_gen),
        name = md_filename,
        char_length = 0,
        status = 'Created',
        is_active = True,
        type = 'markdown',
        meta = {},
        dataset_id = 0,
        hit_handling_method = '',
        directly_return_similarity = 0,
        files = {},
        creator = '',
        create_time = datetime.now(),
        updater = '',
        update_time = datetime.now(),
        deleted = 0,
        tenant_id = 0,
    )
    await executor.insert_document(
        kb_document.id,
        kb_document.name,
        kb_document.char_length,
        kb_document.status,
        kb_document.is_active,
        kb_document.type,
        dumps(kb_document.meta),
        kb_document.dataset_id,
        kb_document.hit_handling_method,
        kb_document.directly_return_similarity,
        dumps(kb_document.files),
        kb_document.creator,
        kb_document.create_time,
        kb_document.updater,
        kb_document.update_time,
        kb_document.deleted,
        kb_document.tenant_id,
    )

    ChunksThread(kb_doc_id=kb_document.id, executor=executor, local_file_path=local_file).start()

    return json({"file": kb_file.__dict__}, default=str)

class ChunksThread(Thread):
    kb_doc_id: int
    local_file_path: str
    executor: ReviewRagPostgresExecutor

    def __init__(self, kb_doc_id, executor, local_file_path):
        super().__init__()
        self.kb_doc_id = kb_doc_id
        self.executor = executor
        self.local_file_path = local_file_path

    async def run_async(self):
        reader = PDFMarkerReader()
        doc = reader.load_data(self.local_file_path)[0]


        splitter = SentenceSplitter(language='en')
        chunk_list: List[MaxKbParagraph] = []
        groups = group_elements_by_title(extract_elements(doc.text))
        for g in groups:
            block_text = str.join('\n', [str(el.element) for el in g.elements])
            text_chunks = splitter.split(block_text)
            for chunk in text_chunks:
                kb_paragraph = MaxKbParagraph(
                    id=next(id_gen),
                    content=chunk,
                    title=g.title or '',
                    status='Created',
                    hit_num=0,
                    is_active=True,
                    dataset_id=0,
                    document_id=self.kb_doc_id,
                    creator='',
                    create_time=datetime.now(),
                    updater='',
                    update_time=datetime.now(),
                    deleted=0,
                    tenant_id=0
                )
                chunk_list.append(kb_paragraph)

        async def insert_paragraphs(chunk_list: List[MaxKbParagraph]):
            for paragraph in chunk_list:
                await self.executor.insert_paragraph(
                    paragraph.id,
                    paragraph.content,
                    paragraph.title,
                    paragraph.status,
                    paragraph.hit_num,
                    paragraph.is_active,
                    paragraph.dataset_id,
                    paragraph.document_id,
                    paragraph.creator,
                    paragraph.create_time,
                    paragraph.updater,
                    paragraph.update_time,
                    paragraph.deleted,
                    paragraph.tenant_id,
                )

        await insert_paragraphs(chunk_list)

        text_nodes = [TextNode(id_=str(chunk.id), text=chunk.content) for chunk in chunk_list]
        embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
        id_to_embed_map = embed_nodes(text_nodes, embed_model, show_progress=True)
        for chunk in chunk_list:
            kb_embedding = MaxKbEmbedding(
                id=next(id_gen),
                source_id=chunk.id,
                source_type='paragraph',
                is_active=True,
                embedding=id_to_embed_map[str(chunk.id)],
                meta={},
                dataset_id=0,
                document_id=self.kb_doc_id,
                paragraph_id=chunk.id,
                search_vector='',
                creator='',
                create_time=datetime.now(),
                updater='',
                update_time=datetime.now(),
                deleted=0,
                tenant_id=0
            )
            await self.executor.insert_embedding(
                kb_embedding.id,
                kb_embedding.source_id,
                kb_embedding.source_type,
                kb_embedding.is_active,
                kb_embedding.embedding,
                dumps(kb_embedding.meta),
                kb_embedding.dataset_id,
                kb_embedding.document_id,
                kb_embedding.paragraph_id,
                kb_embedding.search_vector,
                kb_embedding.creator,
                kb_embedding.create_time,
                kb_embedding.updater,
                kb_embedding.update_time,
                kb_embedding.deleted,
                kb_embedding.tenant_id,
            )
            await self.executor.update_paragraph_status('Completed', chunk.id)

        await self.executor.update_document_content(
            'Parsed',
            len(doc.text),
            dumps({"content": doc.text}),
            "{}",
            self.kb_doc_id
        )


    def run(self):
        asyncio.run(self.run_async())

if __name__ == "__main__":
    app.run(single_process=True)
