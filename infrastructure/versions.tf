terraform {
  required_version = "1.16.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.61.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "4.6.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "3.2.0"
    }
    kubectl = {
      source  = "alekc/kubectl"
      version = "2.4.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "3.2.1"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.9.0"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "1.27.0"
    }
  }
}