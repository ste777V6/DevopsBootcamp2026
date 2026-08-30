
#New em pty repository
resource "aws_ecr_repository" "app_ecr" {
  name = "${var.prefix}-${var.app_name}-ecr"

}

resource "aws_ecs_cluster" "ecs_cluster" {
  name = "ecs-app-cluster"
  #ENable container insights for ECS cluster - charge for PROD
  # setting {
  #  name = "containerInsights"
  #  value = "enabled"
  #}
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  #Task permission
  execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
  #App permission - allow to execute commands in the container
  task_role_arn = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = var.ecr_image
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        }
      ]
      #environment = [
      # {
      #  name  = "DB_NAME"
      # value = local.db_name # "mydb" — static, no secret needed
      #},
      #{
      # name  = "DB_PORT"
      # value = "5432" # also static
      #},
      #{
      # name  = "DB_USER"
      # value = "myuser"
      #},

      #{
      # name  = "DB_HOST"
      # value = aws_db_instance.postgres.address
      #}


      #]

      secrets = [

        {
          # name      = "DB_PASSWORD"
          # valueFrom = "${aws_db_instance.postgres.master_user_secret[0].secret_arn}:password::"
          name      = "DB_LINK"
          valueFrom = aws_secretsmanager_secret.db_link.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/app"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }

  }])

}

resource "aws_ecs_service" "app_service" {
  name                   = "${var.prefix}-${var.app_name}-service"
  cluster                = aws_ecs_cluster.ecs_cluster.id
  task_definition        = aws_ecs_task_definition.app_task.arn
  desired_count          = 2
  launch_type            = "FARGATE"
  enable_execute_command = true # allow to execute commands in the container

  network_configuration {
    subnets          = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups  = [aws_security_group.ecs-sg.id]
    assign_public_ip = false
  }
  #Connection of target-group with ECS

  load_balancer {
    target_group_arn = aws_lb_target_group.app-tg-blue.arn
    container_name   = var.app_name
    container_port   = 5000

  }

  # Target group must already be attached to the ALB via a listener before
  # ECS can register tasks with it, otherwise CreateService fails with
  # "target group ... does not have an associated load balancer".
  depends_on = [aws_lb_listener.https]

}





