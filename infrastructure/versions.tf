terraform {
  required_version = "~> 1.15.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.27"
    }
    kubectl = {
      source  = "alekc/kubectl"
      version = "~> 2.4.1"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.2"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.7.0"
    }
  }
}