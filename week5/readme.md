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

8) Create ECS TAsk definition (see full json in a separate file)

9) Create Service under cluster

    Task Role (custom) :student-app-Secret-Reader (retrieve Env from secret manager)
    TAskExecution Role : ecs-TaskExecutionRole (pulls image from container)
    Environment variable :
    DB_LINK = value from ( arn:aws:secretsmanager:us-east-1:344707019777:secret:dev/student-portal-ibr8hm) 


ISSUES (tasks not starting):

1) Issue Task stopped at: 2026-04-15T12:20:50.259Z
ResourceInitializationError: unable to pull secrets or registry auth: unable to retrieve secret from asm: There is a connection issue between the task and AWS Secrets Manager. Check your task network configuration. failed to fetch secret arn:aws:secretsmanager:us-east-1:344707019777:secret:dev/student-portal-ibr8hm from secrets manager: operation error Secrets Manager: GetSecretValue, https response error StatusCode: 0, RequestID: , canceled, context deadline exceeded

    -missing NAT gateway - must be  ublic subnet - Allow private subnet to use internet gateway
    -missing default route 0.0.0.0/0 on private route table - must point to NAT GAteway
    -missing -AWSSecretsManagerClientReadOnlyAccess- policy in ecsTaskExecutionRole

2)  Task stopped at: 2026-04-15T12:31:41.532Z
Essential container in task exited
1 essential container exited
[student-app] Exit code: 1.


The error sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL means the application is receiving the DB_LINK value, but it is not a valid connection string format.
    
Solution:
Fixed string in Secret manager

 postgresql://myuser:mypassword@student-app-db.cu3wwe2iw53s.us-east-1.rds.amazonaws.com:5432/mydb


3) Task stopped at: 2026-04-15T13:20:50.961Z
Essential container in task exited
1 essential container exited
[student-app] Exit code: 1.

The error has changed to psycopg2.OperationalError: connection to server... failed: Connection timed out. This means your application is now correctly parsing the secret, but it cannot reach the database over the network.

solution :
Check the connection to database - I was missing rule to allow inbound 5432 postgres in the security group for DB

4) Task is stopping
Task failed ELB health checks in (target-group arn:aws:elasticloadbalancing:us-east-1:344707019777:targetgroup/student-app-new-tg/758f2004e4a89e95)


Solution1 : App was listening on port 8000, but LB and security group configured on port 5000.
            Created new security group, deleted service and recreated with correct values.



Solution2 (if still fails with 302 error -redirection ): update the app creating a specific healt route:

@bp.route("/health")
def health_check():
    return "OK", 200


5) Load balancer connectivity problem
ISsue : LBs placed on private subnets by the ECS service . Need to change the LB networks to the two public in teh same VPC 