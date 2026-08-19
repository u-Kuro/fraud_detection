Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Set default credentials
aws configure set aws_access_key_id     $Env:AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $Env:AWS_SECRET_ACCESS_KEY

# Set default configurations
aws configure set region                       $Env:AWS_DEFAULT_REGION
aws configure set endpoint_url                 $Env:AWS_ENDPOINT_URL
aws configure set request_checksum_calculation "when_required"