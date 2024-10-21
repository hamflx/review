from oss2 import ProviderAuthV4, Bucket
from oss2.credentials import EnvironmentVariableCredentialsProvider

def get_storage_bucket():
    oss_auth = ProviderAuthV4(EnvironmentVariableCredentialsProvider())
    endpoint = 'https://oss-cn-nanjing.aliyuncs.com'
    region = 'cn-nanjing'
    return Bucket(oss_auth, endpoint=endpoint, bucket_name='review-rag', region=region)
