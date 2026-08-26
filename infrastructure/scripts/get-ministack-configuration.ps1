Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Get Ministack container name
$ministack_container_name = docker ps --filter "ancestor=ministackorg/ministack" --format '{{.Names}}' | Select-Object -First 1
if (-not $ministack_container_name) {
    throw "Ministack is not running."
}

# Get Ministack container configurations
$ministack_container_json_configurations = (docker inspect $ministack_container_name | ConvertFrom-Json)[0]
$ministack_container_environments        = ($ministack_container_json_configurations.Config.Env -join "`n") | ConvertFrom-StringData
$ministack_container_network_settings    = $ministack_container_json_configurations.NetworkSettings
$ministack_container_networks            = $ministack_container_network_settings.Networks
$ministack_container_ports               = $ministack_container_network_settings.Ports

# Check container environments for used network for Ministack's AWS services
$DOCKER_NETWORK = 'DOCKER_NETWORK'
if (-not $ministack_container_environments.ContainsKey($DOCKER_NETWORK)) {
    throw "'$ministack_container_name' container environments does not contain '$DOCKER_NETWORK'."
}

# Get used Ministack network
$ministack_network_name = $ministack_container_environments.$DOCKER_NETWORK
if (-not $ministack_network_name) {
    throw "'$ministack_container_name' container environment '$DOCKER_NETWORK' has invalid value of '$ministack_network_name'."
}

# Check Ministack container's network connection
if (-not $ministack_container_networks.PSObject.Properties[$ministack_network_name]) {
    throw "Container '$ministack_container_name' has '$DOCKER_NETWORK' set to '$ministack_network_name' but is no longer connected."
}

# Get Ministack network gateway
$ministack_network_gateway = $ministack_container_networks.$ministack_network_name.Gateway
if (-not $ministack_network_gateway) {
    throw "'$ministack_network_name' gateway has invalid value of '$ministack_network_gateway'."
}

# Get Ministack container ip
$ministack_container_ip = $ministack_container_networks.$ministack_network_name.IPAddress
if (-not $ministack_container_ip) {
    throw "'$ministack_container_name' IP has invalid value of '$ministack_container_ip'."
}

# Get Ministack container port
$ministack_container_port = ($ministack_container_ports[0].PSObject.Properties.Name -split "/")[0]

# Get Ministack container host port
$ministack_container_host_port = $ministack_container_ports[0].PSobject.Properties.Value[0].HostPort
if (-not $ministack_container_host_port) {
    throw "'$ministack_container_name' port has invalid value of '$ministack_container_host_port'."
}

@{
    ministack_container_name      = $ministack_container_name
    ministack_network_name        = $ministack_network_name
    ministack_network_gateway     = $ministack_network_gateway
    ministack_container_ip        = $ministack_container_ip
    ministack_container_port      = $ministack_container_port
    ministack_container_host_port = $ministack_container_host_port
    ministack_host_url            = "http://127.0.0.1:${ministack_container_host_port}"
    ministack_url                 = "http://${ministack_container_name}:${ministack_container_port}"
    ministack_endpoint            = "${ministack_container_name}:${ministack_container_port}"
} | ConvertTo-Json -Compress