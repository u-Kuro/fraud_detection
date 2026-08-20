# TODO - 20/08/2026 - Continue here...
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


# need to also add requirements.txt to /opt/airflow then pip install it there
docker cp ./infrastructure/local_files/requirements.txt ministack-mwaa-test:/opt/airflow/requirements.txt
docker exec ministack-mwaa-test sh -c "pip install -r /opt/airflow/requirements.txt --constraint 'https://raw.githubusercontent.com/apache/airflow/constraints-3.0.6/constraints-3.12.txt' 2>&1"
# need to also add kubeconfig.yaml to /opt/airflow (different than mwaa but this directory persists in ministack)
docker cp ./infrastructure/local_files/kubeconfig.yaml ministack-mwaa-test:/opt/airflow/kubeconfig.yaml

docker exec ministack-mwaa-test sh -c "airflow dags reserialize 2>/dev/null" # read immed
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