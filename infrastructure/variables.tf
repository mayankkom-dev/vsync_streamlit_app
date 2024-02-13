variable "region" {
  description = "AWS region to create resource in"
  type        = string
  default     = "us-east-1"
}

variable "site_packages_path" {
  type    = string
  default = "Setup your site packages path here"
}
