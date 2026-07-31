param(
    [Parameter(Mandatory)][string]$aws_access_key,
    [Parameter(Mandatory)][string]$aws_secret_key,
    [Parameter(Mandatory)][string]$aws_region,

    [Parameter(Mandatory)][string]$eks_service_endpoint_url,
    [Parameter(Mandatory)][string]$eks_cluster_name,
    [Parameter(Mandatory)][string]$temporary_kubeconfig_file_path,

    [Parameter(Mandatory)][string]$s3_service_endpoint_url,
    [Parameter(Mandatory)][string]$s3_dag_kubeconfig_uri
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configure aws in host
aws configure set aws_access_key_id "${aws_access_key}"
aws configure set aws_secret_access_key "${aws_secret_key}"
aws configure set region "${aws_region}"

# Upload airflow kubeconfig
aws --endpoint-url "${eks_service_endpoint_url}" eks update-kubeconfig `
    --name "${eks_cluster_name}" `
    --kubeconfig ${temporary_kubeconfig_file_path} | Out-Null

aws --endpoint-url "${s3_service_endpoint_url}" s3 cp `
    "${temporary_kubeconfig_file_path}" `
    "${s3_dag_kubeconfig_uri}"

Write-Host "[MWAA] Internal kubeconfig uploaded to ${s3_dag_kubeconfig_uri}"
