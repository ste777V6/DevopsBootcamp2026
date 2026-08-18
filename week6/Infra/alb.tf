#Creation of target group for ECS
resource "aws_lb_target_group" "app-tg-blue" {
  name        = "app-tg-blue"
  port        = 5000
  protocol    = "HTTP"
  target_type = "ip"

  vpc_id = aws_vpc.main.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

#Creation of second target group for ECS - blue green deployment (App v2)
resource "aws_lb_target_group" "app-tg-green" {
  name        = "app-tg-green"
  port        = 5000
  protocol    = "HTTP"
  target_type = "ip"

  vpc_id = aws_vpc.main.id

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}


#Definition of ALB

resource "aws_lb" "app-lb" {
  name               = "app-lb-tf"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb-sg.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  #enable_deletion_protection = true

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.id
    prefix  = "test-lb"
    enabled = true
  }

  tags = {
    Environment = "production"
  }
}


#Creation of the listener - first only http with forward then change with https forward and http redirect

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app-lb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate_validation.main.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app-tg-blue.arn
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app-lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}


