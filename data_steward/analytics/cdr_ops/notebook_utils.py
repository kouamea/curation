"""
Utility functions for notebooks
"""
import subprocess

import sqlalchemy

from gcloud.gsm import SecretManager
from common import CDR_SCOPES
from utils.auth import get_impersonation_credentials

IMPERSONATION_SCOPES = CDR_SCOPES + [
    'https://www.googleapis.com/auth/cloud-platform'
]

POSTGRES_USER_NAME = "pdr_psql_username"
POSTGRES_PASSWORD = "pdr_psql_password"
POSTGRES_PORT = 7005
DATABASE_NAME = "drc"
HOST = "localhost"
PDR_INSTANCE_NAME = "pdr_cloud_sql_read_only_instance"


def stop_cloud_sql_proxy(process):
    """
    Kills sub process that was used to start cloud_sql_proxy
    """
    process.terminate()


def start_cloud_sql_proxy(project_id, run_as):
    """
    Gets instance name from Secret manager and starts cloud_sql_proxy in a sub process

    :param project_id: Project name where secretes are stored
    :param run_as: service account email for impersonation
    """

    credentials = get_impersonation_credentials(
        target_principal=run_as, target_scopes=IMPERSONATION_SCOPES)

    instance = SecretManager(
        credentials=credentials).get_secret_from_secret_manager(
        PDR_INSTANCE_NAME, project_id)
    command = f'cloud_sql_proxy -instances={instance} --token=$(gcloud auth print-access-token \
    --impersonate-service-account={run_as})'

    return subprocess.Popen([command],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                            shell=True)


def pdr_client(project_id, run_as):
    """
    Gets the username and password for postgres instance and creates a connection
    which can be used to query the views in PDR project.

    NOTE: This expects cloud_sql_proxy is already installed in the google-cloud-sdk
    """

    credentials = get_impersonation_credentials(
        target_principal=run_as, target_scopes=IMPERSONATION_SCOPES)

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=SecretManager(
                credentials=credentials).get_secret_from_secret_manager(
                POSTGRES_USER_NAME, project_id),
            password=SecretManager(
                credentials=credentials).get_secret_from_secret_manager(
                POSTGRES_PASSWORD, project_id),
            host=HOST,
            port=POSTGRES_PORT,
            database=DATABASE_NAME),
        pool_recycle=3600,
        pool_timeout=30)
    pool.dialect.description_encoding = None
    return pool


def execute(client, query, max_rows=False):
    """
    Execute a bigquery command and return the results in a dataframe

    :param client: an instantiated bigquery client object
    :param query: the query to execute
    :param max_rows: Boolean option to manually turn on max rows display(default -> false)
    :return pandas dataframe object
    """
    import pandas as pd
    print(query)

    res = client.query(query).to_dataframe()
    if max_rows:
        pd.set_option('display.max_rows', res.shape[0] + 1)
    return res
