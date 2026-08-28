# EKS
# /cluster
output "cluster_name" { value = aws_eks_cluster.main.name }
# /urls
output "container_ip" { value = data.external.k3s_configuration.result.k3s_container_ip }
output "container_host_port" { value = tonumber(data.external.k3s_configuration.result.k3s_container_host_port) }
output "host_url" { value = "http://localhost:${data.external.k3s_configuration.result.k3s_container_host_port}" }

# Local Files
# /paths
output "local_files_kubeconfig_for_localhost_file_path" { value = data.external.k3s_configuration.result.kubeconfig_for_localhost_file_path }
output "local_files_kubeconfig_for_docker_file_path" { value = data.external.k3s_configuration.result.kubeconfig_for_docker_file_path }