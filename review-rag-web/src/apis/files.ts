const api = function (strings: TemplateStringsArray) {
  return (vars: Record<string, string | undefined | null>) => {
    return Object.entries(vars).reduce(
      (path, [key, value]) => {
        if (value == null) return path
        return path.replaceAll(`{${key}}`, value)
      },
      strings.join('')
    )
  }
}

export const FetchDocumentApi = api`/api/dataset/{dataset_id}/document`
export const CreateDocumentApi = api`/api/dataset/{dataset_id}/document/create`
export const DeleteDocumentApi = api`/api/dataset/{dataset_id}/document`

export const FetchDatasetApi = '/api/dataset'
export const CreateDatasetApi = '/api/dataset/create'
export const UpdateDatasetInfoApi = '/api/dataset/{id}'
export const DeleteDatasetApi = '/api/dataset'

export interface MaxKbDocument {
  id: string
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

export interface MaxKbDataset {
  id: string
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
export interface Meta {}
