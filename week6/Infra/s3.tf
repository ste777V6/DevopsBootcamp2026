resource "aws_s3_bucket" "lb_logs" {
  bucket        = "alb-logs-devopsbootcamp2026"
  force_destroy = true
}

