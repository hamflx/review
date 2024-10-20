import typed_settings as ts

@ts.settings
class ReviewRragLLMConfig:
    name: str
    temperature: float

@ts.settings
class ReviewRragEmbeddingConfig:
    name: str
    dim: int

@ts.settings
class ReviewRragRerankConfig:
    name: str
    topk: int

@ts.settings
class ReviewRragDatabaseConfig:
    retrieve_topk: int

@ts.settings
class ReviewRragConfig:
    llm: ReviewRragLLMConfig
    embedding: ReviewRragEmbeddingConfig
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
