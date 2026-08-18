output "load_balancer_dns_name" {
  description = "DNS name of the AWS load balancer."
  value       = aws_lb.app-lb.dns_name
}

output "load_balancer_ip" {
  description = "IP address of the AWS load balancer."
  value       = aws_lb.app-lb.ip_address_type
}

output "ecs_app_service" {
  description = "ECS settings"
  value       = aws_ecs_service.app_service

}

