# Terraform + ECS: coordinating infra and app deployment pipelines

Pattern for running two independent CI/CD pipelines — one for infrastructure (Terraform), one for the application (build/push/deploy) — against the same ECS service without drift or conflicts.

## Problem

With infra and app code in separate repos/folders, both pipelines eventually need to touch the same ECS service:

- The **infra pipeline** provisions the cluster, service, task definition, networking, IAM.
- The **app pipeline** builds a new image and needs it running.

If Terraform manages the container image field directly, every app deploy becomes infrastructure drift — the next `terraform plan`/`apply` will try to roll the image back to whatever's in the `.tf` source.

## Solution: split ownership

| Concern | Owner |
|---|---|
| Cluster, service, networking, IAM, env vars, CPU/memory | Terraform (infra pipeline) |
| Container image tag, task definition revisions | App pipeline (AWS CLI/SDK directly) |

Terraform is told to ignore the field the app pipeline manages:

```hcl
resource "aws_ecs_task_definition" "app" {
  family                   = "myapp"
  cpu                      = 256
  memory                   = 512
  # ... container_definitions with a placeholder/initial image

  lifecycle {
    ignore_changes = [container_definitions]
  }
}
```

The app pipeline never runs `terraform apply`. It talks to ECS/ECR directly:

```bash
# 1. Build & push
docker build -t $ECR_REPO:$GIT_SHA .
docker push $ECR_REPO:$GIT_SHA

# 2. Fetch current task def, patch image, register new revision
aws ecs describe-task-definition --task-definition myapp \
  --query 'taskDefinition' > task-def.json

jq --arg IMAGE "$ECR_REPO:$GIT_SHA" \
  '.containerDefinitions[0].image = $IMAGE
   | del(.taskDefinitionArn, .revision, .status, .requiresAttributes,
         .compatibilities, .registeredAt, .registeredBy)' \
  task-def.json > new-task-def.json

aws ecs register-task-definition --cli-input-json file://new-task-def.json

# 3. Point the service at the new revision
aws ecs update-service --cluster myapp-cluster --service myapp-service \
  --task-definition myapp --force-new-deployment
```

## Pipeline triggers

**Infra pipeline** (`infra/**` path filter):

| Event | Action |
|---|---|
| `pull_request` | `terraform plan`, posted as PR comment |
| `push` to `main` | `terraform apply` → dev |
| approval on `production` environment | `terraform apply` → prod |

**App pipeline** (`app/**` path filter):

| Event | Action |
|---|---|
| `push` to `main` | build, tag with git SHA, push ECR, deploy → dev |
| approval on `production` environment | deploy same image → prod |

Use GitHub Environments with required reviewers on the `production` environment to gate promotion without a second pipeline definition.

## Environment separation

- Separate Terraform state per environment (distinct backend key or workspace, distinct `tfvars`).
- Separate ECS task definition families and service names per environment (`myapp-dev`, `myapp-prod`).
- Same module/pipeline code, different variables — avoid duplicating logic per environment.

## Bootstrap order (one-time)

1. Run the infra pipeline once (manually is fine) to create the cluster, service, and an initial task definition with a placeholder image.
2. From then on, the app pipeline owns every subsequent image update; the infra pipeline only runs when infrastructure itself changes.

## Why this works

Terraform and the app pipeline never write to the same field. Terraform's state reflects everything except the image; the app pipeline's target (task definition revisions on the running service) is invisible to Terraform's plan. No lock contention, no drift, no manual reconciliation.
