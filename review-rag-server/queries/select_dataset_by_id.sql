SELECT
  id,
  name,
  description,
  type,
  meta,
  user_id,
  remark,
  creator,
  create_time,
  updater,
  update_time,
  deleted,
  tenant_id
FROM max_kb_dataset
WHERE id = $id and deleted = 0
LIMIT 1;
