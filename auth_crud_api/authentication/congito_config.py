from dataclasses import dataclass

@dataclass
class AuthConfig:
    client_id: str
    client_secret: str
    user_pool_id: str
    region: str

    @classmethod
    def from_env(cls) -> 'AuthConfig':
        return cls(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            user_pool_id=os.getenv('USER_POOL_ID'),
            region='ap-northeast-1'
        )