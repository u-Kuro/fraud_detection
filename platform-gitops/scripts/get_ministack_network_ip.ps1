Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ip = docker inspect ministack --format '{{.NetworkSettings.Networks.ministack_network.IPAddress}}'
@{ ip = $ip } | ConvertTo-Json -Compress