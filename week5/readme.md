## ECS with 2 tier app - RDS Db - Postgres Sql

-Database will be POstgres SQL on AWS ( not a container)
-Use student-portal-forECS from week 4 day 2
-need to connect using the string (uncomment it) app.config



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
       
