param(
    [Parameter(Mandatory)][string]$cluster_name,
    [Parameter(Mandatory)][string]$temporary_kubeconfig_file_path,
    [Parameter(Mandatory)][string]$airflow_kubeconfig_s3_uri
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

aws --endpoint-url http://localhost:4566 eks update-kubeconfig `
    --name $cluster_name `
    --kubeconfig $temporary_kubeconfig_file_path | Out-Null

aws --endpoint-url http://localhost:4566 s3 cp `
    $temporary_kubeconfig_file_path `
    $airflow_kubeconfig_s3_uri

Write-Host "[MWAA] Internal kubeconfig uploaded to $airflow_kubeconfig_s3_uri"