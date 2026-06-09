ECS 3 tier app - terraform

VPC
-2 private subnets
-2 public subnets
-2rds subnets (private)

2 Route table
-associate public/pivate sn to corret RT
-1 Nat Gateway - private AZ
-outes for public/private

3 Security groups for RDS ECS and ALB
-open the ports

ALB
-target group
-ALB(public subnets-min2)
-Listener for port 80
-ACM cert for SSL
-Listener for port 443
-WAF

APP 
-ecr repo
-push app image (manually)()

ECS
-task definition
-cluster
-services
-autoscaling

DNS
-route53 public zone
-create a route to LB
-ACM cert validation

DB
-rds
-secret manager for password
-generate a random password
-create a KMS key for db encryption