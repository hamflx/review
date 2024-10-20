UPDATE max_kb_document
SET
status = $status,
char_length = $char_length,
files = $files,
meta = $meta
WHERE
id = $id;
