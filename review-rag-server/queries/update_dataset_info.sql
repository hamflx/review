UPDATE max_kb_dataset
SET
  name = $name,
  description = $description,
  updater = $updater,
  update_time = $update_time
WHERE
  id = $id;
