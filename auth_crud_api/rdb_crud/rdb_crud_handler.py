import os
from dotenv import load_dotenv
from typing import Dict, Any
import pymysql
from dataclasses import dataclass

load_dotenv()


class DatabaseError(BaseException):
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(message)


class DatabaseConnectionError(DatabaseError):
    pass


class DatabaseQueryError(DatabaseError):
    pass


@dataclass
class DatabaseConfig:
    db_host: str
    db_user: str
    db_password: str
    db_name: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        return cls(
            db_host=os.getenv('DB_HOST'),
            db_user=os.getenv('DB_USER'),
            db_password=os.getenv('DB_PASSWORD'),
            db_name=os.getenv('DB_NAME')
        )



# データベース操作を扱うクラス
class RDBCrudHandler:
    def __init__(self, config: DatabaseConfig = DatabaseConfig.from_env()):
        self.db_host = config.db_host
        self.db_user = config.db_user
        self.db_password = config.db_password
        self.db_name = config.db_name

    def connect(self):
        try:
            connection = pymysql.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return {'error': str(e)}

    def show_env_values(self):
        print(self.db_host)

    def _extract_user_id(event: Dict[str, Any]) -> str:
        """
        claimからuser_idを抽出
        :param event:
        :type event:
        :return: ユーザーID
        :rtype: str
        """
        try:
            user_id = event['requestContext']['authorizer']['claims']['sub']
            if not user_id:
                return {'error': 'User not found in claims'}
            return user_id
        except KeyError as e:
            print(f"Key error: {e}")
            return {'error': 'Invalid event structure'}

    def get_user_info(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        user_idを使用してMySQLDBからデータ取得
        :param event:
        :type Dict:
        :return: ユーザー情報
        :rtype: Dict
        """
        user_id = self._extract_user_id(event)
        if 'error' in user_id:
            return user_id

        try:
            connection = self.connect()
            with connection:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM users WHERE user_id = %s"
                    cursor.execute(sql, (user_id,))
                    result = cursor.fetchone()
                    if not result:
                        return {'error': 'User not found in users table'}
                    return result
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return {'error': str(e)}
