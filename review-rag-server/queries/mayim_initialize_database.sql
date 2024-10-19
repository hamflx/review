-- encoding: gbk

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS max_kb_file (
  id BIGINT PRIMARY KEY,
  -- �ļ�ID
  md5 VARCHAR(32) NOT NULL,
  -- �ļ���MD5ֵ������У���ļ�һ����
  filename VARCHAR(64) NOT NULL,
  -- �ļ���
  file_size BIGINT NOT NULL,
  -- �ļ���С���ֽڣ�
  user_id VARCHAR(32),
  -- �û�ID����ʶ�ϴ��ļ����û�
  platform VARCHAR(64) NOT NULL,
  -- �ϴ�ƽ̨����S3��
  region_name VARCHAR(32),
  -- ������
  bucket_name VARCHAR(64) NOT NULL,
  -- �洢Ͱ����
  file_id VARCHAR(64) NOT NULL,
  -- �ļ��洢ID
  target_name VARCHAR(64) NOT NULL,
  -- �ļ��洢·��
  tags JSON,
  -- �ļ���ǩ��JSON��ʽ��
  creator VARCHAR(64) DEFAULT '',
  create_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updater VARCHAR(64) DEFAULT '',
  update_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted SMALLINT NOT NULL DEFAULT 0,
  tenant_id BIGINT NOT NULL DEFAULT 0
);

-- �˴���Ҫ DROP���Ա������ݶ�ʧ��
-- DROP TABLE IF EXISTS max_kb_dataset;
CREATE TABLE IF NOT EXISTS max_kb_dataset (
  id BIGINT PRIMARY KEY,
  name VARCHAR NOT NULL,
  description VARCHAR,
  type VARCHAR,
  meta JSONB,
  user_id VARCHAR NOT NULL,
  remark VARCHAR(256),
  creator VARCHAR(64) DEFAULT '',
  create_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updater VARCHAR(64) DEFAULT '',
  update_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted SMALLINT DEFAULT 0,
  tenant_id BIGINT NOT NULL DEFAULT 0
);

-- �˴���Ҫ DROP���Ա������ݶ�ʧ��
-- DROP TABLE IF EXISTS max_kb_document;
CREATE TABLE IF NOT EXISTS max_kb_document (
  id BIGINT NOT NULL,
  name VARCHAR NOT NULL,
  char_length INT NOT NULL,
  status VARCHAR NOT NULL,
  is_active BOOLEAN NOT NULL,
  type VARCHAR NOT NULL,
  meta JSONB NOT NULL,
  dataset_id BIGINT NOT NULL,
  hit_handling_method VARCHAR NOT NULL,
  directly_return_similarity FLOAT8 NOT NULL,
  files JSON,
  -- �ļ���Ϣ��JSON��ʽ��
  creator VARCHAR(64) DEFAULT '',
  create_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updater VARCHAR(64) DEFAULT '',
  update_time TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted SMALLINT NOT NULL DEFAULT 0,
  tenant_id BIGINT NOT NULL DEFAULT 0
);

-- �˴���Ҫ DROP���Ա������ݶ�ʧ��
-- DROP TABLE IF EXISTS max_kb_paragraph;
CREATE TABLE IF NOT EXISTS max_kb_paragraph (
  id BIGINT NOT NULL,
  content VARCHAR NOT NULL,
  title VARCHAR NOT NULL,
  status VARCHAR NOT NULL,
  hit_num INT NOT NULL,
  is_active BOOLEAN NOT NULL,
  dataset_id BIGINT NOT NULL,
  document_id BIGINT NOT NULL,
  creator VARCHAR(64) DEFAULT '',
  create_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updater VARCHAR(64) DEFAULT '',
  update_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted SMALLINT DEFAULT 0,
  tenant_id BIGINT NOT NULL DEFAULT 0
);

-- �˴���Ҫ DROP���Ա������ݶ�ʧ��
-- DROP TABLE IF EXISTS max_kb_embedding;
CREATE TABLE IF NOT EXISTS max_kb_embedding (
  id BIGINT PRIMARY KEY,
  source_id BIGINT NOT NULL,
  source_type VARCHAR NOT NULL,
  is_active BOOLEAN NOT NULL,
  embedding VECTOR NOT NULL,
  meta JSONB NOT NULL,
  dataset_id BIGINT NOT NULL,
  document_id BIGINT NOT NULL,
  paragraph_id BIGINT NOT NULL,
  search_vector TSVECTOR NOT NULL,
  creator VARCHAR(64) DEFAULT '',
  create_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updater VARCHAR(64) DEFAULT '',
  update_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted SMALLINT DEFAULT 0,
  tenant_id BIGINT NOT NULL DEFAULT 0
);
