variable "services_role" {
  type = object({
    eks = object({
      name  = string
      arn   = string
    })
    ec2 = object({
      name  = string
      arn   = string
    })
  })
}

variable "admin_arn" {
  type = string
}

variable "teams" {
  type = map(object({
    role_arn  = string
    namespace = string
  }))
}

variable "aws_access_key" { type = string }
variable "aws_secret_key" { type = string }
variable "aws_region"     { type = string }

variable "eks_service_endpoint_url" { type = string }

variable "kubeconfig_host_directory_path" { type = string }
variable "kubeconfig_host_file_name"      { type = string }

variable "ecr_registry_endpoint"            { type = string }
variable "ecr_registry_mirror_endpoint_url" { type = string }
variable "ecr_registry_mirror_endpoint"     { type = string }

variable "ecr_registry_secret_name" { type = string }
variable "ecr_registry_username"    { type = string }
variable "ecr_registry_password"    { type = string }