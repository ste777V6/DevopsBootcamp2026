#Fetch the existing ecsTaskExecutionRole"

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}


#App permission - need to be created on AWS first if needed

data "aws_elb_service_account" "main" {}

resource "aws_iam_policy" "secrets_manager_read" {
  name        = "ecs-secrets-manager-read"
  description = "Allow ECS execution role to fetch DB credentials from Secrets Manager"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = aws_secretsmanager_secret.db_link.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_manager" {
  role       = data.aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.secrets_manager_read.arn
}

#s3 buccket policy for load balancer logs
resource "aws_s3_bucket_policy" "lb_logs" {
  bucket = aws_s3_bucket.lb_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowELBLogDelivery"
        Effect = "Allow"
        Principal = {
          AWS = data.aws_elb_service_account.main.arn
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.lb_logs.arn}/*"
      },
      {
        Sid    = "AllowELBLogDeliveryACLCheck"
        Effect = "Allow"
        Principal = {
          Service = "logdelivery.elasticloadbalancing.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.lb_logs.arn
      }
    ]
  })
}


# Create an ECS task role to allow the application to execute commands in the container
resource "aws_iam_role" "ecs_task_role" {
  name = "ecsTaskRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "ecs_exec" {
  name        = "ecs-exec-ssm"
  description = "Allow ECS Exec (SSM) sessions into Fargate tasks"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ssmmessages:CreateControlChannel",
        "ssmmessages:CreateDataChannel",
        "ssmmessages:OpenControlChannel",
        "ssmmessages:OpenDataChannel"
      ]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_role_exec" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_exec.arn
}

