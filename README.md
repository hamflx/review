# RAG

## 开发环境

- Nushell
- uv

## 启动数据库

```shell
docker run --name postgres -e POSTGRES_PASSWORD=she4waeJ_uquahg7goh4aewu -p 5666:5432 -d pgvector/pgvector:pg17
```

## 运行服务端

```shell
cd review-rag-server
OSS_ACCESS_KEY_ID=<OSS_ACCESS_KEY_ID> OSS_ACCESS_KEY_SECRET=<OSS_ACCESS_KEY_SECRET> uv run --index-strategy unsafe-best-match main.py
```

## 运行前端

```shell
cd review-rag-web
bun install
bun run dev
```
