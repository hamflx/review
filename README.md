# RAG

## 启动数据库

```shell
docker run --name postgres -e POSTGRES_PASSWORD=she4waeJ_uquahg7goh4aewu -p 5666:5432 -d pgvector/pgvector:pg17
```

## 运行服务端

```shell
cd review-rag-server
pip3 install sanic sanic-ext pydantic mayim[postgres]
python3 main.py
```
