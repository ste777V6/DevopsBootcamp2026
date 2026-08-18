1. Terraform changes needed

a) Enable exec on the service (aws_ecs_service.app_service):
(done)

enable_execute_command = true
b) Give the task a role with SSM messaging permissions. Right now only execution_role_arn is set — there's no task_role_arn (it's commented out in iam.tf). ECS Exec needs the task role (not execution role) to allow:


ssmmessages:CreateControlChannel
ssmmessages:CreateDataChannel
ssmmessages:OpenControlChannel
ssmmessages:OpenDataChannel
You'd create an aws_iam_role + policy for this and set task_role_arn in aws_ecs_task_definition.app_task.

Networking-wise you're fine — private subnets have a NAT gateway and the ecs-sg egress already allows 443 out, which is what SSM needs.
(done)


2. After terraform apply, exec in via AWS CLI

aws ecs list-tasks --cluster ecs-app-cluster --service-name app-service
aws ecs execute-command \
  --cluster ecs-app-cluster \
  --task <task-id-from-above> \
  --container app-service \
  --interactive \
  --command "/bin/sh"
(Requires AWS CLI v2 + the Session Manager plugin installed locally.)

3. Installing Claude (Code CLI) inside
Your image is python:3.12-slim (Dockerfile) — no curl/node baked in, so:


apt-get update && apt-get install -y curl
curl -fsSL https://claude.ai/install.sh | bash
One caveat worth flagging: whatever you install this way disappears the moment the task restarts or redeploys — Fargate containers are ephemeral and there's no persistent volume here. If you need Claude Code available repeatedly (not just a one-off debug session), it'd make more sense to add it to the Dockerfile, or run it in a separate one-off dev container instead of the live app container.

Want me to make the Terraform changes (task role + enable_execute_command) for you?