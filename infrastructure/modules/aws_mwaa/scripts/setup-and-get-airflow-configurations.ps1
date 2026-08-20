# TODO - 19/08/2026 - Continue here...
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

docker exec ministack-mwaa-test sh -c @'
mkdir -p ~/.aws && cat > ~/.aws/config << EOF
[default]
region = us-east-1
endpoint_url = http://ministack:4566
request_checksum_calculation = when_required
EOF
'@

docker exec ministack-mwaa-test sh -c @'
mkdir -p ~/.aws && cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = test
aws_secret_access_key = test
EOF
'@

# docker cp [local_files_kubeconfig_container_file_path] <airflow_container>:/usr/local/airflow/dags/[s3_kubeconfig_file_path_for_mwaa]
# manually too
#
#But try to put in /opt/airflow for Persistence in current setup

# Get inputs
$query = $Input | Out-String | ConvertFrom-Json
$airflow_container_url  = $query.airflow_container_url
$ministack_network_name = $query.ministack_network_name

# Validate inputs values
$items = @{
    ministack_network_name = $ministack_network_name
    airflow_container_url  = $airflow_container_url
}.GetEnumerator()
foreach ($item in $items) {
    if ([string]::IsNullOrWhiteSpace($item.Value)) {
        throw "$($item.Name): must be a non-empty string."
    }
}

# Get Airflow container host port
$airflow_container_ip = ([System.UriBuilder]$airflow_container_url).Host

# Get Ministack network configurations
$ministack_network_json_configurations = (docker inspect $ministack_network_name | ConvertFrom-Json)[0]
$ministack_network_containers          = $ministack_network_json_configurations.Containers

# Get Airflow container name using its IP in Ministack network
$airflow_container_name = $null
foreach ($container in $ministack_network_containers.PSObject.Properties.Value) {
    if ($container.IPv4Address -like "$airflow_container_ip/*") {
        $airflow_container_name = $container.Name
        break
    }
}
if (-not $airflow_container_name) {
    throw "No container with IP '$airflow_container_ip' found in network '$ministack_network_name'."
}

# Get Postgres container configurations
$postgres_container_json_configurations = (docker inspect $postgres_container_name | ConvertFrom-Json)[0]
$postgres_container_network_settings    = $postgres_container_json_configurations.NetworkSettings
$postgres_container_ports               = $postgres_container_network_settings.Ports

# Get Postgres container host port
$postgres_container_host_port = $postgres_container_ports[0].PSobject.Properties.Value[0].HostPort
if (-not $postgres_container_host_port) {
    throw "'$postgres_container_name' port has invalid value of '$postgres_container_host_port'."
}

@{
    postgres_container_host_port = $postgres_container_host_port
} | ConvertTo-Json -Compress