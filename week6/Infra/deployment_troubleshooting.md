# Deployment Troubleshooting Log

Issues hit while running `terraform apply` for the ECS/ALB/ACM stack, in the order
they were found. Domain is managed at an external DNS provider (2bd.net), not
Route53, so ACM validation and app routing records must be created manually.

## 1. ECS service failed - container name mismatch

```
InvalidParameterException: The container bootcamp2026-student-portal-container
does not exist in the task definition.
```

- Cause: the task definition container was named `var.app_name`, but
  `aws_ecs_service.app_service.load_balancer.container_name` referenced
  `"${var.prefix}-${var.app_name}-container"` - a name that doesn't exist in
  the task definition.
- Fix: `ecs.tf` - set `load_balancer.container_name = var.app_name` to match
  the container definition.

## 2. ALB listener failed - certificate not validated

```
UnsupportedCertificate: The certificate ... must have a fully-qualified
domain name, a supported signature, and a supported key size.
```

- Cause: this message is AWS's misleading way of saying the ACM certificate
  isn't `ISSUED` yet. There was no `aws_acm_certificate_validation` resource,
  so Terraform attached the cert ARN to the HTTPS listener immediately after
  requesting it, before DNS validation ever completed (confirmed via
  `aws acm describe-certificate` -> `PENDING_VALIDATION`).
- Fix: `acm.tf` - added `aws_acm_certificate_validation.main`, referencing
  the validation CNAME from `domain_validation_options`. `alb.tf` - listener's
  `certificate_arn` now points at `aws_acm_certificate_validation.main.certificate_arn`
  so Terraform blocks on real issuance instead of racing ahead.
- Manual step required (external DNS, not automatable by Terraform): create
  the validation CNAME AWS provides (`acm_validation_cname_name` /
  `acm_validation_cname_value` outputs) at the 2bd.net DNS provider. ACM
  polls periodically after the record appears - can take minutes up to ~30-60
  min after DNS is confirmed resolvable, not instant.

## 3. ECS service creation failed - target group not attached to LB yet

```
InvalidParameterException: The target group with targetGroupArn
arn:aws:elasticloadbalancing:.../app-tg-blue/... does not have an
associated load balancer.
```

- Cause: `aws_ecs_service.app_service` only had an implicit dependency on
  `aws_lb_target_group.app-tg-blue` (via its ARN), not on
  `aws_lb_listener.https` - the resource that actually attaches the target
  group to the ALB. Terraform could create the ECS service in parallel with,
  or before, the listener.
- Fix: `ecs.tf` - added `depends_on = [aws_lb_listener.https]` on
  `aws_ecs_service.app_service`.

## 4. App domain routing (separate from ACM validation)

The ACM validation CNAME only proves domain ownership - it does not route
traffic. A second, separate CNAME is required at the same external DNS
provider to actually point the app domain at the load balancer:

```
student-portal.stev6devops.2bd.net  CNAME  <aws_lb.app-lb.dns_name>
```

The ALB is created independently of the certificate/listener, so its DNS
name (`terraform output load_balancer_dns_name`) is available in state as
soon as `aws_lb.app-lb` finishes creating - no need to wait for the full
`apply` (including ACM validation) to complete before setting this up.
