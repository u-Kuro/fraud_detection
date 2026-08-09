resource "aws_vpc" "this" {
  cidr_block = "10.1.0.0/16"
  tags       = { Name = "cluster-alb-vpc" }
}

resource "aws_subnet" "this" {
  vpc_id     = aws_vpc.this.id
  cidr_block = "10.1.1.0/24"
  tags = {
    Name                              = "cluster-alb-subnet"
    "kubernetes.io/role/internal-elb" = "1"
  }
}

resource "aws_lb" "this" {
  name               = "cluster"
  internal           = true
  load_balancer_type = "application"
  subnets            = [aws_subnet.this.id]
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  # Default: 404 — only matched rules get forwarded.
  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "not found"
      status_code  = "404"
    }
  }
}