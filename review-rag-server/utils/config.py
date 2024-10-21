from typing import Optional
import typed_settings as ts

@ts.settings
class ReviewRragLLMConfig:
    name: str
    temperature: float
    provider: str

@ts.settings
class ReviewRragChunkConfig:
    window_size: int

@ts.settings
class ReviewRragEmbeddingConfig:
    name: str
    dim: int

@ts.settings
class ReviewRragRetrieveConfig:
    topk: int
    similarity_cutoff: float

@ts.settings
class ReviewRragRerankConfig:
    topk: int
    name: Optional[str] = None

@ts.settings
class ReviewRragDatabaseConfig:
    host: str
    port: int
    user: str
    password: str


@ts.settings
class ReviewRragConfig:
    llm: ReviewRragLLMConfig
    chunk: ReviewRragChunkConfig
    embedding: ReviewRragEmbeddingConfig
    retrieve: ReviewRragRetrieveConfig
    rerank: ReviewRragRerankConfig
    database: ReviewRragDatabaseConfig

config = ts.load_settings(
    cls=ReviewRragConfig,
    loaders=[
        ts.loaders.FileLoader(
            files=[ts.find("config.toml")],
            formats={"*.toml": ts.loaders.TomlFormat(None)},
        ),
    ],
)
