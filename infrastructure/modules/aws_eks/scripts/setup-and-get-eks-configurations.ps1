Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Get inputs
$query = $Input | Out-String | ConvertFrom-Json
$eks_cluster_host_url               = $query.eks_cluster_host_url
$ministack_network_name             = $query.ministack_network_name
$kubeconfig_for_localhost_file_path = $query.kubeconfig_for_localhost_file_path
$kubeconfig_for_docker_file_path    = $query.kubeconfig_for_docker_file_path
$registries_file_path               = $query.registries_file_path

# Validate inputs values
$items = @{
    eks_cluster_host_url               = $eks_cluster_host_url
    ministack_network_name             = $ministack_network_name
    kubeconfig_for_localhost_file_path = $kubeconfig_for_localhost_file_path
    kubeconfig_for_docker_file_path    = $kubeconfig_for_docker_file_path
    registries_file_path               = $registries_file_path
}.GetEnumerator()
foreach ($item in $items) {
    if ([string]::IsNullOrWhiteSpace($item.Value)) {
        throw "$($item.Name): must be a non-empty string."
    }
}

# Get EKS cluster configurations
$eks_cluster_host_port = ([System.UriBuilder]$eks_cluster_host_url).Port

# Get Ministack network configurations
$ministack_network_json_configurations = (docker inspect $ministack_network_name | ConvertFrom-Json)[0]
$ministack_network_containers          = $ministack_network_json_configurations.Containers

# Find K3s container that EKS spawned through Ministack
$k3s_container_name = $null
foreach ($container in $ministack_network_containers.PSObject.Properties.Value) {
    $container_host_port = (docker inspect $container.Name | ConvertFrom-Json)[0].NetworkSettings.Ports.PSobject.Properties.Value[0].HostPort
    if ([int]$container_host_port -eq [int]$eks_cluster_host_port) {
        $k3s_container_name = $container.Name
        break
    }
}
if (-not $k3s_container_name) {
    throw "No K3s container with port '$eks_cluster_host_port' found in the network '$ministack_network_name'."
}

# Get K3s container configurations
$k3s_container_json_configurations = (docker inspect $k3s_container_name | ConvertFrom-Json)[0]
$k3s_container_ports               = $k3s_container_json_configurations.NetworkSettings.Ports

# Get K3s container ports
$k3s_container_port      = ($k3s_container_ports.PSobject.Properties.Name -split "/")[0]
$k3s_container_host_port = $eks_cluster_host_port

# Define configuration files directory path in K3s container
$k3s_container_configuration_files_directory_path = "/etc/rancher/k3s"

# Get raw kubeconfig file in K3s container
$raw_kubeconfig = docker exec $k3s_container_name cat "${k3s_container_configuration_files_directory_path}/k3s.yaml"

# Write kubeconfig for localhost in defined file
$raw_kubeconfig -replace `
    "https://127\.0\.0\.1:${k3s_container_port}", `
    "https://127.0.0.1:${k3s_container_host_port}" `
    | Out-File $kubeconfig_for_localhost_file_path -Encoding utf8

# Write kubeconfig for docker in defined file
$raw_kubeconfig -replace `
    "https://127\.0\.0\.1:${k3s_container_port}", `
    "https://${k3s_container_name}:${k3s_container_port}" `
    | Out-File $kubeconfig_for_docker_file_path -Encoding utf8

# Copy registries.yaml into K3s container to redirect requests to ECR
docker cp `
    $registries_file_path `
    "${k3s_container_name}:${k3s_container_configuration_files_directory_path}/registries.yaml"

# Restart K3s container to apply registries.yaml
Write-Host "[EKS] Configurations applied, waiting for K3s container to recover after restart..."
docker restart $k3s_container_name

# Wait until it restarts successfully
$env:KUBECONFIG = $kubeconfig_for_localhost_file_path
$max_wait = 120; $elapsed = 0;
do {
    Start-Sleep -Seconds 5
    $elapsed += 5
    try { kubectl get nodes --request-timeout=5s 2>&1 | Out-Null } catch {}
    Write-Host "[EKS] Still waiting... | ${elapsed}s"
} until ($LASTEXITCODE -eq 0 -or $elapsed -ge $max_wait)

# Inform K3s status
if ($elapsed -ge $max_wait) {
    Write-Error "[EKS] K3s container did not recover after waiting ${max_wait}s."
    exit 1
} else {
    Write-Host "[EKS] K3s is ready."
}