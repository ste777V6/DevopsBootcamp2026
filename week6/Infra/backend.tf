terraform {
  backend "s3" {
    bucket       = "devops-bootcamp-terraform-state"
    key          = "infra/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}