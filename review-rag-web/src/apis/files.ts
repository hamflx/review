export const FetchFilesApi = '/api/files'
export const CreateFileApi = '/api/files/create'
export const DeleteFilesApi = '/api/files'

export const FetchDatasetApi = '/api/dataset'
export const CreateDatasetApi = '/api/dataset/create'
export const UpdateDatasetInfoApi = '/api/dataset/{id}'
export const DeleteDatasetApi = '/api/dataset'

export interface MaxKbFile {
  id: number
  md5: string
  filename: string
  file_size: number
  user_id: string
  platform: string
  region_name: string
  bucket_name: string
  file_id: string
  target_name: string
  tags: Tags
  creator: string
  create_time: string
  updater: string
  update_time: string
  deleted: number
  tenant_id: number
}

export interface MaxKbDataset {
  id: number
  name: string
  description: string
  type: string
  meta: Meta
  user_id: string
  remark: string
  creator: string
  create_time: string
  updater: string
  update_time: string
  deleted: number
  tenant_id: number
}

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface Tags {}

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface Meta {}
