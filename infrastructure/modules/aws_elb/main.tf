# LOAD BALANCER
resource "aws_lb" "alb" {
  load_balancer_type = "application"
  internal           = false
}
# TRAEFIK
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
resource "aws_lb_target_group" "traefik_https" {
  port        = var.eks_traefik_https_port
  protocol    = "HTTPS"
  target_type = "ip"
  vpc_id      = "vpc-00000000000000000"

  # MiniStack never executes health checks
  health_check {
    path = "/"
  }
}
# REGISTER TRAEFIK (FROM K3S)
resource "aws_lb_target_group_attachment" "traefik_http" {
  target_group_arn = aws_lb_target_group.traefik_http.arn
  target_id        = var.eks_ip
  port             = var.eks_traefik_http_port

  depends_on = [aws_lb_target_group.traefik_http]
}
resource "aws_lb_target_group_attachment" "traefik_https" {
  target_group_arn = aws_lb_target_group.traefik_https.arn
  target_id        = var.eks_ip
  port             = var.eks_traefik_https_port

  depends_on = [aws_lb_target_group.traefik_https]
}
# FORWARD ALL REQUESTS TO TRAEFIK
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
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.alb.arn
  port              = var.eks_traefik_https_port
  protocol          = "HTTPS"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.traefik_https.arn
  }

  depends_on = [aws_lb_target_group.traefik_https]
}