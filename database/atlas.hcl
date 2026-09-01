variable "url" {
  type    = string
  default = getenv("URL")
}

variable "dev_url" {
  type    = string
  default = getenv("DEV_URL")
}

variable "dir" {
  type = string
  default = "file://${abspath("${path.module}/migrations")}"
}

env "test" {
  dev = var.dev_url
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