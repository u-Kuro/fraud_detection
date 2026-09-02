# Pull MiniStack image
resource "docker_image" "ministack" {
  name         = "ministackorg/ministack:1.5"
  keep_locally = true
}
# Create MiniStack
resource "docker_container" "ministack" {
  name    = "ministack"
  image   = docker_image.ministack.image_id
  restart = "unless-stopped"

  networks_advanced {
    name = var.main_docker_network_name
  }

  ports {
    internal = var.ministack_container_port
    external = var.ministack_container_host_port
  }

  env = [
    "DOCKER_NETWORK=${var.main_docker_network_name}",
    "LOG_LEVEL=DEBUG",
    # MiniStack persistence has bugs (clean restart is recommended)
    # "PERSIST_STATE=1",
    # "LOCALSTACK_PERSISTENCE=1",
    # "S3_PERSIST=1",
    # "RDS_PERSIST=1",
    # "MWAA_PERSIST=1",
    # "DSQL_PERSIST=1",
    # "DSQL_STRICT=1",
  ]

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  healthcheck {
    test         = ["CMD", "python", "-c", "from urllib.request import urlopen; urlopen('http://localhost:${var.ministack_container_port}/_ministack/health')"]
    interval     = "5s"
    timeout      = "3s"
    retries      = 10
    start_period = "10s"
  }
}