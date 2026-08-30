resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "${var.prefix}-${var.app_name}-rds-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

locals {
  db_identifier = "${var.prefix}-${var.app_name}-db"
  db_name       = "mydb"
  db_username   = "myuser"
  db_link       = "postgresql://${local.db_username}:${random_password.db_master_password.result}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}/${local.db_name}"
}

# Master password generated and owned by Terraform (not AWS-managed) so it can be
# embedded directly into the single DB_LINK secret below.
resource "random_password" "db_master_password" {
  length  = 32
  special = false
}

resource "aws_db_instance" "postgres" {
  identifier             = local.db_identifier
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.micro"
  port                   = 5432
  allocated_storage      = 20
  db_name                = local.db_name
  username               = local.db_username
  password               = random_password.db_master_password.result
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds-sg.id]
  skip_final_snapshot    = true
  multi_az               = false
  publicly_accessible    = false
}


#Creation of the secret
resource "aws_secretsmanager_secret" "db_link" {
  name = local.db_identifier
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = data.aws_iam_role.ecs_task_execution_role.arn
      }
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = "*"
    }]
  })
}

#Inserting the secret value into the secret
resource "aws_secretsmanager_secret_version" "db_link" {
  secret_id     = aws_secretsmanager_secret.db_link.id
  secret_string = local.db_link
}
