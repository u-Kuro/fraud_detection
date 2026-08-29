# Allow Kubernetes to manage resources
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = var.iam_eks_role_name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}
# Allow EKS worker node to connect to EKS Cluster
resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = var.iam_ec2_role_name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}
# Allow CNI to modify the IP configuration for EKS worker node
resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = var.iam_ec2_role_name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}
# Allow EC2 worker node to read from ECR
resource "aws_iam_role_policy_attachment" "ecr_read_only" {
  role       = var.iam_ec2_role_name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}
# Initialize EKS
resource "aws_eks_cluster" "main" {
  name     = "eks"
  version  = "v1.31.4-k3s1" # Fixed version, can only be changed in Ministack's container environment `EKS_K3S_IMAGE`
  role_arn = var.iam_eks_role_arn

  vpc_config {
    subnet_ids = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}
# Initialize EKS worker node
resource "aws_eks_node_group" "main" {
  cluster_name  = aws_eks_cluster.main.id
  node_role_arn = var.iam_ec2_role_arn

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }

  subnet_ids = ["subnet-00000000000000000", "subnet-00000000000000001"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_read_only,
  ]
}
# Setup and get Ministack's EKS configurations
data "external" "k3s_configuration" {
  program = ["powershell", "-File", "${path.module}/scripts/setup-and-get-k3s-configurations.ps1"]

  query = {
    ministack_network_name             = var.ministack_network_name
    ministack_network_gateway          = var.ministack_network_gateway
    eks_cluster_endpoint               = aws_eks_cluster.main.endpoint # https://172.19.0.3:6443 or https://localhost:16443
    k3s_registries_file_path           = var.local_files_eks_registries_file_path
    kubeconfig_for_localhost_file_path = var.local_files_kubeconfig_for_localhost_file_path
    kubeconfig_for_docker_file_path    = var.local_files_kubeconfig_for_docker_file_path
  }

  depends_on = [
    aws_eks_cluster.main,
    aws_eks_node_group.main, # Nodes must exist to confirm proper recovery after K3s restarts.
  ]
}
# Register admin to EKS cluster
resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = var.iam_admin_arn
  type          = "STANDARD"
}
# Allow admin full access to EKS cluster
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = var.iam_admin_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope { type = "cluster" }

  depends_on = [
    aws_eks_access_entry.admin # Needs access entry to associate policy for admin
  ]
}
# Register teams to EKS cluster
resource "aws_eks_access_entry" "teams" {
  for_each      = var.eks_teams
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = var.iam_teams_arns[each.key]
  type          = "STANDARD"
}
# Allow teams to edit their own resources in EKS cluster
resource "aws_eks_access_policy_association" "teams" {
  for_each      = var.eks_teams
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = var.iam_teams_arns[each.key]
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"

  access_scope {
    type       = "namespace"
    namespaces = [var.eks_teams_namespaces[each.key]]
  }

  depends_on = [
    aws_eks_access_entry.teams # Needs access entry to associate policy for each team
  ]
}
# {
#    "cluster": {
#        "name": "test",
#        "arn": "arn:aws:eks:us-east-1:000000000000:cluster/test",
#        "createdAt": "2026-08-19T15:10:19+08:00",
#        "version": "1.30",
#        "endpoint": "https://localhost:16443",
#        "roleArn": "0",
#        "resourcesVpcConfig": {
#            "subnetIds": [
#                "0",
#                "1"
#            ],
#            "securityGroupIds": [
#                "0"
#            ],
#            "clusterSecurityGroupId": "sg-dbc3c57251c9433",
#            "vpcId": "vpc-00000000",
#            "endpointPublicAccess": true,
#            "endpointPrivateAccess": false,
#            "publicAccessCidrs": [
#                "0.0.0.0/0"
#            ]
#        },
#        "kubernetesNetworkConfig": {
#            "serviceIpv4Cidr": "10.100.0.0/16",
#            "ipFamily": "ipv4"
#        },
#        "logging": {
#            "clusterLogging": []
#        },
#        "identity": {
#            "oidc": {
#                "issuer": "http://localhost:4566/oidc/id/AC0DBC95D857474180110E76289C"
#            }
#        },
#        "status": "CREATING",
#        "certificateAuthority": {
#            "data": ""
#        },
#        "platformVersion": "eks.19",
#        "tags": {},
#        "encryptionConfig": [],
#        "accessConfig": {}
#    }
#}