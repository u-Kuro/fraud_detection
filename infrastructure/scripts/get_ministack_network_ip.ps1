Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$query = $Input | Out-String | ConvertFrom-Json

$ministack_container_name = $query.ministack_container_name
$ministack_network_name   = $query.ministack_network_name

foreach ($val in @{ container = $ministack_container_name; network = $ministack_network_name }.GetEnumerator()) {
    if ($val.Value -isnot [string] -or [string]::IsNullOrWhiteSpace($val.Value)) {
        throw "$($val.Key): must be a non-empty string."
    }
}

$ip = docker inspect "${ministack_container_name}" --format "{{.NetworkSettings.Networks.${ministack_network_name}.IPAddress}}"

if ([string]::IsNullOrWhiteSpace($ip) -or $ip -eq '<no value>') {
    throw "Got '$ip' from '${ministack_container_name}' on '${ministack_network_name}'."
}

@{ ip = $ip } | ConvertTo-Json -Compress