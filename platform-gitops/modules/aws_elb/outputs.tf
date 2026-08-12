output "alb" {
  value = {
    dns_name = aws_lb.alb.dns_name
  }
}