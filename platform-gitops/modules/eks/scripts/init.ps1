param(
    [Parameter(Mandatory)][string]$cluster_name,
    [Parameter(Mandatory)][string]$kubeconfig_host_directory_path,
    [Parameter(Mandatory)][string]$k3s_mount_directory_path,
    [Parameter(Mandatory)][string]$kubeconfig_mount_file_name
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Wait for cluster to be active
Write-Host "`n[EKS] Waiting for cluster '$cluster_name' to become ACTIVE..."
$max_wait = 120; $waited = 0
do {
    Start-Sleep -Seconds 5; $waited += 5
    $status = aws --endpoint-url http://localhost:4566 eks describe-cluster `
                --name "$cluster_name" `
                --query "cluster.status" `
                --output text 2>$null
    Write-Host "[EKS] Status: $status (${waited}s elapsed)"
} while ($status -ne "ACTIVE" -and $waited -lt $max_wait)

if ($status -ne "ACTIVE") {
    Write-Error "[EKS] Cluster did not become ACTIVE within ${max_wait}s."; exit 1
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
$host_port  = $port_line -replace '.*:', ''
Write-Host "[EKS] k3s API host port: $host_port"

# Copy eks container's kubeconfig.yaml to host
New-Item -ItemType Directory -Force -Path "$kubeconfig_host_directory_path" | Out-Null
$kubeconfig_path = Join-Path "$kubeconfig_host_directory_path" "$kubeconfig_mount_file_name"

docker exec $eks_container_name cat "$k3s_mount_directory_path/$kubeconfig_mount_file_name" | Out-File $kubeconfig_path -Encoding utf8

# Replace Docker-internal 127.0.0.1:6443 with the actual host port.
(Get-Content $kubeconfig_path) `
    -replace "https://127\.0\.0\.1:$default_k3s_port", "https://127.0.0.1:$host_port" |
    Set-Content $kubeconfig_path

Write-Host "[EKS] Kubeconfig written: $kubeconfig_path"

# Set containerd to pull from MiniStack ECR
# k3s uses containerd, not Docker daemon. docker login has no effect on k3s.
# registries.yaml tells containerd where to find the MiniStack ECR mirror.
$registries_yaml = @"
mirrors:
  "localhost:4566":
    endpoint:
      - "http://ministack:4566"
configs:
  "ministack:4566":
    auth:
      username: AWS
      password: test
"@

$temp_registries = Join-Path $env:TEMP "ministack-registries.yaml"
$registries_yaml | Set-Content $temp_registries -Encoding utf8

docker cp $temp_registries "${eks_container_name}:$k3s_mount_directory_path/registries.yaml"
docker exec $eks_container_name kill -HUP 1 # SIGHUP reloads containerd config
Write-Host "[EKS] containerd registry configured. Waiting for reload..."
Start-Sleep -Seconds 3

# Create ECR imagePullSecret in k3s
$env:KUBECONFIG = $kubeconfig_path

kubectl create secret docker-registry ecr-secret `
    --docker-server=localhost:4566 `
    --docker-username=AWS `
    --docker-password=test `
    --dry-run=client -o yaml | kubectl apply -f -

Write-Host "[EKS] ecr-secret applied."
Write-Host "[EKS] Setup complete."