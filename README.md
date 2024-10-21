# RAG

演示地址：<https://review.hamflx.dev/search>（注：后端部署在内网上，由 vercel 转发到腾讯服务器再转发到 AutoDL 或本地机器上，网络可能不稳定）。

## 演示

视频如下，响应结果比较慢，中间有做剪辑处理。

<div><video controls src="https://github.com/user-attachments/assets/d8227ba9-15ac-4f1e-8834-525c48a1ac84" muted="false"></video></div>

## 特性

- 支持通义千问或本地的 rerank 模型。
- 支持通义千问大模型、OpenAI（未测试）。
- 支持聊天上下文。
- 支持滑动窗口优化检索结果。
- 支持指定知识库或全部知识库检索。
- 支持流式返回结果。

## 开发环境

- Nushell
- uv，管理 python 包与项目。
- bun，管理 npm 包与项目。

## 启动数据库

```shell
docker run --name postgres -e POSTGRES_PASSWORD=she4waeJ_uquahg7goh4aewu -p 5666:5432 -d pgvector/pgvector:pg17
```

## 运行服务端

需要提供阿里对象存储的 `OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET` 以及通义千问的 `DASHSCOPE_API_KEY`。

```shell
cd review-rag-server
OSS_ACCESS_KEY_ID=<OSS_ACCESS_KEY_ID> OSS_ACCESS_KEY_SECRET=<OSS_ACCESS_KEY_SECRET> DASHSCOPE_API_KEY=<DASHSCOPE_API_KEY> uv run --index-strategy unsafe-best-match main.py
```

## 运行前端

```shell
cd review-rag-web
bun install
bun run dev
```
