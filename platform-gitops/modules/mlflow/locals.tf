# INPUTS
locals {
  aws    = var.aws
  mlflow = var.mlflow
  rds    = var.rds
  s3     = var.s3
}
# COMPUTED
locals {
  # KUBERNETES
  eks = {
    kubernetes = {
      mlflow = {
        namespace = "mlflow"
      }
    }
  }
  # MLFLOW
  mlflow_tracking_uri = "http://${local.mlflow.host}:${local.mlflow.port}"
  # SCRIPTS
  scripts_relative_path = "scripts"
  create_mlflow_workspace_script_file_name = "create_mlflow_workspace.sh"
  create_mlflow_workspace_script_file_relative_path = "${local.scripts_relative_path}/${local.create_mlflow_workspace_script_file_name}"
}

# CHECK (I THINK THIS NEEDS TO BE DONE ON NEW PODS)
locals {
  mlflow_nodeport  = 30500
  mlflow_path      = "/mlflow"
  # Rule priority — must be unique across ALL rules on the same listener.
  # Assign a fixed number per service so they never collide.
  mlflow_priority  = 100
}
resource "aws_lb_target_group" "mlflow" {
  name        = "mlflow"
  port        = local.mlflow_nodeport
  protocol    = "HTTP"
  vpc_id      = var.alb.vpc_id
  target_type = "ip"

  health_check {
    path = "/health"
  }
}

resource "aws_lb_target_group_attachment" "mlflow" {
  target_group_arn  = aws_lb_target_group.mlflow.arn
  target_id         = var.k3s_ip
  port              = local.mlflow_nodeport
  availability_zone = "all"

  depends_on = [helm_release.mlflow]
}

# Path-based rule on the shared listener.
# Real AWS: this is exactly what the ALB Ingress Controller creates per Ingress resource.
resource "aws_lb_listener_rule" "mlflow" {
  listener_arn = var.alb.listener_arn
  priority     = local.mlflow_priority

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mlflow.arn
  }

  condition {
    path_pattern {
      values = ["${local.mlflow_path}", "${local.mlflow_path}/*"]
    }
  }
}