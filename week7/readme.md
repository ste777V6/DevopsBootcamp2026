## Created test workflows

- **First workflow** — run manually, two jobs in parallel just print hello world; test also run with multiple commands
- **Second workflow** — run manually, test two jobs in parallel, one on Ubuntu and one on Windows machine
- **Third workflow** — run on push on any branch (except main), two sequential jobs
- **Fourth workflow**

## Created production workflows

- **on-pr-terraform** — run when a pull request is created (to merge on main); check the code is properly formatted for Terraform (`terraform fmt`)
- **ecs-app-deploy-terraform** — run on merge with main; deploy the Terraform code (with the version specified on ecs-app)
- **ecs-app-build-and-push** — run manually; build the container from the app folder (`student-portal-for-ECS`), tag with the latest GitHub commit, and push it to the ECR registry