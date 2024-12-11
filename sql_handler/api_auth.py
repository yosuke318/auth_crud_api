import boto3
from botocore.exceptions import ClientError
import os
import hmac
import hashlib
import base64
from dotenv import load_dotenv
from typing import Dict, Union, Any

load_dotenv()


# cognitoによる認証クラス
class AuthApi:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.region = 'ap-northeast-1'

    def get_secret_hash(self, username: str) -> str:
        """
        クライアントシークレットを使用してシークレットハッシュを生成
        """
        message: str = username + self.client_id
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
            secret_hash: str = self.get_secret_hash(email)

            client = boto3.client('cognito-idp', region_name=self.region)

            response: Dict = client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    'SECRET_HASH': secret_hash
                },
                ClientId=self.client_id
            )
            return response['AuthenticationResult']
        except ClientError as e:
            print(f"Login failed: {e}")
            return {'error': str(e)}

    def start_password_reset(self, email: str) -> Dict[str, Any]:
        """
        パスワードリセット処理を開始し、認証コードを要求
        :param email: ユーザーのメールアドレス
        :type email: str
        :return 認証コード要求処理の結果
        :rtype: Dict
        """
        try:
            # シークレットハッシュを生成
            secret_hash: str = self.get_secret_hash(email)

            client = boto3.client('cognito-idp', region_name=self.region)

            response: Dict = client.forgot_password(
                ClientId=self.client_id,
                SecretHash=secret_hash,
                Username=email
            )
            return response
        except ClientError as e:
            print(f"Password reset failed: {e}")
            return {'error': str(e)}

    def set_new_password(self, email: str, valid_code: str, new_password: str) -> Dict[str, Any]:
        """
        認証コードを検証し、新しいパスワードを設定

        :param email: ユーザーのメールアドレス
        :type email: str
        :param valid_code: 認証コード
        :type valid_code: str
        :param new_password: 新しいパスワード
        :type new_password: str
        :return: パスワードリセットの結果
        :rtype: Dict[str, Any]
        """
        try:
            # 環境変数から取得
            client_id: str = os.getenv('CLIENT_ID')

            # シークレットハッシュを生成
            secret_hash: str = self.get_secret_hash(email)

            client = boto3.client('cognito-idp', region_name=self.region)

            response = client.confirm_forgot_password(
                ClientId=client_id,
                SecretHash=secret_hash,
                Username=email,
                ConfirmationCode=valid_code,
                Password=new_password
            )

            return response
        except ClientError as e:
            print(f"Password reset failed: {e}")
            return {'error': str(e)}

    @staticmethod
    def admin_signup(email: str, password: str) -> Dict:
        """
        管理者によるユーザー登録処理
        """
        try:
            # 環境変数から取得
            user_pool_id = os.getenv('USER_POOL_ID')

            client = boto3.client(
                'cognito-idp',
                region_name='ap-northeast-1',
            )

            # 管理者APIでユーザーを作成
            response: Dict = client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    }
                ],
                TemporaryPassword='Temporary_password123',
                MessageAction='SUPPRESS'  # メール通知を抑制
            )

            # 管理者APIでパスワードを設定
            client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=email,
                Password=password,
                Permanent=True
            )

            # 管理者APIでメールアドレスを検証済みにする
            client.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ]
            )

            return {'message': 'User created successfully'}
        except ClientError as e:
            print(f"Admin signup failed: {e}")
            return {'error': str(e)}

    @staticmethod
    def pre_token_generate(event: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """
        トークン生成前に、prefix付きのuuidをIDトークンに追加します
        :param event:
        :type event:
        :param prefix:
        :type prefix:
        :rtype: Dict
        """

        try:
            event['response']['claimsOverrideDetails'] = {
                'claimsToAddOrOverride': {
                    'prefixed_sub': prefix + '_' + event['request']['userAttributes']['sub']
                }
            }
            return event

        except Exception as e:
            print(f"Pre token generate failed: {e}")
            return {'error': str(e)}
