resource "aws_acm_certificate" "main" {
  domain_name       = "${var.app_name}.${var.domain_name}"
  validation_method = "DNS"


  lifecycle {
    create_before_destroy = true
  }
}

#Print the CNAME record to be created at the external DNS provider for validation
output "acm_validation_cname_name" {
  value = tolist(aws_acm_certificate.main.domain_validation_options)[0].resource_record_name
}

output "acm_validation_cname_value" {
  value = tolist(aws_acm_certificate.main.domain_validation_options)[0].resource_record_value
}

# Waits for the CNAME above to be created at the external DNS provider and for
# AWS to confirm validation, so downstream resources never attach a not-yet-issued cert.
resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [tolist(aws_acm_certificate.main.domain_validation_options)[0].resource_record_name]

  timeouts {
    create = "45m"
  }
}