variable "url" {
  type    = string
  default = getenv("POSTGRES_CONNECTION_URI")
}

variable "dev" {
  type    = string
  default = "docker://postgres/${getenv("POSTGRES_VERSION")}/dev?search_path=public"
}

variable "dir" {
  type = string
  default = "file://migrations"
}

env "test" {
  dev = var.dev
  migration {
    dir = var.dir
  }
  lint {
    destructive { error = true }
    incompatible { error = true }
  }
}

env "production" {
  url = var.url
  migration {
    dir = var.dir
  }
}