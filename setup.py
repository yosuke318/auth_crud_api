

from setuptools import setup, find_packages

setup(
    name="sql_handler",
    version="1.0",
    python_requires='>=3.11',
    packages=find_packages(),
    install_requires=[
        'boto3>=1.35,<2.0',
        'pytz>=2021.3',
        'python-dotenv>=1.0,<2.0',
        'pymysql>=1.0,<2.0',
    ]
)