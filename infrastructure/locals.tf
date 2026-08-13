locals {

}

resource "local_sensitive_file" "kubeconfig_host" {
  filename        = "${local.local_files_directory_path}/kubeconfig_host.yaml"
  file_permission = "0600"
}
resource "local_sensitive_file" "mwaa_requirements" {
  filename        = "${local.local_files_directory_path}/requirements.txt"
  file_permission = "0600"
}