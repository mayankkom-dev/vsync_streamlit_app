terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }

  backend "s3" {
    bucket = "terraform-state-vslambda"
    key    = "ecrterraform.tfstate"
    region = "us-east-1"
  }
}
