#Requires -Version 5.1
#
#.SYNOPSIS
#    Full ministack EKS + ALB/NLB + LBC setup — from zero to running nginx.
#
#.DESCRIPTION
#    Phase  1  Prerequisites check
#    Phase  2  Ministack container inspection  (IPs, network, endpoints)
#    Phase  3  Ministack health check
#    Phase  4  Pre-provision AWS resources     (VPC / subnets / SG / IGW)
#    Phase  5  EKS cluster creation            (create + poll until ACTIVE)
#    Phase  6  k3s kubeconfig                  (extract, patch, export)
#    Phase  7  Test workload                   (nginx + NodePort + NLB svc + ALB ingress)
#    Phase  8  cert-manager                    (LBC webhook TLS dependency)
#    Phase  9  AWS Load Balancer Controller    (Helm install)
#    Phase 10  Manual ELBv2 registration       (NLB + ALB targets in ministack)
#    Phase 11  ELBv2 verification              (describe + target health)
#    Phase 12  LBC activity check              (logs + k8s status)
#    Phase 13  Connectivity tests              (3-tier exec strategy + NAT path)
#    Phase 14  Summary
#

Set-StrictMode -Off

# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS — adjust to match your environment
# ═══════════════════════════════════════════════════════════════════════════════
$REGION          = 'us-east-1'
$MINISTACK_PORT  = 4566
$NODE_PORT       = 30080        # fixed NodePort for nginx direct-path tests
$APP_NS          = 'test-app'
$KUBECONFIG_PATH = "$env:TEMP\ministack-kubeconfig.yaml"
$LBC_VERSION     = '1.8.1'     # eks/aws-load-balancer-controller chart version
$CLUSTER_NAME    = 'my-eks-cluster'
$K8S_VERSION     = '1.32'
$EKS_ROLE_NAME   = 'ministack-eks-cluster-role'
$EKS_WAIT_SECS   = 300         # max seconds to wait for cluster ACTIVE
$EKS_POLL_SECS   = 10          # polling interval

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
function Step($msg) { Write-Host "`n╔═══ $msg ═══" -ForegroundColor Cyan }
function OK  ($msg) { Write-Host "  ✅ $msg"       -ForegroundColor Green }
function WARN($msg) { Write-Host "  ⚠  $msg"       -ForegroundColor Yellow }
function INFO($msg) { Write-Host "  ℹ  $msg" }

function KubApply([string]$name, [string]$yaml) {
    $path = "$env:TEMP\ms-$name.yaml"
    $yaml | Set-Content $path
    kubectl apply -f $path
}

# Extract HTTP status from wget -S stderr (e.g. "  HTTP/1.1 200 OK")
function Get-WgetStatus([string]$raw) {
    if ($raw -match 'HTTP/\S+\s+(\d+)') { return $Matches[1] }
    return $null
}

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — Prerequisites
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 1 — Prerequisites"

foreach ($tool in @('docker', 'kubectl', 'helm', 'aws')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Required tool '$tool' not found in PATH."
    }
    OK "$tool found"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 — Ministack Container Inspection
#
#  Resolves the Docker-network IP and host-mapped port of the ministack
#  container. These feed EP_HOST (Windows → ministack) and EP_DOCKER
#  (k3s pods → ministack via NAT), used throughout the script.
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 2 — Ministack Container Inspection"

$ministack_container_name = docker ps `
    --filter "ancestor=ministackorg/ministack" `
    --format '{{.Names}}' | Select-Object -First 1

if (-not $ministack_container_name) {
    throw "Ministack is not running. Start with: docker compose up -d"
}
OK "Ministack container: $ministack_container_name"

$ms_json        = (docker inspect $ministack_container_name | ConvertFrom-Json)[0]
$ms_envs        = ($ms_json.Config.Env -join "`n") | ConvertFrom-StringData
$ms_net_settings = $ms_json.NetworkSettings
$ms_networks    = $ms_net_settings.Networks
$ms_ports       = $ms_net_settings.Ports

if (-not $ms_envs.ContainsKey('DOCKER_NETWORK')) {
    throw "'$ministack_container_name' is missing the 'DOCKER_NETWORK' env var."
}
$ministack_network_name = $ms_envs.DOCKER_NETWORK
if (-not $ministack_network_name) {
    throw "'DOCKER_NETWORK' is empty in '$ministack_container_name'."
}
OK "Docker network: $ministack_network_name"

if (-not $ms_networks.PSObject.Properties[$ministack_network_name]) {
    throw "Container '$ministack_container_name' not connected to '$ministack_network_name'."
}

$ministack_gw        = $ms_networks.$ministack_network_name.Gateway
$ministack_ip        = $ms_networks.$ministack_network_name.IPAddress
$ministack_host_port = $ms_ports.PSObject.Properties.Value[0].HostPort

if (-not $ministack_gw)        { throw "Gateway for '$ministack_network_name' is empty." }
if (-not $ministack_ip)        { throw "IP for '$ministack_container_name' is empty." }
if (-not $ministack_host_port) { throw "Host port for '$ministack_container_name' is empty." }

# Two endpoint references used throughout
$EP_HOST   = "http://localhost:${ministack_host_port}"   # Windows host → ministack
$EP_DOCKER = "http://${ministack_ip}:${MINISTACK_PORT}"  # inside Docker net / k3s pods → ministack

OK "Ministack IP (Docker net)     : $ministack_ip"
OK "Gateway                       : $ministack_gw"
OK "Host port                     : $ministack_host_port"
OK "EP_HOST   (Windows→ministack) : $EP_HOST"
OK "EP_DOCKER (pods→ministack)    : $EP_DOCKER"

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — Ministack Health
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 3 — Ministack Health"

$health = (Invoke-WebRequest "$EP_HOST/_ministack/health" -UseBasicParsing).Content | ConvertFrom-Json
OK "Version: $($health.version)   Edition: $($health.edition)"

if ($health.services.eks -ne 'available') {
    WARN "EKS service not 'available' in ministack (got: $($health.services.eks))"
} else {
    OK "EKS service: available"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 4 — Pre-provision AWS Resources (VPC / Subnets / SG / IGW)
#
#  Done BEFORE EKS creation so real subnet/SG IDs are available to pass
#  into create-cluster and to reuse for LBC Helm values + ELBv2 registration.
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 4 — Pre-provision AWS Resources (VPC / Subnets / SG / IGW)"

# Ministack accepts any non-empty credential values
$env:AWS_ACCESS_KEY_ID     = 'test'
$env:AWS_SECRET_ACCESS_KEY = 'test'
$env:AWS_DEFAULT_REGION    = $REGION
$env:AWS_ENDPOINT_URL      = $EP_HOST   # all Windows-side CLI calls use this

# VPC
INFO "Creating VPC (172.20.0.0/16)..."
$vpcTagSpec = "ResourceType=vpc,Tags=[{Key=Name,Value=ministack-vpc},{Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared}]"
$vpcId = (aws ec2 create-vpc `
    --cidr-block '172.20.0.0/16' `
    --tag-specifications $vpcTagSpec `
    | ConvertFrom-Json).Vpc.VpcId
OK "VPC: $vpcId"

# Two subnets in different AZs — ALB requires ≥2; kubernetes.io/role/elb=1
# lets the LBC auto-discover them via ec2:DescribeSubnets
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

# Security group — ALB requires an SG; allow HTTP inbound
INFO "Creating security group..."
$sgId = (aws ec2 create-security-group `
    --group-name 'ministack-lbc-sg' `
    --description 'LBC SG for ministack ALB' `
    --vpc-id $vpcId `
    | ConvertFrom-Json).GroupId
aws ec2 authorize-security-group-ingress `
    --group-id $sgId `
    --protocol tcp --port 80 --cidr '0.0.0.0/0' | Out-Null
OK "Security group: $sgId"

# Internet gateway — ALB requires an IGW attached to the VPC
INFO "Creating + attaching IGW..."
$igwId = (aws ec2 create-internet-gateway | ConvertFrom-Json).InternetGateway.InternetGatewayId
aws ec2 attach-internet-gateway `
    --internet-gateway-id $igwId `
    --vpc-id $vpcId | Out-Null
OK "IGW: $igwId"

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 5 — EKS Cluster Creation + Poll Until ACTIVE
#
#  ministack spins up a k3s sidecar container (ministack-eks-<name>) once
#  the cluster reaches ACTIVE. Phase 6 depends on that container existing.
#
#  Both the IAM role and the cluster are created idempotently: the script
#  checks for existing resources before attempting creation.
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 5 — EKS Cluster Creation + Wait for ACTIVE"

# ── IAM role (get-or-create) ──────────────────────────────────────────────────
INFO "Ensuring IAM role '$EKS_ROLE_NAME'..."
$eksRoleArn = (aws iam get-role --role-name $EKS_ROLE_NAME 2>$null | ConvertFrom-Json).Role.Arn

if (-not $eksRoleArn) {
    $trustPolicy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"eks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
    $eksRoleArn  = (aws iam create-role `
        --role-name $EKS_ROLE_NAME `
        --assume-role-policy-document $trustPolicy `
        | ConvertFrom-Json).Role.Arn
    OK "IAM role created: $eksRoleArn"
} else {
    OK "IAM role exists : $eksRoleArn"
}

# ── Cluster (skip creation if already exists, still poll to ACTIVE) ───────────
INFO "Checking for existing cluster '$CLUSTER_NAME'..."
$clusterJson   = aws eks describe-cluster --name $CLUSTER_NAME 2>$null
$currentStatus = if ($clusterJson) { ($clusterJson | ConvertFrom-Json).cluster.status } else { $null }

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
        INFO "Cluster '$CLUSTER_NAME' exists with status '$currentStatus' — polling to ACTIVE..."
    }

    # ── Poll until ACTIVE ─────────────────────────────────────────────────────
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
        throw "Cluster '$CLUSTER_NAME' did not reach ACTIVE within ${EKS_WAIT_SECS}s (last: $status)"
    }
    OK "Cluster '$CLUSTER_NAME' is ACTIVE"
}

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 6 — k3s Kubeconfig Setup
#
#  ministack starts ministack-eks-<name> when the cluster becomes ACTIVE.
#  Rule: NEVER use DescribeCluster's endpoint after ACTIVE — it returns the
#  container-internal IP. Always patch 127.0.0.1:6443 → localhost:<host-port>.
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 6 — k3s Kubeconfig Setup"

$k3sContainer = "ministack-eks-$CLUSTER_NAME"

# ministack may lag slightly before the sidecar starts; wait up to 30s
INFO "Waiting for k3s container '$k3sContainer' to appear..."
$k3sDeadline = (Get-Date).AddSeconds(30)
while (-not (docker ps --format '{{.Names}}' | Where-Object { $_ -eq $k3sContainer })) {
    if ((Get-Date) -gt $k3sDeadline) {
        throw "k3s container '$k3sContainer' did not appear within 30s of ACTIVE."
    }
    Start-Sleep 3
}
OK "k3s container running: $k3sContainer"

$k3sInspect = (docker inspect $k3sContainer | ConvertFrom-Json)[0]

# Prefer the 6443 port mapping; fall back to the first available port
$k3sPorts       = $k3sInspect.NetworkSettings.Ports
$k3s6443Prop    = $k3sPorts.PSObject.Properties | Where-Object { $_.Name -like '6443/*' }
$K3S_API_PORT   = if ($k3s6443Prop) {
    $k3s6443Prop.Value[0].HostPort
} else {
    $k3sPorts.PSObject.Properties.Value[0].HostPort
}

$k3sContainerIP = $k3sInspect.NetworkSettings.Networks.$ministack_network_name.IPAddress
if (-not $k3sContainerIP) {
    throw "Cannot resolve IP for '$k3sContainer' on network '$ministack_network_name'."
}

OK "k3s container IP : $k3sContainerIP"
OK "k3s API host port: $K3S_API_PORT"

$rawKubeconfig   = docker exec $k3sContainer cat /etc/rancher/k3s/k3s.yaml
$fixedKubeconfig = $rawKubeconfig -replace 'https://127\.0\.0\.1:6443', "https://localhost:$K3S_API_PORT"
$fixedKubeconfig | Set-Content $KUBECONFIG_PATH
$env:KUBECONFIG  = $KUBECONFIG_PATH
OK "Kubeconfig patched: $KUBECONFIG_PATH"

kubectl cluster-info
kubectl get nodes -o wide

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 7 — Deploy Test Workload
#
#  Three service surfaces:
#    nginx-nodeport  NodePort :30080     — direct Docker-net test path
#    nginx-nlb       LoadBalancer type   — LBC creates NLB in ministack ELBv2
#    nginx-alb       Ingress (alb class) — LBC creates ALB in ministack ELBv2
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 7 — Deploy Test Workload (nginx + NodePort + NLB svc + ALB ingress)"

kubectl create namespace $APP_NS --dry-run=client -o yaml | kubectl apply -f -

KubApply 'nginx-deploy' @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: $APP_NS
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests: { cpu: 50m,  memory: 32Mi }
          limits:   { cpu: 100m, memory: 64Mi }
"@

# NodePort :30080 — the actual traffic path from the ministack container
KubApply 'nginx-nodeport' @"
apiVersion: v1
kind: Service
metadata:
  name: nginx-nodeport
  namespace: $APP_NS
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    nodePort: $NODE_PORT
"@

# LoadBalancer — LBC watches this and calls ministack ELBv2 to create NLB
KubApply 'nginx-nlb-svc' @"
apiVersion: v1
kind: Service
metadata:
  name: nginx-nlb
  namespace: $APP_NS
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "external"
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "instance"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
    service.beta.kubernetes.io/aws-load-balancer-subnets: "$sub1,$sub2"
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
"@

# Ingress — LBC watches this and calls ministack ELBv2 to create ALB
KubApply 'nginx-alb-ingress' @"
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-alb
  namespace: $APP_NS
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: instance
    alb.ingress.kubernetes.io/subnets: "$sub1,$sub2"
    alb.ingress.kubernetes.io/security-groups: "$sgId"
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-nodeport
            port:
              number: 80
"@

INFO "Waiting for nginx pods (timeout 120s)..."
kubectl wait --for=condition=ready pod -l app=nginx -n $APP_NS --timeout=120s
OK "Pods ready"

kubectl get pods,svc,ingress -n $APP_NS -o wide

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 8 — cert-manager (LBC webhook TLS dependency)
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 8 — Install cert-manager"

helm repo add jetstack https://charts.jetstack.io --force-update 2>$null | Out-Null

helm upgrade --install cert-manager jetstack/cert-manager `
    --namespace cert-manager `
    --create-namespace `
    --set crds.enabled=true `
    --wait --timeout 5m

foreach ($label in @('app=cert-manager', 'app=webhook', 'app=cainjector')) {
    kubectl wait pod -n cert-manager -l $label --for=condition=ready --timeout=120s
}
OK "cert-manager ready"

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 9 — AWS Load Balancer Controller
#
#  AWS_ENDPOINT_URL = EP_DOCKER: LBC pods (10.42.x.x) reach ministack
#  (172.x.x.x) via k3s container NAT. EP_HOST is not reachable from inside k3s.
#
#  Expected behaviour against ministack:
#    ✅ ELBv2 API calls succeed (create-load-balancer, create-target-group, …)
#    ⚠  ec2:DescribeInstances returns empty — k3s nodes ≠ EC2 instances
#    ⚠  Target registration incomplete — Phase 10 compensates manually
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 9 — Install AWS Load Balancer Controller (chart v$LBC_VERSION)"

helm repo add eks https://aws.github.io/eks-charts --force-update 2>$null | Out-Null
helm repo update | Out-Null

@"
clusterName: "$CLUSTER_NAME"
region: "$REGION"
vpcId: "$vpcId"
replicaCount: 1
enableCertManager: true

serviceAccount:
  create: true
  name: aws-load-balancer-controller

# Route all AWS SDK calls to ministack via the Docker-network endpoint.
# LBC pods use k3s outbound NAT to reach 172.x.x.x from 10.42.x.x.
extraEnv:
  - name: AWS_ACCESS_KEY_ID
    value: "test"
  - name: AWS_SECRET_ACCESS_KEY
    value: "test"
  - name: AWS_DEFAULT_REGION
    value: "$REGION"
  - name: AWS_ENDPOINT_URL
    value: "$EP_DOCKER"

enableWaf:    false
enableWafv2:  false
enableShield: false

resources:
  requests: { cpu: 100m, memory: 128Mi }
  limits:   { cpu: 200m, memory: 256Mi }
"@ | Set-Content "$env:TEMP\ms-lbc-values.yaml"

INFO "Running helm upgrade/install for LBC..."
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller `
    --namespace kube-system `
    --version $LBC_VERSION `
    --values "$env:TEMP\ms-lbc-values.yaml" `
    --wait --timeout 5m

# kubectl wait can time out when an old revision pod is still terminating.
# Poll the Ready condition directly instead.
INFO "Polling for LBC pod Ready (timeout 120s)..."
$lbcPollSecs = 5
$lbcMaxSecs  = 120
$lbcElapsed  = 0
$lbcReady    = $false

do {
    Start-Sleep $lbcPollSecs
    $lbcElapsed += $lbcPollSecs
    $readyCond  = kubectl get pod -n kube-system `
        -l 'app.kubernetes.io/name=aws-load-balancer-controller' `
        -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>$null
    $lbcReady = ($readyCond -eq 'True')
} until ($lbcReady -or $lbcElapsed -ge $lbcMaxSecs)

if ($lbcReady) { OK "LBC pod Ready" } else { WARN "LBC pod not Ready after ${lbcMaxSecs}s — proceeding" }
kubectl get pods -n kube-system -l 'app.kubernetes.io/name=aws-load-balancer-controller'

INFO "Waiting 30s for LBC to reconcile Service and Ingress..."
Start-Sleep 30

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 10 — Manual ELBv2 Registration (NLB + ALB)
#
#  LBC cannot find k3s containers via ec2:DescribeInstances (no EC2 instances).
#  We register the k3s NodePort directly as the target for both load balancers.
#
#  Actual traffic path:
#    ministack (172.x.x.x) → Docker net → k3s (:NODE_PORT) → iptables → nginx pod
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 10 — Manual ELBv2 Registration (NLB + ALB)"

# ── NLB ──────────────────────────────────────────────────────────────────────
INFO "Creating NLB (network / internet-facing)..."
$nlbResult = aws elbv2 create-load-balancer `
    --name 'ministack-nlb' `
    --type network `
    --scheme 'internet-facing' `
    --subnets $sub1 $sub2 `
    | ConvertFrom-Json
$nlbArn = $nlbResult.LoadBalancers[0].LoadBalancerArn
$nlbDns = $nlbResult.LoadBalancers[0].DNSName
OK "NLB: $nlbDns"

INFO "Creating NLB target group (TCP:${NODE_PORT} / instance)..."
$nlbTgArn = (aws elbv2 create-target-group `
    --name 'ministack-nlb-tg' `
    --protocol TCP `
    --port $NODE_PORT `
    --vpc-id $vpcId `
    --target-type instance `
    --health-check-protocol TCP `
    --health-check-port $NODE_PORT `
    | ConvertFrom-Json).TargetGroups[0].TargetGroupArn
OK "NLB TG: $nlbTgArn"

INFO "Registering k3s node as NLB target (${k3sContainerIP}:${NODE_PORT})..."
aws elbv2 register-targets `
    --target-group-arn $nlbTgArn `
    --targets "Id=${k3sContainerIP},Port=${NODE_PORT}" | Out-Null
OK "NLB target registered"

INFO "Creating NLB listener (TCP:80 → forward)..."
$nlbListenerArn = (aws elbv2 create-listener `
    --load-balancer-arn $nlbArn `
    --protocol TCP `
    --port 80 `
    --default-actions "Type=forward,TargetGroupArn=$nlbTgArn" `
    | ConvertFrom-Json).Listeners[0].ListenerArn
OK "NLB listener: $nlbListenerArn"

# ── ALB ──────────────────────────────────────────────────────────────────────
INFO "Creating ALB (application / internet-facing)..."
$albResult = aws elbv2 create-load-balancer `
    --name 'ministack-alb' `
    --type application `
    --scheme 'internet-facing' `
    --security-groups $sgId `
    --subnets $sub1 $sub2 `
    | ConvertFrom-Json
$albArn = $albResult.LoadBalancers[0].LoadBalancerArn
$albDns = $albResult.LoadBalancers[0].DNSName
OK "ALB: $albDns"

INFO "Creating ALB target group (HTTP:${NODE_PORT} / instance)..."
$albTgArn = (aws elbv2 create-target-group `
    --name 'ministack-alb-tg' `
    --protocol HTTP `
    --port $NODE_PORT `
    --vpc-id $vpcId `
    --target-type instance `
    --health-check-protocol HTTP `
    --health-check-path '/' `
    --health-check-port $NODE_PORT `
    | ConvertFrom-Json).TargetGroups[0].TargetGroupArn
OK "ALB TG: $albTgArn"

INFO "Registering k3s node as ALB target (${k3sContainerIP}:${NODE_PORT})..."
aws elbv2 register-targets `
    --target-group-arn $albTgArn `
    --targets "Id=${k3sContainerIP},Port=${NODE_PORT}" | Out-Null
OK "ALB target registered"

INFO "Creating ALB listener (HTTP:80 → forward)..."
$albListenerArn = (aws elbv2 create-listener `
    --load-balancer-arn $albArn `
    --protocol HTTP `
    --port 80 `
    --default-actions "Type=forward,TargetGroupArn=$albTgArn" `
    | ConvertFrom-Json).Listeners[0].ListenerArn
OK "ALB listener: $albListenerArn"

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 11 — Verify ELBv2 State
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 11 — Verify ELBv2 State"

Write-Host "`n  Load Balancers:"
aws elbv2 describe-load-balancers | ConvertFrom-Json |
    Select-Object -ExpandProperty LoadBalancers |
    Format-Table LoadBalancerName, Type, Scheme,
        @{L='State';E={$_.State.Code}}, DNSName

Write-Host "`n  Target Groups:"
aws elbv2 describe-target-groups | ConvertFrom-Json |
    Select-Object -ExpandProperty TargetGroups |
    Format-Table TargetGroupName, Protocol, Port, TargetType

Write-Host "`n  NLB target health:"
aws elbv2 describe-target-health --target-group-arn $nlbTgArn | ConvertFrom-Json |
    Select-Object -ExpandProperty TargetHealthDescriptions |
    Format-Table @{L='Target';E={"$($_.Target.Id):$($_.Target.Port)"}},
                 @{L='State'; E={$_.TargetHealth.State}}

Write-Host "`n  ALB target health:"
aws elbv2 describe-target-health --target-group-arn $albTgArn | ConvertFrom-Json |
    Select-Object -ExpandProperty TargetHealthDescriptions |
    Format-Table @{L='Target';E={"$($_.Target.Id):$($_.Target.Port)"}},
                 @{L='State'; E={$_.TargetHealth.State}}

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 12 — LBC Activity Check
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 12 — LBC Activity (logs + k8s status)"

$lbcPod = kubectl get pod -n kube-system `
    -l 'app.kubernetes.io/name=aws-load-balancer-controller' -o name |
    Select-Object -First 1

Write-Host "`n  LBC pod: $lbcPod"
Write-Host "`n  LBC logs (last 30 lines) — look for 'reconciled' or ELBv2 calls:"
kubectl logs $lbcPod -n kube-system --tail=30

Write-Host "`n  nginx-nlb .status.loadBalancer.ingress:"
kubectl get svc nginx-nlb -n $APP_NS -o jsonpath='{.status.loadBalancer.ingress}' 2>$null
Write-Host ""

Write-Host "`n  nginx-alb Ingress .status.loadBalancer.ingress:"
kubectl get ingress nginx-alb -n $APP_NS -o jsonpath='{.status.loadBalancer.ingress}' 2>$null
Write-Host ""

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 13 — Connectivity Tests
#
#  Test 1: NodePort reachability — 3-tier exec strategy:
#    Priority 1  docker exec on ministack container (curl or wget)
#    Priority 2  kubectl exec on existing nginx pod (busybox wget, no image pull)
#    Priority 3  ephemeral curlimages/curl pod (last resort)
#  Test 2: Response body preview (reuses whichever exec path succeeded)
#  Test 3: AWS CLI inside ministack container (ELBv2 visibility check)
#  Test 4: Ephemeral pod → ministack health (validates k3s NAT path for LBC)
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 13 — Connectivity Tests"

$nodePORT_URL = "http://${k3sContainerIP}:${NODE_PORT}"
$httpCode     = $null
$method       = $null
$nginxPod     = $null
$wgetInPod    = $null

Write-Host "`n  [Test 1] NodePort reachability — $nodePORT_URL"

# ── Priority 1: docker exec on ministack container (curl or wget) ─────────────
$httpTool = (docker exec $ministack_container_name sh -c `
    'command -v curl >/dev/null 2>&1 && echo curl ||
     command -v wget >/dev/null 2>&1 && echo wget ||
     echo none').Trim()

if ($httpTool -ne 'none' -and $httpTool) {
    INFO "Priority-1: [$httpTool] in ministack container — docker exec"
    if ($httpTool -eq 'curl') {
        $httpCode = (docker exec $ministack_container_name `
            sh -c "curl -s -o /dev/null -w '%{http_code}' '$nodePORT_URL'").Trim()
    } else {
        $raw      = docker exec $ministack_container_name `
            sh -c "wget -qS -O /dev/null '$nodePORT_URL' 2>&1"
        $httpCode = Get-WgetStatus $raw
    }
    $method = "docker exec [$httpTool] on $ministack_container_name"
} else {
    INFO "Priority-1: no http tool in ministack container — trying kubectl exec"
}

# ── Priority 2: kubectl exec on existing nginx pod (busybox wget) ─────────────
if (-not $httpCode) {
    $nginxPod = kubectl get pod -n $APP_NS -l app=nginx `
        -o jsonpath='{.items[0].metadata.name}' 2>$null
    if ($nginxPod) {
        $wgetInPod = kubectl exec -n $APP_NS $nginxPod -- `
            sh -c 'command -v wget 2>/dev/null' 2>$null
        if ($wgetInPod) {
            INFO "Priority-2: kubectl exec [wget] on pod/$nginxPod"
            $raw      = kubectl exec -n $APP_NS $nginxPod -- `
                sh -c "wget -qS -O /dev/null '$nodePORT_URL' 2>&1" 2>$null
            $httpCode = Get-WgetStatus $raw
            $method   = "kubectl exec [wget] on pod/$nginxPod"
        } else {
            INFO "Priority-2: wget not in nginx pod — deploying test pod"
        }
    }
}

# ── Priority 3: ephemeral test pod ───────────────────────────────────────────
if (-not $httpCode) {
    WARN "Priority-3: deploying ephemeral curlimages/curl pod..."
    $testPodName = 'curl-nodeport-test'
    KubApply $testPodName @"
apiVersion: v1
kind: Pod
metadata:
  name: $testPodName
  namespace: $APP_NS
spec:
  restartPolicy: Never
  containers:
  - name: curl
    image: curlimages/curl:latest
    command:
    - sh
    - -c
    - "curl -s -o /dev/null -w '%{http_code}' '$nodePORT_URL'"
"@
    # Wait for Succeeded/Failed — restartPolicy:Never finishes immediately,
    # so --for=condition=ready would never fire.
    $deadline = (Get-Date).AddSeconds(60)
    do {
        Start-Sleep 2
        $phase = kubectl get pod $testPodName -n $APP_NS `
            -o jsonpath='{.status.phase}' 2>$null
    } until ($phase -in @('Succeeded', 'Failed') -or (Get-Date) -gt $deadline)

    $httpCode = (kubectl logs $testPodName -n $APP_NS 2>$null).Trim()
    kubectl delete pod $testPodName -n $APP_NS --ignore-not-found | Out-Null
    $method = 'ephemeral pod [curlimages/curl]'
}

# ── Test 1 result ─────────────────────────────────────────────────────────────
Write-Host ""
if ($httpCode -eq '200') {
    OK "$method"
    OK "  → $nodePORT_URL → HTTP $httpCode — nginx pods reachable ✔"
} elseif ($httpCode) {
    WARN "$method → $nodePORT_URL → HTTP '$httpCode' (expected 200)"
} else {
    WARN "All connectivity methods exhausted — could not determine HTTP status"
}

# ── Test 2: body preview (reuses whichever exec path succeeded) ───────────────
Write-Host "`n  [Test 2] Response body preview (first 8 lines):"
if     ($httpTool -eq 'curl') {
    docker exec $ministack_container_name sh -c "curl -s '$nodePORT_URL'" | Select-Object -First 8
} elseif ($httpTool -eq 'wget') {
    docker exec $ministack_container_name sh -c "wget -qO - '$nodePORT_URL'" | Select-Object -First 8
} elseif ($nginxPod -and $wgetInPod) {
    kubectl exec -n $APP_NS $nginxPod -- sh -c "wget -qO - '$nodePORT_URL'" 2>$null | Select-Object -First 8
} else {
    INFO "Skipped (test pod already cleaned up)"
}

# ── Test 3: AWS CLI inside ministack container ────────────────────────────────
Write-Host "`n  [Test 3] ELBv2 visibility from inside ministack container:"
$awsCmd = @"
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=$REGION \
aws --endpoint-url http://localhost:${MINISTACK_PORT} elbv2 describe-load-balancers \
    --query 'LoadBalancers[*].{Name:LoadBalancerName,Type:Type,DNS:DNSName}' \
    --output table 2>&1
"@
try {
    $t3 = docker exec $ministack_container_name sh -c $awsCmd
    Write-Host $t3
    OK "ELBv2 state visible from inside ministack container"
} catch {
    WARN "AWS CLI not in ministack container — ELBv2 verified in Phase 11."
}

# ── Test 4: pod → ministack health (validates k3s NAT path for LBC) ──────────
Write-Host "`n  [Test 4] Ephemeral pod → ministack health (${EP_DOCKER} via k3s NAT):"
INFO "Deploying test pod..."

@"
apiVersion: v1
kind: Pod
metadata:
  name: test-nat-to-ministack
  namespace: $APP_NS
spec:
  restartPolicy: Never
  containers:
  - name: curl
    image: curlimages/curl:latest
    command:
    - sh
    - -c
    - "curl -s -o /dev/null -w 'Pod->ministack HTTP:%{http_code}' ${EP_DOCKER}/_ministack/health && echo"
"@ | Set-Content "$env:TEMP\ms-nat-test.yaml"

kubectl apply -f "$env:TEMP\ms-nat-test.yaml" | Out-Null

$deadline = (Get-Date).AddSeconds(60)
do {
    Start-Sleep 2
    $natPhase = kubectl get pod test-nat-to-ministack -n $APP_NS `
        -o jsonpath='{.status.phase}' 2>$null
} until ($natPhase -in @('Succeeded', 'Failed') -or (Get-Date) -gt $deadline)

$natResult = (kubectl logs test-nat-to-ministack -n $APP_NS 2>$null).Trim()
Write-Host "  Result: $natResult"
if ($natResult -match '200') {
    OK "k3s NAT path valid — LBC pods can reach $EP_DOCKER ✔"
} else {
    WARN "NAT test unexpected result: '$natResult'"
}
kubectl delete pod test-nat-to-ministack -n $APP_NS --ignore-not-found | Out-Null

# ── Test 5: Docker-network → nginx pod (ingress direction) ────────────────────
# ministack container has no curl/wget, so spin up a throwaway curlimages/curl
# container on the same Docker network — same perspective as ministack itself.
Write-Host "`n  [Test 5] Docker-network → nginx NodePort (ingress direction):"
INFO "docker run [curlimages/curl] on $ministack_network_name → $nodePORT_URL"

$t5code = (docker run --rm `
    --network $ministack_network_name `
    curlimages/curl `
    curl -s -o /dev/null -w '%{http_code}' $nodePORT_URL).Trim()

if ($t5code -eq '200') {
    OK "Docker-network → $nodePORT_URL → HTTP $t5code — ingress direction reachable ✔"
} elseif ($t5code) {
    WARN "Docker-network → $nodePORT_URL → HTTP $t5code (expected 200)"
} else {
    WARN "Docker-network → $nodePORT_URL — no response"
}

Write-Host "`n  Kubernetes workload state:"
kubectl get all -n $APP_NS

# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 14 — Summary
# ═══════════════════════════════════════════════════════════════════════════════
Step "PHASE 14 — Summary"

Write-Host @"

  ╔══════════════════════════════════════════════════════════════════════════╗
  ║  MINISTACK FULL SETUP SUMMARY                                            ║
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  CONTAINERS  (Docker network: $ministack_network_name)
  ║    ministack : $ministack_container_name  ($ministack_ip)
  ║    k3s       : $k3sContainer  ($k3sContainerIP)
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  ENDPOINTS
  ║    EP_HOST   : $EP_HOST   (Windows → ministack)
  ║    EP_DOCKER : $EP_DOCKER  (k3s pods → ministack via NAT)
  ║    NodePort  : http://${k3sContainerIP}:${NODE_PORT}  (direct HTTP test path)
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  EKS CLUSTER
  ║    Name    : $CLUSTER_NAME
  ║    Version : $K8S_VERSION
  ║    Role    : $eksRoleArn
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  AWS RESOURCES (ministack)
  ║    VPC      : $vpcId
  ║    Subnet-A : $sub1  (${REGION}a)
  ║    Subnet-B : $sub2  (${REGION}b)
  ║    SG       : $sgId
  ║    IGW      : $igwId
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  LOAD BALANCERS (ministack ELBv2)
  ║    NLB DNS  : $nlbDns
  ║    NLB ARN  : $nlbArn
  ║    NLB TG   : $nlbTgArn
  ║    ALB DNS  : $albDns
  ║    ALB ARN  : $albArn
  ║    ALB TG   : $albTgArn
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  KUBECONFIG : $KUBECONFIG_PATH
  ╠══════════════════════════════════════════════════════════════════════════╣
  ║  KNOWN LIMITATIONS                                                       ║
  ║    • LBC may log NoCredentialProviders (IRSA unsupported in k3s).        ║
  ║      extraEnv AWS_* vars override this; ELBv2 calls still succeed.       ║
  ║    • LBC logs ec2:DescribeInstances errors (k3s nodes ≠ EC2 instances).  ║
  ║      Phase 10 manual registration is the reliable target path.           ║
  ║    • Pod IPs (10.42.x.x) unreachable from ministack container.           ║
  ║      NodePort (${k3sContainerIP}:${NODE_PORT}) is always the entry point.
  ║    • ALB/NLB DNS names are mock — not locally routable.                  ║
  ╚══════════════════════════════════════════════════════════════════════════╝

"@

Write-Host "  Quick HTTP test (run anytime):" -ForegroundColor Yellow
Write-Host "    docker run --rm --network $ministack_network_name curlimages/curl curl -s http://${k3sContainerIP}:${NODE_PORT}" -ForegroundColor White

Write-Host "`n  ELBv2 check (run anytime):" -ForegroundColor Yellow
Write-Host "    aws --endpoint-url $EP_HOST elbv2 describe-load-balancers" -ForegroundColor White

Write-Host "`n  Set kubeconfig in a new terminal:" -ForegroundColor Yellow
Write-Host "    `$env:KUBECONFIG = '$KUBECONFIG_PATH'" -ForegroundColor White