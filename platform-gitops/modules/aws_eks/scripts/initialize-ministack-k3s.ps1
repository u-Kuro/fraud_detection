param(
    [Parameter(Mandatory)][string]$aws_access_key,
    [Parameter(Mandatory)][string]$aws_secret_key,
    [Parameter(Mandatory)][string]$aws_region,

    [Parameter(Mandatory)][string]$eks_service_endpoint_url,
    [Parameter(Mandatory)][string]$eks_cluster_name,

    [Parameter(Mandatory)][string]$kubeconfig_host_directory_path,
    [Parameter(Mandatory)][string]$kubeconfig_host_file_name,

    [Parameter(Mandatory)][string]$ecr_registry_endpoint,
    [Parameter(Mandatory)][string]$ecr_registry_mirror_endpoint_url,
    [Parameter(Mandatory)][string]$ecr_registry_mirror_endpoint,

    [Parameter(Mandatory)][string]$ecr_registry_secret_name
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configure aws in host
aws configure set aws_access_key_id "${aws_access_key}"
aws configure set aws_secret_access_key "${aws_secret_key}"
aws configure set region "${aws_region}"

# Wait for cluster to be active
Write-Host "`n[EKS] Waiting for cluster '${eks_cluster_name}' to become ACTIVE..."
$max_wait = 120; $waited = 0
do {
    Start-Sleep -Seconds 5; $waited += 5
    $status = aws --endpoint-url "${eks_service_endpoint_url}" eks describe-cluster `
                --name "${eks_cluster_name}" `
                --query "cluster.status" `
                --output text 2>$null
    Write-Host "[EKS] Status: $status (${waited}s elapsed)"
} while ($status -ne "ACTIVE" -and $waited -lt $max_wait)

if ($status -ne "ACTIVE") {
    Write-Error "[EKS] Cluster did not become ACTIVE within ${max_waits}."; exit 1
}

# Find the eks container name
$eks_container_name = docker ps --filter "name=ministack-eks" --format "{{.Names}}" | Select-Object -First 1
if (-not $eks_container_name) {
    $eks_container_name = docker ps --filter "name=k3s" --format "{{.Names}}" | Select-Object -First 1
}
if (-not $eks_container_name) {
    Write-Error "[EKS] No k3s container found. Confirm MiniStack was started with the Docker socket mounted."; exit 1
}
Write-Host "[EKS] k3s container: $eks_container_name"

# Get the host published port of the eks container
# k3s API listens on 6443 inside the container. Docker publishes it on a
# random host port. The MiniStack describe-cluster endpoint returns the
# Docker-internal DNS name (unreachable from the host), so we must read
# the real host port directly from Docker.
$default_k3s_port = 6443;
$port_line = docker port $eks_container_name $default_k3s_port | Select-Object -First 1
$host_port = $port_line -replace '.*:', ''
Write-Host "[EKS] k3s API host port: $host_port"

# Copy eks container's kubeconfig.yaml to host
$k3s_mount_directory_path = "/etc/rancher/k3s"
New-Item -ItemType Directory -Force -Path "${kubeconfig_host_directory_path}" | Out-Null
$kubeconfig_file_path = Join-Path "${kubeconfig_host_directory_path}" "${kubeconfig_host_file_name}"

docker exec $eks_container_name cat "${k3s_mount_directory_path}/k3s.yaml" | Out-File $kubeconfig_file_path -Encoding utf8

# Replace Docker-internal 127.0.0.1:6443 with the actual host port.
(Get-Content $kubeconfig_file_path) `
    -replace "https://127\.0\.0\.1:$default_k3s_port", "https://127.0.0.1:$host_port" |
    Set-Content $kubeconfig_file_path

Write-Host "[EKS] Kubeconfig written: $kubeconfig_file_path"

# Wait for k3s API server to be ready
# Ministack returns ACTIVE the instant the EKS record is created — it has no
# knowledge of whether the k3s container has actually finished bootstrapping.
# K3s needs 30-90 s to start flannel, CoreDNS, and the API server. Terraform's
# helm_apps module depends_on eks_cluster, so blocking here until kubectl can
# reach the cluster guarantees Helm never hits a "connection refused".
$env:KUBECONFIG = $kubeconfig_file_path
Write-Host "[EKS] Waiting for k3s API server to become ready at 127.0.0.1:${host_port}..."
$max_api_wait = 120; $api_waited = 0; $api_ready = $false
do {
    Start-Sleep -Seconds 5; $api_waited += 5
    try { kubectl get nodes --request-timeout=5s 2>&1 | Out-Null } catch {}
    if ($LASTEXITCODE -eq 0) { $api_ready = $true }
    Write-Host "[EKS] API ready check (${api_waited}s elapsed, exitCode=${LASTEXITCODE})"
} while (-not $api_ready -and $api_waited -lt $max_api_wait)

if (-not $api_ready) {
    Write-Error "[EKS] k3s API did not become ready within ${max_api_wait}s."; exit 1
}
Write-Host "[EKS] k3s API is ready."

# Set containerd to pull from MiniStack ECR
# k3s uses containerd, not Docker daemon. docker login has no effect on k3s.
# registries.yaml tells containerd where to find the MiniStack ECR mirror.
$registries_yaml = @"
mirrors:
  "${ecr_registry_endpoint}":
    endpoint:
      - "${ecr_registry_mirror_endpoint_url}"
configs:
  "${ecr_registry_mirror_endpoint}":
    auth:
      username: AWS
      password: test
"@

$temp_registries = Join-Path $env:TEMP "ministack-registries.yaml"
$registries_yaml | Set-Content $temp_registries -Encoding utf8

docker cp $temp_registries "${eks_container_name}:${k3s_mount_directory_path}/registries.yaml"
docker restart $eks_container_name
Write-Host "[EKS] containerd registry configured. Restarting k3s container, waiting for API to recover..."
$max_recovery_wait = 120; $recovery_waited = 0; $api_recovered = $false
do {
    Start-Sleep -Seconds 5; $recovery_waited += 5
    try { kubectl get nodes --request-timeout=5s 2>&1 | Out-Null } catch {}
    if ($LASTEXITCODE -eq 0) { $api_recovered = $true }
    Write-Host "[EKS] Post-restart API check (${recovery_waited}s elapsed, exitCode=$LASTEXITCODE)"
} while (-not $api_recovered -and $recovery_waited -lt $max_recovery_wait)

if (-not $api_recovered) {
    Write-Error "[EKS] k3s API did not recover after restart within ${max_recovery_wait}s."; exit 1
}

# Create ECR imagePullSecret in k3s
# $env:KUBECONFIG is already set from the readiness block above.
kubectl create secret docker-registry "${ecr_registry_secret_name}" `
    --docker-server="${ecr_registry_endpoint}" `
    --docker-username=AWS `
    --docker-password=test `
    --dry-run=client -o yaml | kubectl apply -f -

if ($LASTEXITCODE -ne 0) {
    Write-Error "[EKS] Failed to apply ${ecr_registry_secret_name}. kubectl exited $LASTEXITCODE."; exit 1
}
Write-Host "[EKS] ${ecr_registry_secret_name} applied."
Write-Host "[EKS] Setup complete."