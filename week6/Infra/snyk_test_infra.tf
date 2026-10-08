## SNYK TEST ONLY - DO NOT APPLY
#resource "aws_security_group" "snyk_test_sg" {
#  name = "snyk-test-sg"
#  ingress {
#    from_port   = 22
#    to_port     = 22
#    protocol    = "tcp"
#    cidr_blocks = ["0.0.0.0/0"] # SSH open to the world
#  }
#}
#
#resource "aws_s3_bucket" "snyk_test_bucket" {
#  bucket = "snyk-test-public-bucket-ste777"
#}
#
#resource "aws_s3_bucket_public_access_block" "snyk_test" {
#  bucket                  = aws_s3_bucket.snyk_test_bucket.id
#  block_public_acls       = false
#  block_public_policy     = false
#  ignore_public_acls      = false
#  restrict_public_buckets = false
#}
#
#resource "aws_db_instance" "snyk_test_db" {
#  identifier          = "snyk-test-db"
#  engine              = "postgres"
#  instance_class      = "db.t3.micro"
#  allocated_storage   = 20
#  username            = "admin"
#  password            = "SuperSecret123" # hardcoded secret
#  publicly_accessible = true
#  storage_encrypted   = false
#  skip_final_snapshot = true
#}
#
#resource "aws_iam_policy" "snyk_test_admin" {
#  name = "snyk-test-admin"
#  policy = jsonencode({
#    Version   = "2012-10-17"
#    Statement = [{ Effect = "Allow", Action = "*", Resource = "*" }]
#  })
#}