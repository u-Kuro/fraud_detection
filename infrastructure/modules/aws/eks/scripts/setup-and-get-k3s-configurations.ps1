Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$WarningPreference = $VerbosePreference = $DebugPreference = $InformationPreference = $ProgressPreference = "SilentlyContinue"

# Get inputs
$query = $Input | Out-String | ConvertFrom-Json
$main_network_name                  = $query.main_network_name
$main_network_gateway               = $query.main_network_gateway
$eks_cluster_endpoint               = $query.eks_cluster_endpoint
$k3s_registries_file_path           = $query.k3s_registries_file_path
$kubeconfig_for_localhost_file_path = $query.kubeconfig_for_localhost_file_path
$kubeconfig_for_docker_file_path    = $query.kubeconfig_for_docker_file_path

# Validate inputs values
$items = @{
    main_network_name                  = $main_network_name
    main_network_gateway               = $main_network_gateway
    k3s_container_url                  = $eks_cluster_endpoint
    k3s_registries_file_path           = $k3s_registries_file_path
    kubeconfig_for_localhost_file_path = $kubeconfig_for_localhost_file_path
    kubeconfig_for_docker_file_path    = $kubeconfig_for_docker_file_path
}.GetEnumerator()
foreach ($item in $items) {
    if ([string]::IsNullOrWhiteSpace($item.Value)) {
        throw "$($item.Name): must be a non-empty string."
    }
}

# Get main network configurations
$main_network_json_configurations = (docker inspect $main_network_name | ConvertFrom-Json)[0]
$main_network_containers          = $main_network_json_configurations.Containers

# Get EKS given port
$eks_endpoint_uri              = ([System.UriBuilder]$eks_cluster_endpoint)
$is_eks_endpoint_for_localhost = $eks_endpoint_uri.Host -in "localhost", "127.0.0.1", "::1", "0.0.0.0"

# Find K3s container configurations that EKS spawned through MiniStack
$k3s_container_port      = $null
$k3s_container_host_port = $null
$k3s_container_name = $null
if ($is_eks_endpoint_for_localhost) {
    $k3s_container_host_port = $eks_endpoint_uri.Port
    foreach ($container in $main_network_containers.PSObject.Properties.Value) {
        $container_json_configurations = (docker inspect $container.Name | ConvertFrom-Json)[0]
        $container_network_settings    = $container_json_configurations.NetworkSettings
        $container_ports               = $container_network_settings.Ports
        $container_tcp                 = $container_ports[0].PSObject.Properties.Name
        $container_host_port           = $container_ports.$container_tcp[0].HostPort
        if ([int]$container_host_port -eq [int]$k3s_container_host_port) {
            $k3s_container_name = $container.Name
            $k3s_container_port = ($container_tcp -split "/")[0]
            break
        }
    }
} else {
    $k3s_container_port = $eks_endpoint_uri.Port
    foreach ($container in $main_network_containers.PSObject.Properties.Value) {
        $container_json_configurations = (docker inspect $container.Name | ConvertFrom-Json)[0]
        $container_network_settings    = $container_json_configurations.NetworkSettings
        $container_ports               = $container_network_settings.Ports
        $container_tcp                 = $container_ports[0].PSObject.Properties.Name
        $container_port                = ($container_tcp -split "/")[0]
        if ([int]$container_port -eq [int]$k3s_container_port) {
            $k3s_container_name      = $container.Name
            $k3s_container_host_port = $container_ports.$container_tcp[0].HostPort
            break
        }
    }
}
if (-not $k3s_container_name) {
    throw "No K3s container with port '$k3s_container_port' found in the network '$main_network_name'."
}

# Check K3s container ports
if (-not $k3s_container_host_port) {
    throw "No Host Port found for K3s container '$k3s_container_name'."
}
if (-not $k3s_container_port) {
    throw "No Port found for K3s container '$k3s_container_name'."
}

# Get K3s container configurations
$k3s_container_json_configurations = (docker inspect $k3s_container_name | ConvertFrom-Json)[0]
$k3s_container_network_settings    = $k3s_container_json_configurations.NetworkSettings
$k3s_container_networks            = $k3s_container_network_settings.Networks

# Get K3s container ip
$k3s_container_ip = $k3s_container_networks.$main_network_name.IPAddress
if (-not $k3s_container_ip) {
    throw "No IP found for K3s container '$k3s_container_name' in network '$main_network_name'."
}

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
$null = docker cp `
    $k3s_registries_file_path `
    "${k3s_container_name}:${k3s_container_configuration_files_directory_path}/registries.yaml"

# Restart K3s container to apply registries.yaml
$null = docker restart $k3s_container_name

# Wait until it restarts successfully
$env:KUBECONFIG = $kubeconfig_for_localhost_file_path
$max_wait = 300; $elapsed = 0;
do {
    Start-Sleep -Seconds 5
    $elapsed += 5
    kubectl get nodes --request-timeout=5s *> $null
} until ($LASTEXITCODE -eq 0 -or $elapsed -ge $max_wait)

# Inform K3s status
if ($elapsed -ge $max_wait) {
    throw "K3s container did not recover after waiting ${max_wait}s."
}

# Wait until its safe for deployment
$null = kubectl wait --for=condition=Ready nodes --all --timeout=5m

Write-Output @{
    k3s_container_ip                   = $k3s_container_ip
    k3s_container_host_port            = [string]$k3s_container_host_port
    kubeconfig_for_localhost_file_path = $kubeconfig_for_localhost_file_path
    kubeconfig_for_docker_file_path    = $kubeconfig_for_docker_file_path
} | ConvertTo-Json -Compress