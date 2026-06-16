variable "url" {
  type    = string
  default = getenv("POSTGRES_CONNECTION_URI")
}

variable "dev" {
  type    = string
  default = "docker://postgres/${getenv("POSTGRES_VERSION")}/${getenv("FRAUD_DETECTION_DB_NAME")}?search_path=public"
}

variable "dir" {
  type = string
  default = "file://migrations"
}

env "local" {
  url = var.url
  dev = var.dev
  migration {
    dir = var.dir
  }
  lint {
    destructive { error = true }
    incompatible { error = true }
  }
}

env "ci" {
  url = var.url
  dev = var.dev
  migration {
    dir = var.dir
  }
  lint {
    destructive { error = true }
    incompatible { error = true }
  }
}

env "docker" {
  url = var.url
  migration {
    dir = var.dir
  }
}

env "production" {
  url = var.url
  migration {
    dir = var.dir
  }
}