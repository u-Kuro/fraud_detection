variable "aws_account_id" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "eks_service_endpoint_url" {
  type = string
}

variable "ecr_registry_endpoint" {
  type = string
}
variable "ecr_registry_mirror_endpoint" {
  type = string
}
variable "ecr_registry_mirror_endpoint_url" {
  type = string
}
variable "ecr_registry_secret_name" {
  type = string
}

variable "kubeconfig_host_directory_path" {
  type = string
}
variable "k3s_mount_directory_path" {
  type = string
}
variable "k3s_mount_file_name" {
  type = string
}
