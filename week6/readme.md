ECS 3 tier app - terraform

VPC
-2 private subnets
-2 public subnets
-2rds subnets (private)

2 Route table
-associate public/pivate sn to corret RT
-1 Nat Gateway - private AZ
-outes for public/private

ALB
-target group
-ALB(public subnets-min2)
-Listener for port 80
-ACM cert for SSL
-Listener for port 443

