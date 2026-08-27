Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$WarningPreference = $VerbosePreference = $DebugPreference = $InformationPreference = $ProgressPreference = "SilentlyContinue"

# Get inputs
$query = $Input | Out-String | ConvertFrom-Json
$ministack_network_name = $query.ministack_network_name
$postgres_container_ip  = $query.postgres_container_ip

# Validate inputs values
$items = @{
    ministack_network_name = $ministack_network_name
    postgres_container_ip  = $postgres_container_ip
}.GetEnumerator()
foreach ($item in $items) {
    if ([string]::IsNullOrWhiteSpace($item.Value)) {
        throw "$($item.Name): must be a non-empty string."
    }
}

# Get Ministack network configurations
$ministack_network_json_configurations = (docker inspect $ministack_network_name | ConvertFrom-Json)[0]
$ministack_network_containers          = $ministack_network_json_configurations.Containers

# Get Postgres container name using its IP in Ministack network
$postgres_container_name = $null
foreach ($container in $ministack_network_containers.PSObject.Properties.Value) {
    if ($container.IPv4Address -like "$postgres_container_ip/*") {
        $postgres_container_name = $container.Name
        break
    }
}
if (-not $postgres_container_name) {
    throw "No container with IP '$postgres_container_ip' found in network '$ministack_network_name'."
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

Write-Output @{
    postgres_container_host_port = $postgres_container_host_port
} | ConvertTo-Json -Compress