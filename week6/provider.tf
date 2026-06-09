aws provider "aws" {

    region = "us-east-1"

}

terraform {
  
    required_providers {
        aws = {
        source  = "hashicorp/aws"
        version = "~> 4.0"
        }
    }
    }

backend "s3" {
    bucket = "terraform-state-bucket-2024"
    key    = "terraform.tfstate"
    region = "us-east-1"
}