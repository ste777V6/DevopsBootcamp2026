variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  type    = string
  default = "Dev"
}

#Defualt tag moved under provider configuration
#variable "aws_tags" {
# description = "A map of tags to apply to all resources"
#type        = map(string)
#default = {
# Environment = "dev"
#Project     = "terraform-bootcamp"
#}
#}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_1_cidr" {
  description = "The CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "public_subnet_2_cidr" {
  description = "The CIDR block for the second public subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "private_subnet_1_cidr" {
  description = "The CIDR block for the private subnet"
  type        = string
  default     = "10.0.3.0/24"
}

variable "private_subnet_2_cidr" {
  description = "The CIDR block for the second private subnet"
  type        = string
  default     = "10.0.4.0/24"
}


variable "availability_zones" {
  description = "List of availability zones to use for subnets"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "aws_eip" {
  description = "Whether to create an Elastic IP for the NAT Gateway"
  type        = bool
  default     = true
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "student-portal"
}

variable "prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "bootcamp2026"
}

variable "ecr_image" {
  description = "The ECR image to use for the ECS task"
  type        = string
  default     = "344707019777.dkr.ecr.us-east-1.amazonaws.com/dev/studentportal:latest"
}

variable "domain_name" {
  description = "The domain name for the application"
  type        = string
  default     = "stev6devops.2bd.net"
}


#Additional variables for rds upgrade via pipeline - need also to point at the variable inside the resource

#variable "db_engine_version" { default = "16" }
#variable "ecs_desired_count" { default = 2 }
#variable "autoscaling_min" { default = 2 }
#variable "autoscaling_max" { default = 4 }
#variable "maintenance_mode" { default = false }