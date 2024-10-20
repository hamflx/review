export const errorMessage = <T>(response: CommonResponse<T>): string | undefined => {
  if (response && typeof response === 'object' && 'error' in response) {
    return response.error
  }
  return undefined
}

export const isError = <T>(response: CommonResponse<T>): response is ApiError => {
  if (response && typeof response === 'object' && 'error' in response) {
    return true
  }
  return false
}

export type CommonResponse<T = EmptyResponse> = ApiError | T

export interface ApiError {
  error: string
}

export interface EmptyResponse {
  success: true
}
