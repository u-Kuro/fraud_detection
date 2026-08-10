resource "aws_lb" "main" {
  load_balancer_type = "application"
  internal           = false
}

resource "aws_lb_target_group" "traefik" {
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = "vpc-00000000000000000"

  # MiniStack never actually executes health checks — all targets are
  # always reported healthy — so these values only matter for real AWS parity
  health_check {
    path = "/"
  }
}

# Register the k3s container's Docker-network IP as the single stable target
# This never changes — Traefik handles all routing from here on
resource "aws_lb_target_group_attachment" "traefik" {
  target_group_arn = aws_lb_target_group.traefik.arn
  target_id        = local.eks.ip
  port             = 80

  depends_on = [aws_lb_target_group.traefik]
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  # Catch-all forward — Traefik owns all routing decisions, not the ALB
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.traefik.arn
  }

  depends_on = [aws_lb_target_group.traefik]
}