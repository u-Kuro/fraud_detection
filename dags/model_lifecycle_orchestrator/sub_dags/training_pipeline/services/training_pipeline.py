# from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
# from airflow.sdk import task
# from kubernetes import client as k8s
#
# from dags.shared.modules.configs import ecr_config
# from dags.shared.modules.configs.airflow import airflow_config, ModelDeploymentWorkflowsKeys
# from dags.model_lifecycle_orchestrator.sub_dags.training_pipeline.modules.schemas.airflow.configurations import TrainingPipelineConfigurations
#
# train_model_task_id = "train_model"
# @task(task_id="train_model_caller")
# def train_model_caller(**context):
#     configurations = TrainingPipelineConfigurations.from_context(context)
#     operator = KubernetesPodOperator(
#         task_id=train_model_task_id,
#         name=train_model_task_id,
#         namespace="default",
#         image=f"{ecr_config.ECR_URL}/train-model:latest",
#         image_pull_policy="Always",
#         image_pull_secrets=[
#             k8s.V1LocalObjectReference(
#                 name="ecr-secret"
#             )
#         ],
#         env_vars=[
#             k8s.V1EnvVar(
#                 name=ModelDeploymentWorkflowsKeys.MODEL_DEPLOYMENT_WORKFLOW_ID,
#                 value=configurations.model_deployment_workflow_id
#             ),
#         ],
#         env_from=[
#             k8s.V1EnvFromSource(
#                 config_map_ref=k8s.V1ConfigMapEnvSource(
#                     name="platform-infrastructure"
#                 )
#             ),
#             k8s.V1EnvFromSource(
#                 secret_ref=k8s.V1SecretEnvSource(
#                     name="mle-pipeline-secret"
#                 )
#             ),
#         ],
#         do_xcom_push=True,
#         get_logs=True,
#         is_delete_operator_pod=True,
#         startup_timeout_seconds=300,
#         config_file="/usr/local/airflow/dags/kubeconfig.yaml",
#     )
#     return operator.execute(context)