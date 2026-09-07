##Created test workflows

first worklow - run manually, two jobs in paralle ljust print hello world - test also run with multiple commands
second workflow - run manually, test two jobs in parallel, one on ubuntu and one on windows machine
third workflow - run on push on any branch(except main), two sequntial jobs
fourth-workflow

##Created production workflows

on-pr-terraform - run when a pull request is created ( to merge on main) - check the code is properly formatted for terraform - terraform fmt
ecs-app-deploy-terraform - run on merge with main, deploy the terraform code ( with the version specified on ecs-app)
ecs-app-build-and-push - run manually, build the container from the app folcder(student-portal-for-ECS) tag with the latest Gihub commit
                        and push it to the ECR registry


