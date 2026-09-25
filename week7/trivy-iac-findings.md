3# Trivy IaC Scan — `week6/Infra`

| | |
|---|---|
| **Scan date** | 2026-09-25 |
| **Command** | `trivy config week6/Infra` (Trivy v0.74.0, trivy-action v0.36.0) |
| **Severity filter** | HIGH, CRITICAL |
| **Result** | 14 findings: 12 HIGH, 2 CRITICAL, in 5 of 8 files |

## Summary

| File | Findings | Checks |
|---|:---:|---|
| `alb.tf` | 2 | AWS-0052, AWS-0053 |
| `ecs.tf` | 2 | AWS-0030, AWS-0031 |
| `rds.tf` | 1 | AWS-0080 |
| `s3.tf` | 5 | AWS-0086, AWS-0087, AWS-0091, AWS-0093, AWS-0132 |
| `security_groups.tf` | 2 | AWS-0104 (×2) |
| `log_groups.tf`, `networking.tf`, root module | 0 | — |

### At a glance

| ID | Severity | Resource | Issue | Action |
|---|---|---|---|---|
| AWS-0052 | HIGH | `aws_lb.app-lb` | ALB doesn't drop invalid headers | Fix |
| AWS-0053 | HIGH | `aws_lb.app-lb` | ALB is internet-facing | Accept (by design) |
| AWS-0030 | HIGH | `aws_ecr_repository.app_ecr` | Scan on push disabled | Fix |
| AWS-0031 | HIGH | `aws_ecr_repository.app_ecr` | Image tags are mutable | Fix |
| AWS-0080 | HIGH | `aws_db_instance.postgres` | Storage not encrypted | Fix |
| AWS-0086 | HIGH | `aws_s3_bucket.lb_logs` | Public ACLs not blocked | Fix |
| AWS-0087 | HIGH | `aws_s3_bucket.lb_logs` | Public policies not blocked | Fix |
| AWS-0091 | HIGH | `aws_s3_bucket.lb_logs` | Public ACLs not ignored | Fix |
| AWS-0093 | HIGH | `aws_s3_bucket.lb_logs` | Public buckets not restricted | Fix |
| AWS-0132 | HIGH | `aws_s3_bucket.lb_logs` | No customer-managed KMS key | Accept (ALB logs require SSE-S3) |
| AWS-0104 | CRITICAL | `aws_security_group.ecs-sg` (line 44) | Egress to `0.0.0.0/0` | Restrict or accept |
| AWS-0104 | CRITICAL | `aws_security_group.ecs-sg` (line 51) | Egress to `0.0.0.0/0` | Restrict or accept |

The four S3 public-access findings are fixed by one resource.

---

## `alb.tf`

### AWS-0052 (HIGH) — ALB not set to drop invalid headers

- **Location:** `alb.tf:40-58`, `aws_lb.app-lb`
- **Risk:** Malformed or non-standard headers pass through to the targets.
- **Fix:**

```hcl
resource "aws_lb" "app-lb" {
  # ...
  drop_invalid_header_fields = true
}
```

Reference: https://avd.aquasec.com/misconfig/aws-0052

### AWS-0053 (HIGH) — Load balancer is exposed publicly

- **Location:** `alb.tf:42`, `internal = false`
- **Risk:** A warning against accidentally exposing internal services.
- **Action:** Accept. This ALB is the application's public entry point, so being internet-facing is intentional. Add it to `.trivyignore.yaml` (see below).

Reference: https://avd.aquasec.com/misconfig/aws-0053

---

## `ecs.tf`

### AWS-0030 (HIGH) — ECR image scanning not enabled

- **Location:** `ecs.tf:3-6`, `aws_ecr_repository.app_ecr`
- **Fix:**

```hcl
resource "aws_ecr_repository" "app_ecr" {
  # ...
  image_scanning_configuration {
    scan_on_push = true
  }
}
```

Reference: https://avd.aquasec.com/misconfig/aws-0030

### AWS-0031 (HIGH) — ECR repository tags are mutable

- **Location:** `ecs.tf:3-6`, `aws_ecr_repository.app_ecr`
- **Risk:** An existing tag can be overwritten with a different image.
- **Fix:**

```hcl
resource "aws_ecr_repository" "app_ecr" {
  # ...
  image_tag_mutability = "IMMUTABLE"
}
```

> **Note:** With `IMMUTABLE`, re-pushing the same tag fails. Tag images with the commit SHA instead of `latest`, and deploy by that tag.

Reference: https://avd.aquasec.com/misconfig/aws-0031

---

## `rds.tf`

### AWS-0080 (HIGH) — RDS storage encryption not enabled

- **Location:** `rds.tf:20-35`, `aws_db_instance.postgres`
- **Fix:**

```hcl
resource "aws_db_instance" "postgres" {
  # ...
  storage_encrypted = true
  # kms_key_id      = aws_kms_key.rds.arn   # optional: customer-managed key
}
```

> **Note:** On an existing instance this forces replacement, because encryption can't be enabled in place. Take a snapshot first if the data matters.

Reference: https://avd.aquasec.com/misconfig/aws-0080

---

## `s3.tf`

All five findings are on `s3.tf:1-4`, `aws_s3_bucket.lb_logs` (bucket `alb-logs-devopsbootcamp2026`).

### AWS-0086, AWS-0087, AWS-0091, AWS-0093 (HIGH) — No public access block

| ID | Missing setting |
|---|---|
| AWS-0086 | `block_public_acls` |
| AWS-0087 | `block_public_policy` |
| AWS-0091 | `ignore_public_acls` |
| AWS-0093 | `restrict_public_buckets` |

**Fix (one resource covers all four):**

```hcl
resource "aws_s3_bucket_public_access_block" "lb_logs" {
  bucket = aws_s3_bucket.lb_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

The ALB log-delivery bucket policy grants access to the ELB service principal, not to the public, so it still works with these settings.

References: https://avd.aquasec.com/misconfig/aws-0086 · https://avd.aquasec.com/misconfig/aws-0087 · https://avd.aquasec.com/misconfig/aws-0091 · https://avd.aquasec.com/misconfig/aws-0093

### AWS-0132 (HIGH) — Bucket not encrypted with a customer-managed key

- **Action:** Accept. ALB access logs can only be delivered to buckets encrypted with SSE-S3 (`AES256`), not SSE-KMS, so a CMK here would break log delivery. Set SSE-S3 explicitly and ignore this check for this bucket:

```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "lb_logs" {
  bucket = aws_s3_bucket.lb_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

Reference: https://avd.aquasec.com/misconfig/aws-0132

---

## `security_groups.tf`

### AWS-0104 (CRITICAL ×2) — Unrestricted egress

- **Location:** `security_groups.tf:44` and `:51`, both egress rules in `aws_security_group.ecs-sg` (lines 28-53)
- **Risk:** ECS tasks can connect to any IP on the internet, which would make exfiltration easy from a compromised container.
- **Context:** The tasks do need outbound access to pull images from ECR, write to CloudWatch Logs, and reach RDS.
- **Options, strongest first:**
  1. Add VPC endpoints (ECR API, ECR DKR, S3 gateway, CloudWatch Logs) and restrict egress to those endpoints plus the RDS security group.
  2. Keep internet egress but limit it to what's needed: HTTPS (443) to `0.0.0.0/0`, and 5432 only to the RDS security group.

```hcl
# Option 2 example
egress {
  description = "HTTPS for ECR, CloudWatch, external APIs"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

egress {
  description     = "Postgres to RDS only"
  from_port       = 5432
  to_port         = 5432
  protocol        = "tcp"
  security_groups = [aws_security_group.rds-sg.id]  # adjust to your RDS SG name
}
```

With option 2, Trivy still flags the 443 rule. Accept it in `.trivyignore.yaml` with a justification, or move to option 1.

Reference: https://avd.aquasec.com/misconfig/aws-0104

---

## Accepted findings — `.trivyignore.yaml`

Put this in `week6/Infra/` and pass it with `trivyignores: week6/Infra/.trivyignore.yaml` in the workflow. Each exception has a reason and an expiry date, so it gets reviewed again.

```yaml
misconfigurations:
  - id: AWS-0053
    paths:
      - "alb.tf"
    statement: "Public ALB is the application's intended entry point."
    expired_at: 2027-03-31

  - id: AWS-0132
    paths:
      - "s3.tf"
    statement: "ALB access-log buckets only support SSE-S3; SSE-KMS breaks log delivery."
    expired_at: 2027-03-31

  # Only if you go with option 2 for egress:
  # - id: AWS-0104
  #   paths:
  #     - "security_groups.tf"
  #   statement: "ECS tasks need HTTPS egress to AWS APIs until VPC endpoints are added."
  #   expired_at: 2026-12-31
```

## Remediation checklist

- [ ] AWS-0052 — `drop_invalid_header_fields = true` on the ALB
- [ ] AWS-0030 — `scan_on_push = true` on ECR
- [ ] AWS-0031 — `image_tag_mutability = "IMMUTABLE"`, and switch to SHA tags
- [ ] AWS-0080 — `storage_encrypted = true` on RDS (forces replacement)
- [ ] AWS-0086/0087/0091/0093 — add `aws_s3_bucket_public_access_block`
- [ ] AWS-0132 — explicit SSE-S3, then ignore with a justification
- [ ] AWS-0104 — tighten ECS egress (VPC endpoints or port-restricted rules)
- [ ] AWS-0053 — ignore with a justification
- [ ] Add `.trivyignore.yaml` and reference it in the workflow
- [ ] Re-run the pipeline and confirm the gate passes
