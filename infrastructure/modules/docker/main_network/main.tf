# Create main network for infrastructure
resource "docker_network" "main" {
  name = "fraud-detection-platform-network"
}