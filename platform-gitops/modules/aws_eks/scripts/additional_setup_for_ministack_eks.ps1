param(
    [Parameter(Mandatory)][securestring]$aws_admin_access_key,
    [Parameter(Mandatory)][securestring]$aws_admin_secret_key,
    [Parameter(Mandatory)][string]$aws_admin_region,

    # MiniStack (local AWS emulator) endpoint, e.g. http://localhost:4566
    [Parameter(Mandatory)][string]$eks_host_endpoint_url,
    [Parameter(Mandatory)][string]$eks_cluster_name,

    [Parameter(Mandatory)][string]$kubeconfig_container_file_path,
    [Parameter(Mandatory)][string]$kubeconfig_host_file_path,

    # containerd registry config that redirects image pulls to MiniStack's ECR
    [Parameter(Mandatory)][string]$registries_host_file_path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configure AWS CLI to talk to MiniStack instead of real AWS
$plain_aws_admin_access_key = ConvertFrom-SecureString -SecureString $aws_admin_access_key -AsPlainText
$plain_aws_admin_secret_key = ConvertFrom-SecureString -SecureString $aws_admin_secret_key -AsPlainText
aws configure set aws_access_key_id "${plain_aws_admin_access_key}"
aws configure set aws_secret_access_key "${plain_aws_admin_secret_key}"
aws configure set region "${aws_admin_region}"

# Wait for MiniStack to finish registering the cluster record
Write-Host "`n[EKS] Waiting for cluster '$eks_cluster_name' to become ACTIVE..."
$max_wait = 120; $waited = 0
do {
    Start-Sleep -Seconds 5; $waited += 5
    $status = aws --endpoint-url "${eks_host_endpoint_url}" eks describe-cluster `
                --name "${eks_cluster_name}" `
                --query "cluster.status" `
                --output text 2>$null
    Write-Host "[EKS] Status: '$status' (${waited}s / ${max_wait}s)"
} while ($status -ne "ACTIVE" -and $waited -lt $max_wait)

if ($status -ne "ACTIVE") {
    Write-Error "[EKS] Cluster did not reach ACTIVE within ${max_wait}s. Last status: '$status'"
    exit 1
}
Write-Host "[EKS] Cluster is ACTIVE."

# Find k3s container that MiniStack uses as EKS
$eks_container_name = docker ps --filter "name=ministack-eks" --format "{{.Names}}" | Select-Object -First 1
if (-not $eks_container_name) {
    Write-Error "[EKS] No k3s container found. Confirm MiniStack was started with the Docker socket mounted."
    exit 1
}
Write-Host "[EKS] k3s container: $eks_container_name"

# k3s API runs on 6443 inside the container, mapped to a random host port.
# The address MiniStack returns is Docker-internal and unreachable from the host.
$default_k3s_port = 6443
$port_line = docker port $eks_container_name $default_k3s_port | Select-Object -First 1
$host_port = $port_line -replace '.*:', ''
Write-Host "[EKS] k3s API host port: $host_port"

# Pull the kubeconfig out of the container and patch the server address
# from the container-internal 127.0.0.1:6443 to the actual host port
$k3s_config_directory_path = "/etc/rancher/k3s"

docker exec $eks_container_name cat "${k3s_config_directory_path}/k3s.yaml" | Out-File $kubeconfig_container_file_path -Encoding utf8

(Get-Content $kubeconfig_container_file_path) `
    -replace "https://127\.0\.0\.1:$default_k3s_port", "https://127.0.0.1:$host_port" |
    Set-Content $kubeconfig_host_file_path

Write-Host "[EKS] Kubeconfig written: $kubeconfig_host_file_path"

# Pull the kubeconfig out of the container and produce two patched copies.
# Raw k3s.yaml has server 127.0.0.1:6443 (container-internal, unreachable from host or other containers).
$k3s_config_directory_path = "/etc/rancher/k3s"
$raw_kubeconfig = docker exec $eks_container_name cat "${k3s_config_directory_path}/k3s.yaml"

# Host kubeconfig
$raw_kubeconfig -replace "https://127\.0\.0\.1:$default_k3s_port", "https://127.0.0.1:${host_port}" |
    Set-Content $kubeconfig_host_file_path -Encoding utf8
Write-Host "[EKS] Host kubeconfig written: $kubeconfig_host_file_path"

# Container kubeconfig
$raw_kubeconfig -replace "https://127\.0\.0\.1:$default_k3s_port", "https://${eks_container_name}:$default_k3s_port" |
    Set-Content $kubeconfig_container_file_path -Encoding utf8
Write-Host "[EKS] Container kubeconfig written: $kubeconfig_container_file_path"

# ACTIVE only means the cluster record exists. k3s itself still needs
# 30-90s to start. Block until the API server is actually reachable.
$env:KUBECONFIG = $kubeconfig_host_file_path
Write-Host "[EKS] Waiting for k3s API server at 127.0.0.1:$host_port..."
$max_api_wait = 120; $api_waited = 0; $api_ready = $false
do {
    Start-Sleep -Seconds 5; $api_waited += 5
    try { kubectl get nodes --request-timeout=5s 2>&1 | Out-Null } catch {}
    if ($LASTEXITCODE -eq 0) { $api_ready = $true }
    Write-Host "[EKS] API ready check: exit=$LASTEXITCODE (${api_waited}s / ${max_api_wait}s)"
} while (-not $api_ready -and $api_waited -lt $max_api_wait)

if (-not $api_ready) {
    Write-Error "[EKS] k3s API did not become ready within ${max_api_wait}s."
    exit 1
}
Write-Host "[EKS] k3s API is ready."

# k3s uses containerd (not the Docker daemon), so docker login has no effect.
# Copy registries.yaml into the container so containerd can find MiniStack's
# ECR, then restart k3s to pick up the config.
docker cp $registries_host_file_path "${eks_container_name}:${k3s_config_directory_path}/registries.yaml"
docker restart $eks_container_name
Write-Host "[EKS] Registry config applied, waiting for k3s to recover after restart..."
$max_recovery_wait = 120; $recovery_waited = 0; $api_recovered = $false
do {
    Start-Sleep -Seconds 5; $recovery_waited += 5
    try { kubectl get nodes --request-timeout=5s 2>&1 | Out-Null } catch {}
    if ($LASTEXITCODE -eq 0) { $api_recovered = $true }
    Write-Host "[EKS] Post-restart API check: exit=$LASTEXITCODE (${recovery_waited}s / ${max_recovery_wait}s)"
} while (-not $api_recovered -and $recovery_waited -lt $max_recovery_wait)

if (-not $api_recovered) {
    Write-Error "[EKS] k3s API did not recover after restart within ${max_recovery_wait}s."
    exit 1
}
Write-Host "[EKS] Cluster is ready."