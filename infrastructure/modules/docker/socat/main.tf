# Pull Socat image
resource "docker_image" "socat" {
  name         = "alpine/socat:1.8.1.3"
  keep_locally = true
}
# Create HTTP proxy for Traefik listening on K3s IP
resource "docker_container" "traefik_http_proxy" {
  name    = "traefik-http-proxy"
  image   = docker_image.socat.image_id
  command = ["TCP-LISTEN:80,fork,reuseaddr", "TCP-CONNECT:${var.eks_container_ip}:80"]

  networks_advanced {
    name = var.main_network_name
  }
  ports {
    internal = 80
    external = 80
  }

  wait         = true
  wait_timeout = 300
  healthcheck {
    test         = ["CMD", "nc", "-z", "127.0.0.1", "80"]
    interval     = "5s"
    timeout      = "3s"
    retries      = 10
    start_period = "10s"
  }
  restart = "unless-stopped"
}