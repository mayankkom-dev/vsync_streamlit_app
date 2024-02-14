variable "site_packages_path" {
  type = string
}

variable "lambda_deploy" {
  type = string
  default = "lambda_layer"
}

variable "lambda_code" {
  type = string
  default = "lambda_code"
}
