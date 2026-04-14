## ECS with 2 tier app - RDS Db - Postgres Sql

Notes:
-Database will be POstgres SQL on AWS ( not a container)
-Use student-portal-forECS from week 4 day 2
-Will not include the credential into source code (BAD practicse). We will pass the DB credential via ENV from Clud secret manager  


1) build the network part
     - 2x Private subnet for DB ( 2 zones)
     - 2x Private subnets for app
     - 2x Public subnets for LB
     -connect public subnet to Internet gateway + create default route
     -connect private subnet to egress only (NAt gateway)
     - create security groups
         -https/http to lb
         -port 5000 to app on ECS
         -port xxxx to Postgres DB
  
  2) Create Postgres DB
     - Free or Dev
     - 1 zone for free , 2 zones for DEV second instance read-only

   3) Store the string to access the DB into Secret Manager
       DB_LINK = = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
    
    4) If don't have create a IAM user with permission only for pushing the image into ECR

    5) Build the app from week4/day2/student-portal and tag it for ECR
        docker build -t 344707019777.dkr.ecr.us-east-1.amazonaws.com/dev/studentportal .
    
    6) Login and  Push the image into ECR


      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 344707019777.dkr.ecr.us-east-1.amazonaws.com

    docker push 344707019777.dkr.ecr.us-east-1.amazonaws.com/dev/studentportal:latest

7) Create ECS Cluster

8) Create ECS TAsk definition with 

    Task Role (custom) :student-app-Secret-Reader (retrieve Env from secret manager)
    TAskExecution Role : ecs-TaskExecutionRole (pulls image from container)
    Environment variable :
    DB_LINK = value from ( arn:aws:secretsmanager:us-east-1:344707019777:secret:dev/student-portal-ibr8hm) 

    