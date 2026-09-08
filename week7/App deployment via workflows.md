##APP DEPLOYMENT AND UPGRADE

Use ecs-app-deploy-terraform "run it manually" to create the Terraform infrastructure and deploy the first version of the app contained in ECR registry : 

"344707019777.dkr.ecr.us-east-1.amazonaws.com/bootcamp2026-student-portal-ecr:latest"

The domain where the app is deployed is :

"student-portal-stev6devops.2bd.net"

Requirement for the deployment to succeed:

Need to have reserved ip in AWS
A record stev6devops.2bd.net" in Free IP
Permitted AWS servers for validation ()
Create a CNAME record  student.portal.stev6devops.2bd.net -----> Current LB DNS
Create a CNAME record certificate------>certificate
Wait 20 minutes for validation
Load balancer will be created

###APP UPGRADE 

Use ecs-app-build-and-push "run it manually"
