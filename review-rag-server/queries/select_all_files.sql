SELECT
  id,
  md5,
  filename,
  file_size,
  user_id,
  platform,
  region_name,
  bucket_name,
  file_id,
  target_name,
  tags,
  creator,
  create_time,
  updater,
  update_time,
  deleted,
  tenant_id
FROM max_kb_file
LIMIT $limit OFFSET $offset;
