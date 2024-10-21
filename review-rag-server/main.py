from database.vector import ReviewRagPGVectorStore
from storage import get_storage_bucket
from utils.config import config

import os
import hashlib
import asyncio

from datetime import datetime
from json import dumps
from typing import Any, List, Optional
from threading import Thread
from os.path import splitext

from loguru import logger
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
from llama_index.readers.pdf_marker import PDFMarkerReader
from llama_index.core.postprocessor import SimilarityPostprocessor
from utils.markdown import extract_elements, group_elements_by_title
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.indices.utils import embed_nodes
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex
from llama_index.llms.dashscope import DashScope
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.chat_engine.types import ChatMode
from llama_index.postprocessor.dashscope_rerank import DashScopeRerank
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)

id_gen = SnowflakeGenerator(100)

class ReviewRagPostgresExecutor(PostgresExecutor):
    async def select_all_files(self, limit: int = 20, offset: int = 0) -> list[MaxKbFile]:
        ...
    async def select_all_documents(self, dataset_id, limit: int = 20, offset: int = 0) -> list[MaxKbDocument]:
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
    async def update_document_mark_deleted(self, deleted, id) -> None:
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

def create_chat_engine_with_dataset_id(dataset_id: int):
    filters = MetadataFilters(
        filters=[
            MetadataFilter(
                key="dataset_id", operator=FilterOperator.EQ, value=dataset_id
            ),
        ],
    ) if dataset_id else None
    chat_engine = app.ctx.index.as_chat_engine(
        llm=app.ctx.llm,
        chat_mode=ChatMode.BEST,
        similarity_top_k=config.retrieve.topk,
        node_postprocessors=[
            # TrimOverlapped(mongo=mongo_client(), target_metadata_key="window"),
            # WindowTextLoader(mongo=mongo_client(), target_metadata_key="window"),
            # MetadataReplacementPostProcessor(target_metadata_key="window"),

            # 过滤检索结果时使用的最低相似度阈值
            SimilarityPostprocessor(similarity_cutoff=config.retrieve.similarity_cutoff),

            # 对检索结果进行重排，返回语义上相关度最高的结果。
            app.ctx.rerank_processor,
        ], 
        # text_qa_template=ChatPromptTemplate(message_templates=[
        #     ChatMessage(role=MessageRole.SYSTEM, content=CHAT_SYSTEM_PROMPT_STR),
        #     ChatMessage(role=MessageRole.USER, content=CHAT_QA_PROMPT_TMPL_STR),
        # ]),
        # refine_template=ChatPromptTemplate(message_templates=[
        #     ChatMessage(role=MessageRole.SYSTEM, content=CHAT_SYSTEM_PROMPT_STR),
        #     ChatMessage(role=MessageRole.USER, content=CHAT_REFINE_QA_PROMPT_TMPL_STR),
        # ]),
        filters=filters,
    )
    return chat_engine

@app.before_server_start
async def setup_mayim(app: Sanic):
    app.ctx.bucket = get_storage_bucket()

    logger.info("Building embedding model...")
    embed_model = HuggingFaceEmbedding(model_name=config.embedding.name)
    app.ctx.embed_model = embed_model

    logger.info("Building LLM...")
    app.ctx.llm = DashScope(model_name=config.llm.name, api_key=os.getenv("DASHSCOPE_API_KEY"))

    vector_store = ReviewRagPGVectorStore.from_params(
        database="postgres",
        host=config.database.host,
        password=config.database.password,
        port=str(config.database.port),
        user=config.database.user,
        table_name="max_kb_embedding",
        embed_dim=config.embedding.dim  # openai embedding dimension
    )
    app.ctx.index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
    if config.rerank.name:
        app.ctx.rerank_processor = SentenceTransformerRerank(model=config.rerank.name, top_n=config.rerank.topk)
    else:
        app.ctx.rerank_processor = DashScopeRerank(top_n=config.rerank.topk, model="gte-rerank")

    logger.info("Connecting to postgres...")
    executor = ReviewRagPostgresExecutor()
    app.ctx.pool = PostgresPool(dsn="postgres://%s:%s@%s:%d" % (config.database.user, config.database.password, config.database.host, config.database.port))
    await app.ctx.pool.open()
    Mayim(executors=[executor], pool=app.ctx.pool)
    app.ext.dependency(executor)
    await executor.initialize_database()

@app.after_server_stop
async def shutdown_mayim(app: Sanic):
    await app.ctx.pool.close()

@app.post("/api/chat")
async def chat_with_llm(request: Request, executor: ReviewRagPostgresExecutor):
    dataset_id = int(request.json['datasetId']) if request.json['datasetId'] else 0
    query = request.json['query']
    history = request.json['history'] or []
    normalized_history = [ChatMessage.from_str(h['message'], h['role']) for h in history]
    response = await request.respond(content_type="text/plain; charset=utf-8")

    chat_engine = create_chat_engine_with_dataset_id(dataset_id)
    chat_response = chat_engine.stream_chat(query, normalized_history)
    for token in chat_response.response_gen:
        await response.send(token)
    await response.eof()

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

@app.get("/api/dataset/<dataset_id>/document")
async def fetch_all_files(request: Request, executor: ReviewRagPostgresExecutor, dataset_id: str):
    files = await executor.select_all_documents(int(dataset_id))
    list = []
    for f in files:
        file_dict = f.__dict__.copy()
        file_dict['id'] = str(file_dict['id'])
        list.append(file_dict)
    return json(list, default=str)

@app.delete("/api/dataset/<dataset_id>/document")
async def delete_files(request: Request, executor: ReviewRagPostgresExecutor, dataset_id: str):
    ids = tuple(request.json)
    for id in ids:
        await executor.update_document_mark_deleted(1, int(id))
    return json({"success": True})

@app.post("/api/dataset/<dataset_id>/document/create")
async def create_new_file_handler(request: Request, executor: ReviewRagPostgresExecutor, dataset_id: str):
    file = request.files.get('file')
    if not file:
        return json({"error": "没有文件"})
    file = request.files['file'][0]
    hash = hashlib.md5()
    hash.update(file.body)
    md5 = hash.hexdigest()

    kb_file = await executor.select_file_by_md5(md5, len(file.body))
    local_file = ''
    if not kb_file:
        kb_file_id = next(id_gen)

        app.ctx.bucket.put_object(str(kb_file_id), file.body)

        filename, file_ext = splitext(file.name)
        if not os.path.exists('caches'):
            os.mkdir('caches')
        local_file = os.path.join('caches', '%d%s' % (kb_file_id, file_ext))
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

    kb_document = MaxKbDocument(
        id = next(id_gen),
        name = file.name,
        char_length = 0,
        status = 'Created',
        is_active = True,
        type = 'markdown',
        meta = {},
        dataset_id = int(dataset_id),
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

    if local_file:
        EmbeddingThread(kb_dataset_id=int(dataset_id), kb_doc_id=kb_document.id, executor=executor, local_file_path=local_file, embed_model=app.ctx.embed_model).start()
    else:
        logger.info("文档对应的文件已经存在，跳过向量化。")

    return json({"file": kb_document.__dict__}, default=str)

class EmbeddingThread(Thread):
    kb_dataset_id: int
    kb_doc_id: int
    local_file_path: str
    embed_model: Any
    executor: ReviewRagPostgresExecutor

    def __init__(self, kb_dataset_id, kb_doc_id, executor, local_file_path, embed_model):
        super().__init__()
        self.kb_dataset_id = kb_dataset_id
        self.kb_doc_id = kb_doc_id
        self.executor = executor
        self.local_file_path = local_file_path
        self.embed_model = embed_model

    async def run_async(self):
        logger.info(f"开始向量化文档【{self.local_file_path}】")

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
                    dataset_id=self.kb_dataset_id,
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
        id_to_embed_map = embed_nodes(text_nodes, self.embed_model, show_progress=True)
        for chunk in chunk_list:
            kb_embedding = MaxKbEmbedding(
                id=next(id_gen),
                source_id=chunk.id,
                source_type='paragraph',
                is_active=True,
                embedding=id_to_embed_map[str(chunk.id)],
                meta={"text": chunk.content},
                dataset_id=self.kb_dataset_id,
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
    app.run(single_process=True, host="0.0.0.0")
