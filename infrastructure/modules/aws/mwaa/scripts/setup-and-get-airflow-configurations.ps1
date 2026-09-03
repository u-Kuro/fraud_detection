#requires -Version 7.4
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true
$ErrorActionPreference = "Stop"
$WarningPreference = $VerbosePreference = $DebugPreference = $InformationPreference = $ProgressPreference = "SilentlyContinue"

# Get inputs
$query = $Input | Out-String | ConvertFrom-Json
$main_network_name                       = $query.main_network_name
$airflow_container_url                   = $query.airflow_container_url
$airflow_requirements_file_path          = $query.airflow_requirements_file_path
$airflow_python_packages_constraint_url  = $query.airflow_python_packages_constraint_url
$kubeconfig_for_docker_file_path         = $query.kubeconfig_for_docker_file_path
$aws_configurations_for_docker_file_path = $query.aws_configurations_for_docker_file_path
$aws_credentials_for_docker_file_path    = $query.aws_credentials_for_docker_file_path

# Validate inputs values
$items = @{
    main_network_name                       = $main_network_name
    airflow_container_url                   = $airflow_container_url
    airflow_requirements_file_path          = $airflow_requirements_file_path
    airflow_python_packages_constraint_url  = $airflow_python_packages_constraint_url
    kubeconfig_for_docker_file_path         = $kubeconfig_for_docker_file_path
    aws_configurations_for_docker_file_path = $aws_configurations_for_docker_file_path
    aws_credentials_for_docker_file_path    = $aws_credentials_for_docker_file_path
}.GetEnumerator()
foreach ($item in $items) {
    if ([string]::IsNullOrWhiteSpace($item.Value)) {
        throw "$($item.Name): must be a non-empty string."
    }
}

# Get Airflow container IP
$airflow_container_ip = ([System.UriBuilder]$airflow_container_url).Host

# Get main network configurations
$main_network_json_configurations = (docker inspect $main_network_name | ConvertFrom-Json)[0]
$main_network_containers          = $main_network_json_configurations.Containers

# Get Airflow container name using its IP in MiniStack network
$airflow_container_name = $null
foreach ($container in $main_network_containers.PSObject.Properties.Value) {
    if ($container.IPv4Address -like "$airflow_container_ip/*") {
        $airflow_container_name = $container.Name
        break
    }
}
if (-not $airflow_container_name) {
    throw "No container with IP '$airflow_container_ip' found in network '$main_network_name'."
}

# Get Airflow container configurations
$airflow_container_json_configurations = (docker inspect $airflow_container_name | ConvertFrom-Json)[0]
$airflow_container_network_settings    = $airflow_container_json_configurations.NetworkSettings
$airflow_container_ports               = $airflow_container_network_settings.Ports
$airflow_container_persisted_directory = "/opt/airflow"
$airflow_container_dag_directory_path  = "$airflow_container_persisted_directory/dags"

# Install additional package and dependencies in Airflow container
$airflow_container_requirements_file_path = "${airflow_container_persisted_directory}/requirements.txt"
$null = docker exec $airflow_container_name mkdir -p $airflow_container_persisted_directory
$null = docker cp $airflow_requirements_file_path "${airflow_container_name}:${airflow_container_requirements_file_path}"
$null = docker exec $airflow_container_name sh -c "pip install -r $airflow_container_requirements_file_path --constraint '$airflow_python_packages_constraint_url' -qq"

# Copy kubeconfig to Airflow container for K3s access
$airflow_container_kubeconfig_file_path = "${airflow_container_persisted_directory}/kubeconfig.yaml"
$null = docker exec $airflow_container_name mkdir -p $airflow_container_persisted_directory
$null = docker cp $kubeconfig_for_docker_file_path "${airflow_container_name}:${airflow_container_kubeconfig_file_path}"

# Set Airflow container AWS paths
$airflow_user_home_aws_directory_path      = "/home/airflow/.aws"
$airflow_container_aws_configurations_path = "${airflow_user_home_aws_directory_path}/config"
$airflow_container_aws_credentials_path    = "${airflow_user_home_aws_directory_path}/credentials"

# Initialize AWS config/credentials for Airflow's secrets backend (secrets manager)
$null = docker exec $airflow_container_name mkdir -p $airflow_user_home_aws_directory_path
$null = docker cp $aws_configurations_for_docker_file_path "${airflow_container_name}:${airflow_container_aws_configurations_path}"
$null = docker cp $aws_credentials_for_docker_file_path "${airflow_container_name}:${airflow_container_aws_credentials_path}"

# Get Airflow container host port
$airflow_container_host_port = $airflow_container_ports[0].PSobject.Properties.Value[0].HostPort
if (-not $airflow_container_host_port) {
    throw "'$airflow_container_name' port has invalid value of '$airflow_container_host_port'."
}

Write-Output @{
    airflow_container_name                 = $airflow_container_name
    airflow_container_host_port            = [string]$airflow_container_host_port
    airflow_container_dag_directory_path   = $airflow_container_dag_directory_path
    airflow_container_kubeconfig_file_path = $airflow_container_kubeconfig_file_path
} | ConvertTo-Json -Compress