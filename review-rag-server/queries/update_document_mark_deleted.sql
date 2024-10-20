UPDATE max_kb_document
SET
  deleted = $deleted
WHERE
  id = $id;
