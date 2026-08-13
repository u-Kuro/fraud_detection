# LOAD BALANCER
resource "aws_lb" "alb" {
  load_balancer_type = "application"
  internal           = false
}
# TRAEFIK
resource "aws_lb_target_group" "traefik_http" {
  port        = local.system_ports.http
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = "vpc-00000000000000000"

  # MiniStack never executes health checks
  health_check {
    path = "/"
  }
}
resource "aws_lb_target_group" "traefik_https" {
  port        = local.system_ports.https
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
  target_id        = local.eks.ip
  port             = local.system_ports.http

  depends_on = [aws_lb_target_group.traefik_http]
}
resource "aws_lb_target_group_attachment" "traefik_https" {
  target_group_arn = aws_lb_target_group.traefik_https.arn
  target_id        = local.eks.ip
  port             = local.system_ports.https

  depends_on = [aws_lb_target_group.traefik_https]
}
# FORWARD ALL REQUESTS TO TRAEFIK
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = local.system_ports.http
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.traefik_http.arn
  }

  depends_on = [aws_lb_target_group.traefik_http]
}
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.alb.arn
  port              = local.system_ports.https
  protocol          = "HTTPS"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.traefik_https.arn
  }

  depends_on = [aws_lb_target_group.traefik_https]
}