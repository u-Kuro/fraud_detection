# EKS
# /urls
variable "eks_ip" { type = string }
# /traefik
variable "eks_traefik_http_port" {
  type    = number
  default = 80
}
variable "eks_traefik_https_port" {
  type    = number
  default = 443
}