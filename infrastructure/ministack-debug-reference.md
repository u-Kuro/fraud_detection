# MiniStack Local AWS Debug Reference

> Debugged on Windows / PowerShell. Services tested: RDS (Postgres), EKS (k3s), MWAA (Airflow 2.8.1).
> Intended as a reference for future Terraform-based projects using MiniStack.

---

## Architecture — How MiniStack Sidecars Work

MiniStack does not emulate RDS, EKS, or MWAA in-process. It spins up **real Docker sidecar containers**:

| Service | Container image | Container name pattern |
|---|---|---|
| RDS | `postgres:15-alpine` (or mysql) | `ministack-rds-<identifier>` |
| EKS | `rancher/k3s:<version>` | `ministack-eks-<cluster-name>` |
| MWAA | `apache/airflow:<version>` | `ministack-mwaa-<env-name>` |

`DOCKER_NETWORK` is the critical env var that attaches all sidecars to the same Docker network as MiniStack. Without it, sidecars land on the default bridge and cannot reach MiniStack or each other.

---

## Network Reality

```
Docker network: ministack-test_default (172.20.0.x subnet)

ministack-test          → 172.20.0.2   MiniStack gateway
RDS/postgres container  → 172.20.0.3   joined via DOCKER_NETWORK
k3s container           → 172.20.0.4   joined via DOCKER_NETWORK
Airflow container       → 172.20.0.3:8080  joined via DOCKER_NETWORK
```

**Pods inside k3s are NOT on the Docker network.** They run on k3s's internal CNI (`10.42.x.x`) and route outward through the k3s container via NAT. They can still reach RDS/MiniStack but not directly on `172.20.0.x`.

**From the Windows host**, container IPs (`172.20.x.x`) are not directly reachable. Only host-mapped ports work.

---

## docker-compose Template

```yaml
services:
  ministack-test:
    image: ministackorg/ministack:latest
    container_name: ministack-test
    ports:
      - "4566:4566"
    environment:
      DOCKER_NETWORK: "ministack-test_default"
      PERSIST_STATE:  "0"
      LOG_LEVEL:      INFO
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    healthcheck:
      test: ["CMD","python","-c","import urllib.request; urllib.request.urlopen('http://localhost:4566/_ministack/health')"]
      interval: 5s
      timeout: 3s
      retries: 12
```

The network name must match `<project-name>_default` where project name is what you pass to `docker compose -p`.

---

## Issue 1 — RDS psql failed with `host.docker.internal`

**Error:**
```
connection to server at "host.docker.internal" (192.168.65.254), port 5432 failed: Connection refused
```

**Root cause:** The RDS postgres container port is not mapped to the host. It only listens on the Docker network. `host.docker.internal` resolves to the host machine, not to the container.

**Fix:** Run psql inside a container on the same Docker network, connecting via the container IP returned by `DescribeDBInstances`:

```powershell
$rds     = (aws --endpoint-url $ep --region $region rds describe-db-instances `
                --db-instance-identifier testdb-test | ConvertFrom-Json).DBInstances[0]
$rdsPort = $rds.Endpoint.Port
$rdsIP   = $rds.Endpoint.Address

docker run --rm --network $network -e PGPASSWORD="$dbpass" postgres:15-alpine `
    psql "postgresql://admin:${dbpass}@${rdsIP}:5432/testdb-test" `
    -c "SELECT current_database(), version();"
```

**How to confirm RDS is on the correct network:** `DescribeDBInstances` returns a `172.20.0.x` address (not `localhost`) only when `DOCKER_NETWORK` is set and the container joined the network.

---

## Issue 2 — kubectl failed: connection refused → then credentials error

Two separate failures happened across two attempts.

### Attempt 1 — Connection refused (`172.20.0.4:6443`)

`DescribeCluster` returns `https://localhost:16443` during CREATING but switches to `https://172.20.0.4:6443` (container IP) after going ACTIVE. That IP is unreachable from the Windows host.

**Fix:** Always hardcode `https://localhost:16443` in the kubeconfig. MiniStack always maps k3s port 6443 to host port **16443**.

### Attempt 2 — Credentials error (`server has asked for credentials`)

The kubeconfig used a made-up token (`ministack-dev-token-test`) which k3s rejected. k3s generates its own real CA cert and admin credentials — a fake token does not work.

**Fix:** Extract the real kubeconfig from inside the k3s container, then patch the server address:

```powershell
# First find the actual container name
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
# Pattern is: ministack-eks-<cluster-name>
# e.g. ministack-eks-cluster-test

$k3sContainer = "ministack-eks-cluster-test"
$rawKubeconfig = docker exec $k3sContainer cat /etc/rancher/k3s/k3s.yaml
$fixedKubeconfig = $rawKubeconfig -replace "https://127\.0\.0\.1:6443", "https://localhost:16443"
$fixedKubeconfig | Set-Content "$env:TEMP\ministack-kubeconfig-test.yaml"
$env:KUBECONFIG = "$env:TEMP\ministack-kubeconfig-test.yaml"
kubectl cluster-info
```

> Never use `$cl.endpoint` from `DescribeCluster` directly in kubeconfig. After ACTIVE it returns the container IP which is unreachable from the host. Always use `localhost:16443`.

---

## Issue 3 — S3 upload failed with CRC64NVME checksum error

**Error:**
```
An error occurred (InvalidRequest): Checksum algorithm not supported: CRC64NVME.
Supported: SHA256, SHA1, CRC32.
```

**Root cause:** AWS CLI v2 (recent versions) defaults to CRC64NVME checksum on `s3 cp`. MiniStack does not support this algorithm.

**Fix:** Set this env var before any S3 upload:

```powershell
$env:AWS_REQUEST_CHECKSUM_CALCULATION = "when_required"
aws --endpoint-url $ep s3 cp "$env:TEMP\myfile.py" s3://my-bucket/path/myfile.py
```

For Terraform, use `checksum_algorithm = "SHA256"` on the `aws_s3_object` resource, or set the env var in your shell before running `terraform apply`.

---

## Issue 4 — `mwaa create-environment` failed with JSON parsing errors

### Failure 1 — PowerShell strips double quotes from inline JSON

```
Error parsing parameter '--network-configuration': Invalid JSON
JSON received: {SubnetIds:[],SecurityGroupIds:[]}
```

PowerShell unquotes the JSON string when passing it to the AWS CLI, removing `"` from keys and values.

### Failure 2 — Empty arrays rejected by client-side validation

```
Invalid length for parameter NetworkConfiguration.SubnetIds, value: 0, valid min length: 2
Invalid length for parameter NetworkConfiguration.SecurityGroupIds, value: 0, valid min length: 1
```

The AWS CLI validates values client-side before sending. Empty arrays are rejected regardless of MiniStack.

**Fix:** Write JSON to a file with dummy values that satisfy validation:

```powershell
'{"SubnetIds":["subnet-00000001","subnet-00000002"],"SecurityGroupIds":["sg-00000001"]}' | Set-Content "$env:TEMP\netconfig-test.json"

aws --endpoint-url $ep --region $region mwaa create-environment `
    --name               env-test `
    --dag-s3-path        dags `
    --source-bucket-arn  "arn:aws:s3:::airflow-dags-test" `
    --execution-role-arn "arn:aws:iam::000000000000:role/mwaa-role-test" `
    --airflow-version    "2.8.1" `
    --network-configuration "file://$env:TEMP\netconfig-test.json"
```

For Terraform `aws_mwaa_environment`:

```hcl
network_configuration {
  subnet_ids         = ["subnet-00000001", "subnet-00000002"]
  security_group_ids = ["sg-00000001"]
}
```

---

## Issue 5 — `invoke-rest-api` returned 404

**Error:**
```json
{ "RestApiStatusCode": 404, "detail": "The requested URL was not found on the server." }
```

**Root cause:** MiniStack strips `/api/v1` from the path internally before proxying to Airflow. Passing the full Airflow REST path results in a 404 because MiniStack tries to route `/api/v1/dags/api/v1/dags`.

**Fix:** Use bare paths without the `/api/v1` prefix:

```powershell
# Wrong
aws ... mwaa invoke-rest-api --name env-test --method GET --path "/api/v1/dags"

# Correct
aws ... mwaa invoke-rest-api --name env-test --method GET --path "/dags"
```

---

## Issue 6 — Airflow scheduler unhealthy, DAG not visible via REST API

**What happened:** After MWAA reached AVAILABLE, `GET /api/v1/dags` returned `{"dags": [], "total_entries": 0}` even though the DAG file was in `/opt/airflow/dags/`.

**Diagnosis:**

```powershell
# Check health
docker exec ministack-mwaa-env-test curl -s http://localhost:8080/health
# scheduler.status was "unhealthy" with a stale heartbeat

# DAG visible via CLI (bypasses webserver)
docker exec ministack-mwaa-env-test airflow dags list
# Shows the DAG — meaning parsing worked but scheduler not serving it
```

**Fix:** Restart the Airflow container:

```powershell
docker restart ministack-mwaa-env-test
Start-Sleep 30
docker exec ministack-mwaa-env-test curl -s http://localhost:8080/health
# scheduler.status should now be "healthy"
```

> Restarting wipes in-memory state but the SQLite DB inside the container persists including DAG records. However user credentials may need to be recreated — see Issue 8.

---

## Issue 7 — S3 DAG sync does NOT work automatically

**What happened:** DAG uploaded to S3 never appeared in Airflow. The `/opt/airflow/dags/` folder inside the container was empty (or only had the file from a previous `docker cp`).

**Root cause:** MiniStack accepts the `dag-s3-path` and `source-bucket-arn` parameters in the MWAA API but the actual S3-to-container DAG sync is not implemented. The dags folder inside the container is not automatically populated from S3.

**Workaround:**

```powershell
# Copy DAG directly into the container after creation
docker cp "$env:TEMP\my_dag.py" ministack-mwaa-env-test:/opt/airflow/dags/my_dag.py

# Verify
docker exec ministack-mwaa-env-test ls /opt/airflow/dags

# Wait for scheduler to pick it up (DAG_DIR_LIST_INTERVAL=5s)
Start-Sleep 15
docker exec ministack-mwaa-env-test airflow dags list
```

For Terraform: use a `null_resource` with `local-exec` provisioner to run `docker cp` after the environment is created.

---

## Issue 8 — `invoke-rest-api` returned 401

**Error:**
```json
{ "RestApiStatusCode": 401, "title": "Unauthorized" }
```

**Root cause — three-way credential conflict:**

1. Airflow starts in standalone mode and auto-generates a **random password**, writing it to `standalone_admin_password.txt` inside the container (e.g. `gzRUECWh8BD88mKx`).
2. MiniStack **reads and caches** this file once at environment creation — this is the credential its proxy will use for all `invoke-rest-api` calls.
3. The container env var `_AIRFLOW_WWW_USER_PASSWORD=admin` then **overwrites the DB password hash** to `admin`, which differs from the standalone password MiniStack cached.

**Result:** MiniStack proxy authenticates with the random standalone password, but Airflow's DB has `admin` as the hash. Every API call through the proxy gets 401.

Direct curl with `admin:admin` works because it hits the DB hash directly. But the MiniStack proxy is using the standalone password it cached at boot.

**Fix:**

```powershell
# Get the password MiniStack captured at boot
$standalonePass = docker exec ministack-mwaa-env-test bash -c 'find / -name standalone_admin_password.txt 2>/dev/null | xargs cat'
Write-Host "Standalone password: $standalonePass"

# Delete existing admin (whose hash was overwritten by the env var)
docker exec ministack-mwaa-env-test airflow users delete --username admin

# Recreate with the standalone password so DB matches what MiniStack cached
docker exec ministack-mwaa-env-test airflow users create --username admin --password $standalonePass --firstname Admin --lastname User --role Admin --email admin@example.com

# Verify directly
docker exec ministack-mwaa-env-test curl -s -u "admin:$standalonePass" http://localhost:8080/api/v1/dags

# Verify through MiniStack proxy — should now return 200
aws --endpoint-url $ep --region $region mwaa invoke-rest-api --name env-test --method GET --path "/dags"
```

> **Key rule:** Never manually set a different password than what is in `standalone_admin_password.txt`. MiniStack caches that password at environment creation and always uses it for proxy auth. Every time you run `airflow users delete/create` with a different password, you re-introduce the mismatch.

> **Note on Airflow version:** MiniStack officially verifies MWAA auth against `apache/airflow:2.10.4` and `3.0.6`. Version `2.8.1` worked after applying this fix but is not in the officially verified set.

---

## Issue 9 — PowerShell mangles JSON in `docker exec curl` commands

**Error:**
```json
{ "status": 400, "title": "Bad Request", "detail": "Request body is not valid JSON" }
```

**Root cause:** PowerShell intercepts and transforms quote characters when passing strings through `docker exec`, mangling the JSON body before curl receives it. This affects any `docker exec ... curl ... -d '{...}'` pattern.

**Fix:** Use the Airflow CLI directly instead of curl for any write operation:

```powershell
# Unpause a DAG — instead of curl PATCH
docker exec ministack-mwaa-env-test airflow dags unpause my_dag_id

# Trigger a DAG run — instead of curl POST
docker exec ministack-mwaa-env-test airflow dags trigger my_dag_id

# Check run status
docker exec ministack-mwaa-env-test airflow dags list-runs -d my_dag_id
```

---

## Useful Debug Commands

```powershell
# List all running containers including sidecars
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# Check MiniStack health and all service statuses
Invoke-WebRequest "http://localhost:4566/_ministack/health" -UseBasicParsing

# Check Airflow health directly
docker exec ministack-mwaa-env-test curl -s http://localhost:8080/health

# Check Airflow env vars (find credentials, auth backend, etc.)
docker exec ministack-mwaa-env-test env

# List Airflow users
docker exec ministack-mwaa-env-test airflow users list

# Check DAG import errors
docker exec ministack-mwaa-env-test airflow dags list-import-errors

# List DAGs via CLI (bypasses webserver/scheduler state)
docker exec ministack-mwaa-env-test airflow dags list

# Check DAG runs
docker exec ministack-mwaa-env-test airflow dags list-runs -d my_dag_id

# Get standalone password MiniStack cached
docker exec ministack-mwaa-env-test bash -c 'find / -name standalone_admin_password.txt 2>/dev/null | xargs cat'

# Test Airflow REST API directly with credentials
docker exec ministack-mwaa-env-test curl -s -u "admin:$standalonePass" http://localhost:8080/api/v1/dags

# Check k3s kubeconfig path
docker exec ministack-eks-cluster-test cat /etc/rancher/k3s/k3s.yaml

# Reset MiniStack state without restart
Invoke-WebRequest "http://localhost:4566/_ministack/reset" -Method POST
```

---

## Final Working State Summary

| Component | Status | Details |
|---|---|---|
| MiniStack | ✅ | Port 4566, health 200 |
| RDS / Postgres | ✅ | `172.20.0.3:5432`, on Docker network |
| EKS / k3s | ✅ | `localhost:16443`, real kubeconfig from container |
| nginx pod | ✅ | `10.42.0.4` — k3s CNI, not Docker network |
| MWAA / Airflow | ✅ | `172.20.0.3:8080`, on Docker network |
| S3 → Airflow DAG sync | ❌ | Not implemented — use `docker cp` |
| `invoke-rest-api` | ✅ | Works after standalone password sync |

---

## Terraform Notes

**S3 object checksum:**
```hcl
resource "aws_s3_object" "dag" {
  bucket           = aws_s3_bucket.airflow_dags.id
  key              = "dags/my_dag.py"
  source           = "dags/my_dag.py"
  checksum_algorithm = "SHA256"  # avoid CRC64NVME which MiniStack doesn't support
}
```

**MWAA network configuration — dummy values required:**
```hcl
resource "aws_mwaa_environment" "this" {
  name              = "env-test"
  airflow_version   = "2.10.4"  # use 2.10.4+ for verified MiniStack support
  dag_s3_path       = "dags"
  source_bucket_arn = aws_s3_bucket.airflow_dags.arn
  execution_role_arn = "arn:aws:iam::000000000000:role/mwaa-role-test"

  network_configuration {
    subnet_ids         = ["subnet-00000001", "subnet-00000002"]  # dummy, MiniStack ignores
    security_group_ids = ["sg-00000001"]                          # dummy, MiniStack ignores
  }
}
```

**EKS kubeconfig — never use the Terraform output endpoint directly on the host:**
```hcl
# This endpoint from aws_eks_cluster.this.endpoint will be 172.20.0.x after ACTIVE
# That IP is unreachable from the host. Always use localhost:16443 for kubectl.
```

After `terraform apply` creates the EKS cluster, run this to get a working kubeconfig:
```powershell
$k3sContainer = docker ps --format "{{.Names}}" | Select-String "ministack-eks"
$rawKubeconfig = docker exec $k3sContainer cat /etc/rancher/k3s/k3s.yaml
($rawKubeconfig -replace "https://127\.0\.0\.1:6443", "https://localhost:16443") | Set-Content "$env:TEMP\kubeconfig.yaml"
$env:KUBECONFIG = "$env:TEMP\kubeconfig.yaml"
```

**DAG deployment — S3 alone is not enough:**
```hcl
# After aws_mwaa_environment is created, use null_resource to copy DAG into container
resource "null_resource" "copy_dag" {
  depends_on = [aws_mwaa_environment.this]

  provisioner "local-exec" {
    command = "docker cp dags/my_dag.py ministack-mwaa-${var.env_name}:/opt/airflow/dags/my_dag.py"
  }
}
```

**MWAA auth fix after apply:**
```powershell
# Run this after terraform apply once the MWAA environment is AVAILABLE
$standalonePass = docker exec ministack-mwaa-env-test bash -c 'find / -name standalone_admin_password.txt 2>/dev/null | xargs cat'
docker exec ministack-mwaa-env-test airflow users delete --username admin
docker exec ministack-mwaa-env-test airflow users create --username admin --password $standalonePass --firstname Admin --lastname User --role Admin --email admin@example.com
```
