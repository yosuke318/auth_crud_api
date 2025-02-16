from botocore.exceptions import ClientError
from typing import Dict
from auth_api_config import AuthAPIConfig


class AdminAuthApi(AuthAPIConfig):

    def admin_create_user(self) -> Dict:
        """
        管理者によるユーザー登録(一時パスワードを発行)
        :return:
        :rtype:
        """
        try:
            response: Dict = self.boto3_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=self.username,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': self.username
                    }
                ],
                TemporaryPassword='Temporary_password123',
                MessageAction='SUPPRESS'
            )
            return response
        except ClientError as e:
            print(f"Admin signup failed: {e}")
            raise

    def admin_set_user_password(self) -> Dict:
        """
        管理者によるユーザーのパスワード設定
        :return:
        :rtype:
        """
        try:
            response: Dict = self.boto3_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=self.username,
                Password=self.password,
                Permanent=True
            )
            return response
        except ClientError as e:
            print(f"Admin signup failed: {e}")
            raise

    def admin_update_user_attributes(self) -> Dict:
        """
        管理者によるユーザーの属性更新
        :return:
        :rtype:
        """
        try:
            response: Dict = self.boto3_client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=self.username,
                UserAttributes=[
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ]
            )
            return response
        except ClientError as e:
            print(f"Admin signup failed: {e}")
            raise

