export const FetchFilesApi = '/api/files'
export const CreateFileApi = '/api/files/create'
export const DeleteFilesApi = '/api/files'

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

export interface Tags {}
