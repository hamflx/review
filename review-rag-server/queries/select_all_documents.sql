SELECT
  id,
  name,
  char_length,
  status,
  is_active,
  type,
  meta,
  dataset_id,
  hit_handling_method,
  directly_return_similarity,
  files,
  creator,
  create_time,
  updater,
  update_time,
  deleted,
  tenant_id
FROM max_kb_document
WHERE dataset_id = $dataset_id and deleted = 0
LIMIT $limit OFFSET $offset;
