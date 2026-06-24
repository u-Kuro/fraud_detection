# from shared.schemas.base_environment import MleEnvironmentBase
#
# class DriftEnvironment(MleEnvironmentBase):
#     """
#     Runtime values for drift_monitor.
#
#     Postgres: libpq reads PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD.
#     S3:       boto3 reads AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/
#               AWS_DEFAULT_REGION/AWS_ENDPOINT_URL_S3.
#     MLflow:   not used by drift_monitor.
#     """
#     SLACK_BOT_USER_AUTH_TOKEN: str
#     SLACK_CHANNEL_ID:          str
#
#     # psycopg2 reads PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE from env.
#     # PGHOST/PGPORT/PGDATABASE come from platform-infra ConfigMap.
#     # PGUSER/PGPASSWORD come from the mle-pipeline-secret.
#     @property
#     def POSTGRES_FRAUD_DB_URL(self) -> str:
#         return "postgresql+psycopg2://"
#
#     @property
#     def S3_PIPELINE_REFERENCE_PATH(self) -> str:
#         return "reference"
#
#     @property
#     def S3_PIPELINE_DRIFT_REPORTS_PATH(self) -> str:
#         return "drift_reports"
#
# environment = DriftEnvironment()