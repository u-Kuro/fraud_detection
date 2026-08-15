Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Get ministack container name
$ministack_container_name = docker ps --filter "ancestor=ministackorg/ministack" --format '{{.Names}}' | Select-Object -First 1
if (-not $ministack_container_name) {
    throw "Ministack is not running."
}

# Get network used in ministack
$ministack_network_name = docker inspect $ministack_container_name --format '{{range .Config.Env}}{{println .}}{{end}}' |
    Where-Object { $_ -match '^DOCKER_NETWORK=' } |
    ForEach-Object { $_.Split('=', 2)[1] }
if (-not $ministack_network_name) {
    $ministack_network_name = docker inspect $ministack_container_name --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}'
}
if (-not $ministack_network_name) {
    throw "'$ministack_container_name' container does not have a network."
}

# Get gateway IP
$gateway_ip = docker network inspect $ministack_network_name --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}'
if (-not $gateway_ip) {
    throw "Could not get gateway IP for '$ministack_network_name'."
}

# Get ministack container IP
$container_ip = docker inspect $ministack_container_name --format "{{(index .NetworkSettings.Networks `"$ministack_network_name`").IPAddress}}"
if (-not $container_ip) {
    throw "Could not get container IP for '$ministack_container_name'."
}

# Get gateway port
$port = docker inspect $ministack_container_name --format '{{range .Config.Env}}{{println .}}{{end}}' |
    Where-Object { $_ -match '^GATEWAY_PORT=' } |
    ForEach-Object { $_.Split('=', 2)[1] }
if (-not $port) {
    $port = docker inspect $ministack_container_name --format '{{range $k, $v := .NetworkSettings.Ports}}{{range $v}}{{.HostPort}}{{end}}{{end}}'
}
if (-not $port) {
    throw "Could not get port for '$ministack_container_name'."
}

# Get rds host port
$rds_host_port = docker inspect $ministack_container_name --format '{{range .Config.Env}}{{println .}}{{end}}' |
    Where-Object { $_ -match '^RDS_BASE_PORT=' } |
    ForEach-Object { $_.Split('=', 2)[1] }

@{
    ministack_container_name = $ministack_container_name
    ministack_network_name   = $ministack_network_name
    gateway_ip               = $gateway_ip
    container_ip             = $container_ip
    port                     = $port
    rds_host_port            = $rds_host_port
} | ConvertTo-Json -Compress