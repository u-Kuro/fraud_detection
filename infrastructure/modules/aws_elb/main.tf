# Initialize ALB
resource "aws_lb" "alb" {
  load_balancer_type = "application"
  internal           = false
}
# Define Traefik from Ministack's K3s port 80
resource "aws_lb_target_group" "traefik_http" {
  port        = var.eks_traefik_http_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = "vpc-00000000000000000"

  # MiniStack never executes health checks
  health_check {
    path = "/"
  }
}
# Register IP from Ministack's EKS for ALB to call
resource "aws_lb_target_group_attachment" "traefik_http" {
  target_group_arn = aws_lb_target_group.traefik_http.arn
  target_id        = var.eks_ip
  port             = var.eks_traefik_http_port

  depends_on = [aws_lb_target_group.traefik_http]
}
# Attach listener in ALB to forward HTTP requests to Traefik for ingress calls
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = var.eks_traefik_http_port
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.traefik_http.arn
  }

  depends_on = [aws_lb_target_group.traefik_http]
}