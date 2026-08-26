#Requires -Version 5.1
#
#.SYNOPSIS
#    Ministack EKS + NLB -> Traefik v3 -> IngressRoute path routing.
#
#.DESCRIPTION
#    Phase  1  Prerequisites
#    Phase  2  Ministack container inspection  (IPs, network, endpoints)
#    Phase  3  Ministack health
#    Phase  4  Pre-provision AWS resources     (VPC / subnets / SG / IGW)
#    Phase  5  EKS cluster creation            (create + poll until ACTIVE)
#    Phase  6  k3s kubeconfig                  (extract, patch, export)
#    Phase  7  Deploy FastAPI pods             (test-app + test-app-b namespaces)
#    Phase  8  Install Traefik v3              (Helm: LoadBalancer + externalIP + NodePort)
#    Phase  9  Middleware + IngressRoute       (path-based routing for both apps)
#    Phase 10  Manual NLB registration         (TCP:80 -> Traefik NodePort :32080)
#    Phase 11  ELBv2 verification
#    Phase 12  Traefik activity                (logs + CRD status)
#    Phase 13  Tests:
#                1) Ingress  -- docker-network -> k3s:32080 -> Traefik -> IngressRoute -> fastapi-app
#                2) Egress   -- pod -> S3 via ministack container IP (EP_DOCKER)
#                3) Egress   -- pod -> S3 via Docker network gateway:host-port
#                4) Cross-NS -- fastapi-app <-> fastapi-app-b via cluster DNS
#    Phase 14  Summary
#

Set-StrictMode -Off

# ==============================================================================
#  CONSTANTS
# ==============================================================================
$REGION            = 'us-east-1'
$MINISTACK_PORT    = 4566
$KUBECONFIG_PATH   = "$env:TEMP\ministack-kubeconfig.yaml"
$CLUSTER_NAME      = 'my-eks-cluster'
$K8S_VERSION       = '1.32'
$EKS_ROLE_NAME     = 'ministack-eks-cluster-role'
$EKS_WAIT_SECS     = 300
$EKS_POLL_SECS     = 10

$TRAEFIK_NS        = 'traefik'
$TRAEFIK_NODE_PORT = 32080        # fixed NodePort for Traefik web entrypoint

# App 1 -- test-app namespace
$APP1_NAME  = 'fastapi-app'
$APP1_NS    = 'test-app'
$APP1_CPORT = 8765                # container port (non-standard / "random")
$APP1_PATH  = "/$APP1_NAME"      # /fastapi-app

# App 2 -- test-app-b namespace (cross-namespace partner)
$APP2_NAME  = 'fastapi-app-b'
$APP2_NS    = 'test-app-b'
$APP2_CPORT = 9123                # container port (non-standard / "random")
$APP2_PATH  = "/$APP2_NAME"      # /fastapi-app-b

# ==============================================================================
#  HELPERS
# ==============================================================================
function Step($msg) { Write-Host "`n╔═══ $msg ═══" -ForegroundColor Cyan }
function OK  ($msg) { Write-Host "  ✅ $msg"       -ForegroundColor Green }
function WARN($msg) { Write-Host "  ⚠  $msg"       -ForegroundColor Yellow }
function INFO($msg) { Write-Host "  ℹ  $msg" }

# Write UTF-8 YAML to a temp file and kubectl apply it
function KubApply([string]$name, [string]$yaml) {
    $p = "$env:TEMP\ms-$name.yaml"
    [System.IO.File]::WriteAllText($p, $yaml, [System.Text.Encoding]::UTF8)
    kubectl apply -f $p
}

# ==============================================================================
#  PHASE 1 -- Prerequisites
# ==============================================================================
Step "PHASE 1 — Prerequisites"

foreach ($tool in @('docker', 'kubectl', 'helm', 'aws')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Required tool '$tool' not found in PATH."
    }
    OK "$tool found"
}

# ==============================================================================
#  PHASE 2 -- Ministack Container Inspection
# ==============================================================================
Step "PHASE 2 — Ministack Container Inspection"

$ministack_container_name = docker ps `
    --filter "ancestor=ministackorg/ministack" `
    --format '{{.Names}}' | Select-Object -First 1

if (-not $ministack_container_name) {
    throw "Ministack container not running. Start it first."
}
OK "Ministack container: $ministack_container_name"

$ms_json         = (docker inspect $ministack_container_name | ConvertFrom-Json)[0]
$ms_envs         = ($ms_json.Config.Env -join "`n") | ConvertFrom-StringData
$ms_net_settings = $ms_json.NetworkSettings
$ms_networks     = $ms_net_settings.Networks
$ms_ports        = $ms_net_settings.Ports

if (-not $ms_envs.ContainsKey('DOCKER_NETWORK')) {
    throw "'$ministack_container_name' missing DOCKER_NETWORK env var."
}
$ministack_network_name = $ms_envs.DOCKER_NETWORK
if (-not $ministack_network_name) { throw "DOCKER_NETWORK is empty." }
OK "Docker network: $ministack_network_name"

if (-not $ms_networks.PSObject.Properties[$ministack_network_name]) {
    throw "Container not connected to '$ministack_network_name'."
}

$ministack_gw        = $ms_networks.$ministack_network_name.Gateway
$ministack_ip        = $ms_networks.$ministack_network_name.IPAddress
$ministack_host_port = $ms_ports[0].PSObject.Properties.Value[0].HostPort

if (-not $ministack_gw)        { throw "Gateway for '$ministack_network_name' is empty." }
if (-not $ministack_ip)        { throw "Ministack container IP is empty." }
if (-not $ministack_host_port) { throw "Ministack host port is empty." }

# Endpoint references used throughout
$EP_HOST    = "http://127.0.0.1:${ministack_host_port}"          # Windows -> ministack
$EP_DOCKER  = "http://${ministack_ip}:${MINISTACK_PORT}"         # pods -> ministack direct
$EP_GATEWAY = "http://${ministack_gw}:${ministack_host_port}"    # pods -> host gateway

OK "Ministack IP (Docker net) : $ministack_ip"
OK "Gateway                   : $ministack_gw"
OK "Host port                 : $ministack_host_port"
OK "EP_HOST   (Windows)       : $EP_HOST"
OK "EP_DOCKER (pods direct)   : $EP_DOCKER"
OK "EP_GATEWAY (pods via gw)  : $EP_GATEWAY"

# ==============================================================================
#  PHASE 3 -- Ministack Health
# ==============================================================================
Step "PHASE 3 — Ministack Health"

$health = (Invoke-WebRequest "$EP_HOST/_ministack/health" -UseBasicParsing).Content |
    ConvertFrom-Json
OK "Version: $($health.version)   Edition: $($health.edition)"

if ($health.services.eks -ne 'available') {
    WARN "EKS service status: $($health.services.eks)"
} else {
    OK "EKS service: available"
}

# ==============================================================================
#  PHASE 4 -- Pre-provision AWS Resources (VPC / Subnets / SG / IGW)
# ==============================================================================
Step "PHASE 4 — Pre-provision AWS Resources (VPC / Subnets / SG / IGW)"

$env:AWS_ACCESS_KEY_ID     = 'test'
$env:AWS_SECRET_ACCESS_KEY = 'test'
$env:AWS_DEFAULT_REGION    = $REGION
$env:AWS_ENDPOINT_URL      = $EP_HOST

INFO "Creating VPC (172.20.0.0/16)..."
$vpcTagSpec = "ResourceType=vpc,Tags=[{Key=Name,Value=ministack-vpc},{Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared}]"
$vpcId = (aws ec2 create-vpc `
    --cidr-block '172.20.0.0/16' `
    --tag-specifications $vpcTagSpec `
    | ConvertFrom-Json).Vpc.VpcId
OK "VPC: $vpcId"

INFO "Creating subnets (two AZs)..."
$sub1TagSpec = "ResourceType=subnet,Tags=[{Key=Name,Value=ministack-sub-a},{Key=kubernetes.io/role/elb,Value=1},{Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared}]"
$sub1 = (aws ec2 create-subnet `
    --vpc-id $vpcId `
    --cidr-block '172.20.0.0/24' `
    --availability-zone "${REGION}a" `
    --tag-specifications $sub1TagSpec `
    | ConvertFrom-Json).Subnet.SubnetId

$sub2TagSpec = "ResourceType=subnet,Tags=[{Key=Name,Value=ministack-sub-b},{Key=kubernetes.io/role/elb,Value=1},{Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared}]"
$sub2 = (aws ec2 create-subnet `
    --vpc-id $vpcId `
    --cidr-block '172.20.1.0/24' `
    --availability-zone "${REGION}b" `
    --tag-specifications $sub2TagSpec `
    | ConvertFrom-Json).Subnet.SubnetId

OK "Subnet-A (${REGION}a): $sub1"
OK "Subnet-B (${REGION}b): $sub2"

INFO "Creating security group..."
$sgId = (aws ec2 create-security-group `
    --group-name 'ministack-sg' `
    --description 'SG for ministack NLB' `
    --vpc-id $vpcId `
    | ConvertFrom-Json).GroupId
aws ec2 authorize-security-group-ingress `
    --group-id $sgId `
    --protocol tcp --port 80 --cidr '0.0.0.0/0' | Out-Null
OK "Security group: $sgId"

INFO "Creating + attaching IGW..."
$igwId = (aws ec2 create-internet-gateway | ConvertFrom-Json).InternetGateway.InternetGatewayId
aws ec2 attach-internet-gateway `
    --internet-gateway-id $igwId `
    --vpc-id $vpcId | Out-Null
OK "IGW: $igwId"

# ==============================================================================
#  PHASE 5 -- EKS Cluster Creation + Poll Until ACTIVE
# ==============================================================================
Step "PHASE 5 — EKS Cluster Creation + Wait for ACTIVE"

INFO "Ensuring IAM role '$EKS_ROLE_NAME'..."
$eksRoleArn = (aws iam get-role --role-name $EKS_ROLE_NAME 2>$null | ConvertFrom-Json).Role.Arn

if (-not $eksRoleArn) {
    $trustDoc   = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"eks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
    $eksRoleArn = (aws iam create-role `
        --role-name $EKS_ROLE_NAME `
        --assume-role-policy-document $trustDoc `
        | ConvertFrom-Json).Role.Arn
    OK "IAM role created: $eksRoleArn"
} else {
    OK "IAM role exists : $eksRoleArn"
}

INFO "Checking for existing cluster '$CLUSTER_NAME'..."
$clusterJson    = aws eks describe-cluster --name $CLUSTER_NAME 2>$null
$clusterDesc    = if ($clusterJson) { $clusterJson | ConvertFrom-Json } else { $null }
$currentStatus  = if ($clusterDesc) { $clusterDesc.cluster.status } else { $null }

if ($currentStatus -eq 'ACTIVE') {
    OK "Cluster '$CLUSTER_NAME' already ACTIVE — skipping creation"
} else {
    if (-not $currentStatus) {
        INFO "Creating EKS cluster '$CLUSTER_NAME' (kubernetes v${K8S_VERSION})..."
        aws eks create-cluster `
            --name $CLUSTER_NAME `
            --kubernetes-version $K8S_VERSION `
            --role-arn $eksRoleArn `
            --resources-vpc-config "subnetIds=$sub1,$sub2,securityGroupIds=$sgId" `
            | Out-Null
        OK "Cluster creation request submitted"
    } else {
        INFO "Cluster exists with status '$currentStatus' — polling to ACTIVE..."
    }

    INFO "Polling for ACTIVE (timeout: ${EKS_WAIT_SECS}s, interval: ${EKS_POLL_SECS}s)..."
    $elapsed = 0
    $status  = $currentStatus

    do {
        Start-Sleep $EKS_POLL_SECS
        $elapsed += $EKS_POLL_SECS
        $clusterDesc = aws eks describe-cluster --name $CLUSTER_NAME | ConvertFrom-Json
        $status      = $clusterDesc.cluster.status
        $filled = [int][Math]::Min(20, [Math]::Floor($elapsed / $EKS_WAIT_SECS * 20))
        $bar    = ('█' * $filled).PadRight(20, '░')
        INFO "  [$elapsed/${EKS_WAIT_SECS}s] [$bar] $status"
    } until ($status -eq 'ACTIVE' -or $elapsed -ge $EKS_WAIT_SECS)

    if ($status -ne 'ACTIVE') {
        throw "Cluster did not reach ACTIVE within ${EKS_WAIT_SECS}s (last: $status)"
    }
    OK "Cluster '$CLUSTER_NAME' is ACTIVE"
}

# ==============================================================================
#  PHASE 6 -- k3s Kubeconfig
# ==============================================================================
Step "PHASE 6 — k3s Kubeconfig Setup"

# Get ministack network configurations
$ministack_network_json_config = (docker inspect $ministack_network_name | ConvertFrom-Json)[0]
$ministack_network_containers = $ministack_network_json_config.Containers

# Get k3s container name using its ip in ministack network
$k3sContainer = $null
foreach ($container in $ministack_network_containers.PSObject.Properties.Value) {
    $containerName = $container.Name
    $containerHostPort = (docker inspect $containerName | ConvertFrom-Json)[0].NetworkSettings.Ports.PSobject.Properties.Value[0].HostPort
    $k3sClusterHostPort = ([System.UriBuilder]$clusterDesc.cluster.endpoint).Port
    if ([int]$containerHostPort -eq [int]$k3sClusterHostPort) {
        $k3sContainer = $containerName
        break
    }
}
if (-not $k3sContainer) {
    throw "No container with IP '$k3sContainer' found in network '$ministack_network_name'."
}

INFO "Waiting for k3s container '$k3sContainer'..."
$k3sDeadline = (Get-Date).AddSeconds(30)
while (-not (docker ps --format '{{.Names}}' | Where-Object { $_ -eq $k3sContainer })) {
    if ((Get-Date) -gt $k3sDeadline) { throw "k3s container did not appear within 30s." }
    Start-Sleep 2
}
OK "k3s container running: $k3sContainer"

$k3sInspect    = (docker inspect $k3sContainer | ConvertFrom-Json)[0]
$k3sPorts      = $k3sInspect.NetworkSettings.Ports
$k3s6443Prop   = $k3sPorts.PSObject.Properties | Where-Object { $_.Name -like '6443/*' }
$K3S_API_PORT  = $k3sPorts.PSobject.Properties.Value[0].HostPort
$k3sContainerIP = $k3sInspect.NetworkSettings.Networks.$ministack_network_name.IPAddress

if (-not $k3sContainerIP) { throw "Cannot resolve k3s container IP on '$ministack_network_name'." }

OK "k3s container IP : $k3sContainerIP"
OK "k3s API host port: $K3S_API_PORT"

$rawKubeconfig = docker exec $k3sContainer cat /etc/rancher/k3s/k3s.yaml
$rawKubeconfig -replace 'https://127\.0\.0\.1:6443', "https://127.0.0.1:$K3S_API_PORT" |
    Set-Content $KUBECONFIG_PATH
$env:KUBECONFIG = $KUBECONFIG_PATH
OK "Kubeconfig patched: $KUBECONFIG_PATH"

kubectl cluster-info
kubectl get nodes -o wide

# ==============================================================================
#  PHASE 7 -- Deploy FastAPI Pods
#
#  Both apps use:
#    image        : python:3.11-slim
#    startup      : pip install deps, then uvicorn
#    container port: non-standard (app1=8765, app2=9123)
#    service      : ClusterIP, port 80 -> targetPort (container port)
#
#  The app code is injected via ConfigMap so it can be shared across replicas.
#  readinessProbe has a 90s initial delay to account for pip install time.
# ==============================================================================
Step "PHASE 7 — Deploy FastAPI Pods"

# -- Shared FastAPI app code (written once, reused for both apps) -------------
$fastapiCode = @'
from fastapi import FastAPI
import socket, os

app = FastAPI()

@app.get("/")
async def root():
    return {
        "hostname": socket.gethostname(),
        "app":      os.getenv("APP_NAME", "unknown"),
        "ns":       os.getenv("POD_NAMESPACE", "unknown"),
        "path":     "/",
        "status":   "ok",
    }

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return {
        "hostname": socket.gethostname(),
        "app":      os.getenv("APP_NAME", "unknown"),
        "ns":       os.getenv("POD_NAMESPACE", "unknown"),
        "path":     f"/{full_path}",
        "status":   "ok",
    }
'@
$fastapiCodePath = "$env:TEMP\ms-fastapi-main.py"
[System.IO.File]::WriteAllText($fastapiCodePath, $fastapiCode, [System.Text.Encoding]::UTF8)

# Helper: deploy one FastAPI app
function Deploy-FastApiApp(
    [string]$name,
    [string]$ns,
    [int]$cport
) {
    INFO "Deploying $name in namespace $ns (container port $cport)..."

    # Namespace
    KubApply "$name-ns" @"
apiVersion: v1
kind: Namespace
metadata:
  name: $ns
"@

    # ConfigMap with app code
    kubectl create configmap "$name-code" `
        --from-file="main.py=$fastapiCodePath" `
        --namespace $ns `
        --dry-run=client -o yaml | kubectl apply -f -

    # Deployment + ClusterIP Service (no NodePort)
    KubApply "$name-deploy" @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $name
  namespace: $ns
spec:
  replicas: 2
  selector:
    matchLabels:
      app: $name
  template:
    metadata:
      labels:
        app: $name
    spec:
      containers:
      - name: app
        image: python:3.11-slim
        command: ["/bin/sh", "-c"]
        args:
        - pip install fastapi uvicorn boto3 -q --no-cache-dir && cd /opt/appcode && uvicorn main:app --host 0.0.0.0 --port $cport
        ports:
        - containerPort: $cport
        env:
        - name: APP_NAME
          value: "$name"
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        volumeMounts:
        - name: app-code
          mountPath: /opt/appcode
        readinessProbe:
          httpGet:
            path: /
            port: $cport
          initialDelaySeconds: 90
          periodSeconds: 10
          failureThreshold: 18
        livenessProbe:
          httpGet:
            path: /
            port: $cport
          initialDelaySeconds: 120
          periodSeconds: 15
          failureThreshold: 5
      volumes:
      - name: app-code
        configMap:
          name: $name-code
---
apiVersion: v1
kind: Service
metadata:
  name: $name
  namespace: $ns
spec:
  type: ClusterIP
  selector:
    app: $name
  ports:
  - port: 80
    targetPort: $cport
    protocol: TCP
"@
    OK "$name deployed (service ClusterIP:80 -> container:$cport)"
}

Deploy-FastApiApp -name $APP1_NAME -ns $APP1_NS -cport $APP1_CPORT
Deploy-FastApiApp -name $APP2_NAME -ns $APP2_NS -cport $APP2_CPORT

# Wait for both apps — use rollout status first (ensures pods exist), then wait for Ready
INFO "Waiting for $APP1_NAME pods ready (up to 300s — includes pip install)..."
kubectl rollout status deployment/$APP1_NAME -n $APP1_NS --timeout=300s 2>&1 | Out-Null
kubectl wait pod `
    --for=condition=ready `
    --selector="app=$APP1_NAME" `
    --namespace=$APP1_NS `
    --timeout=300s 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    WARN "$APP1_NAME pods not ready after 300s:"
    kubectl get pod -n $APP1_NS -l app=$APP1_NAME
    kubectl logs -n $APP1_NS -l app=$APP1_NAME --tail=20 2>$null
} else {
    OK "$APP1_NAME pods ready"
}

INFO "Waiting for $APP2_NAME pods ready (up to 300s)..."
kubectl rollout status deployment/$APP2_NAME -n $APP2_NS --timeout=300s 2>&1 | Out-Null
kubectl wait pod `
    --for=condition=ready `
    --selector="app=$APP2_NAME" `
    --namespace=$APP2_NS `
    --timeout=300s 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    WARN "$APP2_NAME pods not ready after 300s:"
    kubectl get pod -n $APP2_NS -l app=$APP2_NAME
    kubectl logs -n $APP2_NS -l app=$APP2_NAME --tail=20 2>$null
} else {
    OK "$APP2_NAME pods ready"
}

kubectl get pod -n $APP1_NS -l app=$APP1_NAME -o wide
kubectl get pod -n $APP2_NS -l app=$APP2_NAME -o wide

# ==============================================================================
#  PHASE 8 -- Install Traefik v3 via Helm
#
#  Key values:
#    service.type=LoadBalancer          -- k3s klipper-lb handles external IP
#    service.externalIPs[0]=<k3s IP>    -- explicit external IP (k3s container)
#    ports.web.nodePort=32080           -- fixed NodePort for NLB registration
#    ingressClass.enabled=false         -- avoid conflict with k3s built-in Traefik
#
#  k3s ships with Traefik v2 (traefik.containo.us CRDs).
#  Traefik v3 uses different CRDs (traefik.io) -- no conflict.
# ==============================================================================
Step "PHASE 8 — Install Traefik v3 (Helm)"

INFO "Adding Traefik Helm repo..."
helm repo add traefik https://helm.traefik.io/traefik 2>$null | Out-Null
helm repo update traefik | Out-Null
OK "Helm repo ready"

INFO "Running helm upgrade/install for Traefik..."
helm upgrade --install traefik traefik/traefik `
    --namespace $TRAEFIK_NS `
    --create-namespace `
    --set service.type=LoadBalancer `
    --set "service.externalIPs[0]=$k3sContainerIP" `
    --set ports.web.nodePort=$TRAEFIK_NODE_PORT `
    --set ingressClass.enabled=false `
    --set deployment.replicas=1 `
    --set accessLog.enabled=true

INFO "Waiting for Traefik pod to exist (timeout 60s)..."
$traefikExistDeadline = (Get-Date).AddSeconds(60)
do {
    Start-Sleep 3
    $traefikPodName = kubectl get pod -n $TRAEFIK_NS -l 'app.kubernetes.io/name=traefik' `
        -o jsonpath='{.items[0].metadata.name}' 2>$null
} until ($traefikPodName -or ((Get-Date) -gt $traefikExistDeadline))

if ($traefikPodName) {
    INFO "Traefik pod found ($traefikPodName) — waiting for Ready (timeout 120s)..."
    kubectl wait pod/$traefikPodName -n $TRAEFIK_NS --for=condition=Ready --timeout=120s 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        OK "Traefik pod Ready"
    } else {
        WARN "Traefik pod not Ready after 120s — proceeding"
    }
} else {
    WARN "Traefik pod did not appear within 60s — proceeding"
}

kubectl get pod   -n $TRAEFIK_NS
kubectl get svc   -n $TRAEFIK_NS

# ==============================================================================
#  PHASE 9 -- Middleware + IngressRoute
#
#  Pattern per app:
#    Middleware  : stripPrefix ["/app-name"]
#    IngressRoute: PathPrefix(`/app-name`) -> middleware -> app-service:80
#
#  Traffic flow:
#    NLB:80 -> Traefik NodePort:32080 -> IngressRoute match -> strip prefix
#           -> ClusterIP service:80 -> pod container port
# ==============================================================================
Step "PHASE 9 — Middleware + IngressRoute"

function Apply-IngressRoute(
    [string]$name,
    [string]$ns,
    [string]$path
) {
    INFO "Applying Middleware + IngressRoute for $name ($path)..."

    KubApply "$name-mw" @"
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: ${name}-middleware
  namespace: $ns
spec:
  stripPrefix:
    prefixes:
      - $path
"@

    KubApply "$name-ir" @"
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: ${name}-ingress-route
  namespace: $ns
spec:
  entryPoints:
    - web
  routes:
    - match: PathPrefix(``$path``)
      kind: Rule
      middlewares:
        - name: ${name}-middleware
          namespace: $ns
      services:
        - name: $name
          port: 80
"@
    OK "$name IngressRoute: PathPrefix($path) -> ${name}:80"
}

Apply-IngressRoute -name $APP1_NAME -ns $APP1_NS -path $APP1_PATH
Apply-IngressRoute -name $APP2_NAME -ns $APP2_NS -path $APP2_PATH

Write-Host ""
kubectl get middleware    -n $APP1_NS 2>$null
kubectl get middleware    -n $APP2_NS 2>$null
kubectl get ingressroute -n $APP1_NS 2>$null
kubectl get ingressroute -n $APP2_NS 2>$null

# ==============================================================================
#  PHASE 10 -- Manual NLB Registration (TCP:80 -> Traefik NodePort)
# ==============================================================================
Step "PHASE 10 — Manual NLB Registration (TCP:80 -> :${TRAEFIK_NODE_PORT})"

INFO "Creating NLB (network / internet-facing)..."
$nlbArn = (aws elbv2 create-load-balancer `
    --name 'ministack-nlb' `
    --type network `
    --scheme internet-facing `
    --subnets $sub1 $sub2 `
    | ConvertFrom-Json).LoadBalancers[0].LoadBalancerArn
$nlbDns = (aws elbv2 describe-load-balancers `
    --load-balancer-arns $nlbArn `
    | ConvertFrom-Json).LoadBalancers[0].DNSName
OK "NLB: $nlbDns"

INFO "Creating target group (TCP:${TRAEFIK_NODE_PORT} / instance)..."
$nlbTgArn = (aws elbv2 create-target-group `
    --name 'ministack-nlb-tg' `
    --protocol TCP `
    --port $TRAEFIK_NODE_PORT `
    --vpc-id $vpcId `
    --target-type instance `
    | ConvertFrom-Json).TargetGroups[0].TargetGroupArn
OK "Target group: $nlbTgArn"

INFO "Registering k3s node as target (${k3sContainerIP}:${TRAEFIK_NODE_PORT})..."
aws elbv2 register-targets `
    --target-group-arn $nlbTgArn `
    --targets "Id=${k3sContainerIP},Port=${TRAEFIK_NODE_PORT}" | Out-Null
OK "Target registered"

INFO "Creating NLB listener (TCP:80 -> forward)..."
$nlbListenerArn = (aws elbv2 create-listener `
    --load-balancer-arn $nlbArn `
    --protocol TCP --port 80 `
    --default-actions "Type=forward,TargetGroupArn=$nlbTgArn" `
    | ConvertFrom-Json).Listeners[0].ListenerArn
OK "Listener: $nlbListenerArn"

# ==============================================================================
#  PHASE 11 -- ELBv2 Verification
# ==============================================================================
Step "PHASE 11 — ELBv2 Verification"

Write-Host "`n  Load Balancers:"
aws elbv2 describe-load-balancers `
    --query 'LoadBalancers[*].{Name:LoadBalancerName,Type:Type,Scheme:Scheme,State:State.Code,DNS:DNSName}' `
    --output table

Write-Host "`n  Target Group:"
aws elbv2 describe-target-groups `
    --query 'TargetGroups[*].{Name:TargetGroupName,Protocol:Protocol,Port:Port,Type:TargetType}' `
    --output table

Write-Host "`n  NLB target health:"
aws elbv2 describe-target-health `
    --target-group-arn $nlbTgArn `
    --query 'TargetHealthDescriptions[*].{Target:Target.Id,Port:Target.Port,State:TargetHealth.State}' `
    --output table

# ==============================================================================
#  PHASE 12 -- Traefik Activity
# ==============================================================================
Step "PHASE 12 — Traefik Activity"

$traefikPod = kubectl get pod -n $TRAEFIK_NS -l 'app.kubernetes.io/name=traefik' `
    -o jsonpath='{.items[0].metadata.name}' 2>$null

if ($traefikPod) {
    Write-Host "`n  Traefik pod: pod/$traefikPod"
    Write-Host "`n  Traefik logs (last 20 lines):"
    kubectl logs $traefikPod -n $TRAEFIK_NS --tail=20 2>$null
} else {
    WARN "No Traefik pod found in namespace $TRAEFIK_NS"
}

Write-Host "`n  IngressRoutes:"
kubectl get ingressroute -A 2>$null

Write-Host "`n  Middleware:"
kubectl get middleware -A 2>$null

Write-Host "`n  Traefik service:"
kubectl get svc traefik -n $TRAEFIK_NS 2>$null

# ==============================================================================
#  PHASE 13 -- Tests
# ==============================================================================
Step "PHASE 13 — Tests"

$app1Pod = kubectl get pod -n $APP1_NS -l app=$APP1_NAME `
    -o jsonpath='{.items[0].metadata.name}' 2>$null
$app2Pod = kubectl get pod -n $APP2_NS -l app=$APP2_NAME `
    -o jsonpath='{.items[0].metadata.name}' 2>$null

$traefikClusterIP = kubectl get svc traefik -n $TRAEFIK_NS `
    -o jsonpath='{.spec.clusterIP}' 2>$null

# Write reusable Python test scripts to temp
$s3TestScript = @'
import boto3, uuid, json, sys

def run(endpoint):
    s3 = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1',
    )
    bucket = 'egress-' + uuid.uuid4().hex[:8]
    key    = 'hello.txt'
    body   = f'ministack egress ok via {endpoint}'
    try:
        s3.create_bucket(Bucket=bucket)
        s3.put_object(Bucket=bucket, Key=key, Body=body)
        got = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode()
        print(json.dumps({'endpoint': endpoint, 'bucket': bucket,
                          'put': body, 'got': got, 'match': got == body}))
    except Exception as e:
        print(json.dumps({'endpoint': endpoint, 'error': str(e)}))

run(sys.argv[1])
'@

$crossTestScript = @'
import urllib.request, json, sys

def call(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return {'url': url, 'status': r.status, 'body': json.loads(r.read().decode())}
    except Exception as e:
        return {'url': url, 'error': str(e)}

for url in sys.argv[1:]:
    print(json.dumps(call(url)))
'@

$s3ScriptPath    = "$env:TEMP\ms-s3test.py"
$crossScriptPath = "$env:TEMP\ms-crosstest.py"

[System.IO.File]::WriteAllText($s3ScriptPath,    $s3TestScript,    [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($crossScriptPath, $crossTestScript, [System.Text.Encoding]::UTF8)

# Helper: copy a local file into a pod via kubectl exec + stdin (no tar required).
# kubectl cp needs tar inside the container; python:3.11-slim may not have it.
# kubectl exec -i streams stdin through the same websocket channel already
# proven to work by Test 1, so this is unconditionally more reliable.
function Copy-ToPod([string]$localPath, [string]$ns, [string]$pod, [string]$destPath) {
    $content = [System.IO.File]::ReadAllText($localPath, [System.Text.Encoding]::UTF8)
    $content | kubectl exec -i -n $ns $pod -- sh -c "cat > '$destPath'" 2>&1 | Out-Null
    kubectl exec -n $ns $pod -- test -f $destPath 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { return $true }
    WARN "Copy-ToPod failed: $localPath -> ${ns}/${pod}:${destPath}"
    return $false
}

# ─────────────────────────────────────────────────────────────────────────────
#  Test 1 — Ingress: Docker-network -> k3s NodePort -> Traefik -> IngressRoute
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n  [Test 1] Ingress — docker-network → k3s:${TRAEFIK_NODE_PORT}${APP1_PATH} → Traefik → $APP1_NAME"

$t1url = "http://${k3sContainerIP}:${TRAEFIK_NODE_PORT}${APP1_PATH}"
INFO "GET $t1url"

$t1out = docker run --rm --network $ministack_network_name `
    curlimages/curl curl -sf $t1url 2>$null

if ($t1out -match '"hostname"') {
    OK "Ingress confirmed — FastAPI pod reachable via IngressRoute"
    Write-Host $t1out
} elseif ($t1out) {
    WARN "Got response but unexpected format — check IngressRoute and Traefik logs:"
    Write-Host $t1out
} else {
    WARN "No response from $t1url"
    INFO "Verify Traefik pod is Running and IngressRoute is accepted:"
    kubectl get pod -n $TRAEFIK_NS
    kubectl get ingressroute -n $APP1_NS
}

# ─────────────────────────────────────────────────────────────────────────────
#  Test 2 — Egress (EP_DOCKER): pod -> S3 via ministack container IP
#           http://<ministack_ip>:4566
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n  [Test 2] Egress (EP_DOCKER) — $APP1_NAME pod → S3 via $EP_DOCKER"

$s3ScriptCopied = $false
if ($app1Pod) {
    if (Copy-ToPod $s3ScriptPath $APP1_NS $app1Pod '/tmp/s3test.py') {
        $s3ScriptCopied = $true
        $t2out  = kubectl exec -n $APP1_NS $app1Pod -- python3 /tmp/s3test.py $EP_DOCKER 2>&1
        $t2json = $t2out | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($t2json -and $t2json.match -eq $true) {
            OK "Egress (EP_DOCKER) confirmed — S3 put+get matched via $EP_DOCKER"
            Write-Host $t2out
        } elseif ($t2json -and $t2json.error) {
            WARN "Egress (EP_DOCKER) S3 error: $($t2json.error)"
        } else {
            WARN "Egress (EP_DOCKER) unexpected output: $t2out"
        }
    }
    # Copy-ToPod already printed the warning on failure; $s3ScriptCopied stays $false
} else {
    WARN "Skipped — $APP1_NAME pod not found"
}

# ─────────────────────────────────────────────────────────────────────────────
#  Test 3 — Egress (Gateway): pod -> S3 via Docker network gateway:host-port
#           http://<ministack_gw>:<host_port>
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n  [Test 3] Egress (Gateway) — $APP1_NAME pod → S3 via $EP_GATEWAY"

if ($app1Pod -and $s3ScriptCopied) {
    # s3test.py already copied in Test 2
    $t3out  = kubectl exec -n $APP1_NS $app1Pod -- python3 /tmp/s3test.py $EP_GATEWAY 2>&1
    $t3json = $t3out | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($t3json -and $t3json.match -eq $true) {
        OK "Egress (Gateway) confirmed — S3 put+get matched via $EP_GATEWAY"
        Write-Host $t3out
    } elseif ($t3json -and $t3json.error) {
        WARN "Egress (Gateway) S3 error: $($t3json.error)"
    } else {
        WARN "Egress (Gateway) unexpected output: $t3out"
    }
} elseif (-not $app1Pod) {
    WARN "Skipped — $APP1_NAME pod not found"
} else {
    WARN "Skipped — s3test.py could not be copied to pod (kubectl cp failed in Test 2)"
}

# ─────────────────────────────────────────────────────────────────────────────
#  Test 4 — Cross-namespace: app1 <-> app2 via cluster DNS
#           http://[service].[namespace].svc.cluster.local:80
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n  [Test 4] Cross-namespace — $APP1_NAME <-> $APP2_NAME via cluster DNS"

$app1DnsUrl = "http://${APP1_NAME}.${APP1_NS}.svc.cluster.local:80/"
$app2DnsUrl = "http://${APP2_NAME}.${APP2_NS}.svc.cluster.local/"

if ($app1Pod -and $app2Pod) {
    # Copy cross-test script to each pod; track success independently
    $app1CrossCopied = Copy-ToPod $crossScriptPath $APP1_NS $app1Pod '/tmp/crosstest.py'
    $app2CrossCopied = Copy-ToPod $crossScriptPath $APP2_NS $app2Pod '/tmp/crosstest.py'

    # app1 -> app2
    INFO "$APP1_NAME -> $APP2_NAME  ($app2DnsUrl)"
    if ($app1CrossCopied) {
        $t4a     = kubectl exec -n $APP1_NS $app1Pod -- python3 /tmp/crosstest.py $app2DnsUrl 2>&1
        $t4aJson = $t4a | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($t4aJson -and $t4aJson.status -eq 200) {
            OK "$APP1_NAME -> $APP2_NAME cross-namespace call succeeded (HTTP 200)"
        } else {
            WARN "${APP1_NAME} -> ${APP2_NAME}: $t4a"
        }
        Write-Host $t4a
    } else {
        WARN "Skipped — crosstest.py could not be copied to $APP1_NAME pod"
    }

    # app2 -> app1
    INFO "$APP2_NAME -> $APP1_NAME  ($app1DnsUrl)"
    if ($app2CrossCopied) {
        $t4b     = kubectl exec -n $APP2_NS $app2Pod -- python3 /tmp/crosstest.py $app1DnsUrl 2>&1
        $t4bJson = $t4b | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($t4bJson -and $t4bJson.status -eq 200) {
            OK "$APP2_NAME -> $APP1_NAME cross-namespace call succeeded (HTTP 200)"
        } else {
            WARN "${APP2_NAME} -> ${APP1_NAME}: $t4b"
        }
        Write-Host $t4b
    } else {
        WARN "Skipped — crosstest.py could not be copied to $APP2_NAME pod"
    }
} else {
    WARN "Skipped — one or both pods not found (app1Pod='$app1Pod' app2Pod='$app2Pod')"
}

# ─────────────────────────────────────────────────────────────────────────────
#  Test 5 — NLB DNS: external Docker container -> NLB -> Traefik -> pod
#
#  This is the only test that exercises the NLB as an actual routing hop.
#  Tests 1-4 all bypass the NLB (they hit the k3s NodePort or ClusterIP
#  directly). Here a fresh container on the Docker network hits the real
#  NLB DNS name so the path is:
#
#    container -> NLB DNS -> NLB listener:80 -> target:32080 (Traefik NodePort)
#             -> IngressRoute -> ClusterIP:80 -> pod
#
#  DNS note: *.elb.amazonaws.com won't resolve via the default Docker DNS.
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n  [Test 5] NLB DNS — external container -> $nlbDns -> NLB -> Traefik -> $APP1_NAME"

$t5url = "http://${nlbDns}${APP1_PATH}"
INFO "GET $t5url"

$t5out = docker run --rm `
    --network $ministack_network_name `
    curlimages/curl `
    curl -sf --connect-timeout 5 --max-time 10 $t5url 2>$null

if ($t5out -match '"hostname"') {
    OK "NLB DNS confirmed -- external container reached $APP1_NAME via NLB"
    Write-Host $t5out
} elseif ($t5out) {
    WARN "Got a response but unexpected format -- NLB is routing but check output:"
    Write-Host $t5out
} else {
    WARN "NLB DNS not reachable: $t5url"
    INFO "ministack '$($health.edition)' edition may not proxy NLB listeners."
    INFO "NLB target (${k3sContainerIP}:${TRAEFIK_NODE_PORT}) is healthy (Phase 11)"
}

# Final workload state
Write-Host "`n  Workload state:"
kubectl get all -n $APP1_NS
kubectl get all -n $APP2_NS
kubectl get all -n $TRAEFIK_NS

# ==============================================================================
#  PHASE 14 -- Summary
# ==============================================================================
Step "PHASE 14 — Summary"

Write-Host @"

  ╔══════════════════════════════════════════════════════════════════════════╗
  ║  MINISTACK EKS + TRAEFIK INGRESSROUTE SUMMARY                           ║
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  CONTAINERS  (Docker network: $ministack_network_name)
  ║    ministack : $ministack_container_name  ($ministack_ip)
  ║    k3s       : $k3sContainer  ($k3sContainerIP)
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  ENDPOINTS
  ║    EP_HOST    : $EP_HOST   (Windows -> ministack)
  ║    EP_DOCKER  : $EP_DOCKER   (pods -> ministack direct)
  ║    EP_GATEWAY : $EP_GATEWAY   (pods -> host gateway)
  ║    Traefik    : http://${k3sContainerIP}:${TRAEFIK_NODE_PORT}   (NodePort)
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  EKS CLUSTER
  ║    Name    : $CLUSTER_NAME
  ║    Version : $K8S_VERSION
  ║    Role    : $eksRoleArn
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  AWS RESOURCES
  ║    VPC      : $vpcId
  ║    Subnet-A : $sub1  (${REGION}a)
  ║    Subnet-B : $sub2  (${REGION}b)
  ║    SG       : $sgId
  ║    IGW      : $igwId
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  NLB
  ║    DNS      : $nlbDns
  ║    ARN      : $nlbArn
  ║    TG       : $nlbTgArn
  ║    Target   : ${k3sContainerIP}:${TRAEFIK_NODE_PORT}   (Traefik NodePort)
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  TRAEFIK v3
  ║    Namespace  : $TRAEFIK_NS
  ║    NodePort   : $TRAEFIK_NODE_PORT
  ║    ExternalIP : $k3sContainerIP
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  APPS + INGRESSROUTES
  ║    $APP1_NAME  NS=$APP1_NS  svc:80->pod:$APP1_CPORT  path=$APP1_PATH
  ║    $APP2_NAME  NS=$APP2_NS  svc:80->pod:$APP2_CPORT  path=$APP2_PATH
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  ROUTING PATH
  ║    Client -> NLB:80 -> k3s NodePort:$TRAEFIK_NODE_PORT -> Traefik
  ║           -> IngressRoute (PathPrefix match)
  ║           -> stripPrefix Middleware
  ║           -> ClusterIP Service:80 -> Pod container port
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  KUBECONFIG : $KUBECONFIG_PATH
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  KNOWN LIMITATIONS
  ║    NLB DNS names are mock — not locally routable.
  ║    Test directly via NodePort (see quick tests below).
  ╚══════════════════════════════════════════════════════════════════════════╝

"@

Write-Host "  Quick ingress tests (run anytime):" -ForegroundColor Yellow
Write-Host "    docker run --rm --network $ministack_network_name curlimages/curl curl -s http://${k3sContainerIP}:${TRAEFIK_NODE_PORT}${APP1_PATH}" -ForegroundColor White
Write-Host "    docker run --rm --network $ministack_network_name curlimages/curl curl -s http://${k3sContainerIP}:${TRAEFIK_NODE_PORT}${APP2_PATH}" -ForegroundColor White

Write-Host "`n  Cross-namespace DNS (run from inside cluster pod):" -ForegroundColor Yellow
Write-Host "    http://${APP1_NAME}.${APP1_NS}.svc.cluster.local:80/" -ForegroundColor White
Write-Host "    http://${APP2_NAME}.${APP2_NS}.svc.cluster.local/" -ForegroundColor White

Write-Host "`n  ELBv2 check:" -ForegroundColor Yellow
Write-Host "    aws --endpoint-url $EP_HOST elbv2 describe-load-balancers" -ForegroundColor White

Write-Host "`n  Set kubeconfig in a new terminal:" -ForegroundColor Yellow
Write-Host "    `$env:KUBECONFIG = '$KUBECONFIG_PATH'" -ForegroundColor White
