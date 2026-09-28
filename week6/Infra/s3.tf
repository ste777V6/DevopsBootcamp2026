resource "aws_s3_bucket" "lb_logs" {
  bucket        = "alb-logs-devopsbootcamp2026"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "lb_logs" {
  bucket = aws_s3_bucket.lb_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

