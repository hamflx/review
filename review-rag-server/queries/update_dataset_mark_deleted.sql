UPDATE max_kb_dataset
SET
  deleted = $deleted
WHERE
  id = $id;
