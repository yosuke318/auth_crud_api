from abc import ABC, abstractmethod
from congito_config import AuthConfig
import boto3

class AuthAPIConfig(ABC):
    def __init__(self, username=None, password=None, config: AuthConfig = AuthConfig.from_env()):
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.user_pool_id = config.user_pool_id
        self.region = config.region
        self.username = username
        self.password = password
        self.boto3_client = boto3.client('cognito-idp', region_name=self.region)
