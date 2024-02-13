variable "site_packages_path" {
  type = string
}

variable "lambda_deploy" {
  type = string
  default = "lambda_layer"
}

variable "improver_code_deploy" {
  type = string
  default = "lambda_improver_code"
}
variable "optimizer_code_deploy" {
  type = string
  default = "lambda_optimizer_code"
}
