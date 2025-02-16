import boto3
from botocore.exceptions import ClientError
import hmac
import hashlib
import base64
from dotenv import load_dotenv
from typing import Dict, Union, Any
from congito_config import AuthConfig


load_dotenv()


# cognitoによる認証クラス
class AuthApi:
    def __init__(self):
        super().__init__()
        self.secret_hash = self._get_secret_hash()

    def _get_secret_hash(self) -> str:
        """
        クライアントシークレットを使用してシークレットハッシュを生成
        """
        message: str = self.username + self.client_id
        dig = hmac.new(self.client_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    def login(self, email: str, password: str) -> Dict[str, Union[str, int]]:
        """
        ログイン処理

        :param email: ユーザーのメールアドレス
        :type email: str
        :param password: ユーザーのパスワード
        :type password: str
        :return: 認証結果。成功時は認証トークンを、失敗時はエラーメッセージを含む。
        :rtype: Dict
        """
        try:
            # シークレットハッシュを生成
            response: Dict = self.client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': self.username,
                    'PASSWORD': self.password,
                    'SECRET_HASH': self.secret_hash
                },
                ClientId=self.client_id
            )
            return response['AuthenticationResult']
        except ClientError as e:
            print(f"Login failed: {e}")
            raise

    def start_password_reset(self, email: str) -> Dict[str, Any]:
        """
        パスワードリセット処理を開始し、認証コードを要求
        :param email: ユーザーのメールアドレス
        :type email: str
        :return 認証コード要求処理の結果
        :rtype: Dict
        """
        try:

            response: Dict = self.client.forgot_password(
                ClientId=self.client_id,
                SecretHash=self.secret_hash,
                Username=self.username
            )
            return response
        except ClientError as e:
            print(f"Password reset failed: {e}")
            raise

    def set_new_password(self, valid_code: str, new_password: str) -> Dict[str, Any]:
        """
        認証コードを検証し、新しいパスワードを設定

        :param valid_code: 認証コード
        :type valid_code: str
        :param new_password: 新しいパスワード
        :type new_password: str
        :return: パスワードリセットの結果
        :rtype: Dict[str, Any]
        """
        try:
            response = self.client.confirm_forgot_password(
                ClientId=self.client_id,
                SecretHash=self.secret_hash,
                Username=self.username,
                ConfirmationCode=valid_code,
                Password=new_password
            )

            return response
        except ClientError as e:
            print(f"Password reset failed: {e}")
            raise
