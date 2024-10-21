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
  tenant_id,
  coalesce(completed, 0) as completed,
  coalesce(total, 0) as total
FROM max_kb_dataset
left join (
  select count(case status when 'Completed' then 1 else null end) as completed, count(1) as total, dataset_id from max_kb_document group by dataset_id
) doc on max_kb_dataset.id = doc.dataset_id
WHERE deleted = 0
LIMIT $limit OFFSET $offset;
