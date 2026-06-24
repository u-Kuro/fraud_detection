# from shared.schemas.base_environment import MleEnvironmentBase
#
# class FraudApiEnvironment(MleEnvironmentBase):
#     """
#     Runtime values for fraud_api.
#     Postgres + MLflow use standard env vars — not declared here.
#     """
#     # Slack
#     SLACK_BOT_USER_AUTH_TOKEN: str
#     SLACK_APP_LEVEL_TOKEN:     str
#     SLACK_CHANNEL_ID:          str
#     SLACK_SIGNING_SECRET:      str
#
#     # Airflow REST API — fraud_api proxies Slack actions here.
#     # MWAA_WEBSERVER_URL comes from platform-infra ConfigMap.
#     MWAA_WEBSERVER_URL: str = "http://airflow-webserver:8080"
#     AIRFLOW_USERNAME:   str = "admin"
#     AIRFLOW_PASSWORD:   str = "admin"
#
# environment = FraudApiEnvironment()