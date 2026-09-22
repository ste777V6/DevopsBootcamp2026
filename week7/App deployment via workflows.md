##APP DEPLOYMENT AND UPGRADE 

Use ecs-app-deploy-terraform "run it manually" to create the Terraform infrastructure and deploy the first version of the app contained in ECR registry : 

"344707019777.dkr.ecr.us-east-1.amazonaws.com/bootcamp2026-student-portal-ecr:latest"

The domain where the app is deployed is :

"student-portal-stev6devops.2bd.net"

Requirement for the deployment to succeed:
Need to have reserved ip in AWS
A record stev6devops.2bd.net" in Free IP
Permitted AWS servers for validation () in FreeIP
ISSUE founded : the image created was tagged with GitHub commit hash - deployment failed because terraform was looking for :latest Tag
FIX : I've run the V2 script for update the app and it started to work


##Deployment

Run the ecs-app-deploy-terraform
Wait creation of Load Balancer
Create a CNAME record  student.portal.stev6devops.2bd.net -----> Current LB DNS
Create a CNAME record certificate------>certificate
Wait few minutes for validation
Load balancer will also have https listener with certificate
Wait for creation of ECS task ( depends_on = [aws_lb_listener.https] )

<img width="767" height="410" alt="image" src="https://github.com/user-attachments/assets/6698caa5-af40-4cd5-be37-dcb07aed6d8e" />


##APP UPGRADE 

Use ecs-app-build-and-push (V2 tested) "run it manually" 
V1 is using jq
V2 is using pre-built Github actions

<img width="908" height="393" alt="image" src="https://github.com/user-attachments/assets/dc2cd7c3-19f4-44e6-bff9-67a3f1e2a491" />


##NOTES
I've downgraded the app to the previous version because I taught that the issue was teh new app version-
Not true - the issue was the wrong tag : latest 

<img width="494" height="308" alt="image" src="https://github.com/user-attachments/assets/c748b0be-12bc-4a47-a04d-c409b1c7b9ef" />



