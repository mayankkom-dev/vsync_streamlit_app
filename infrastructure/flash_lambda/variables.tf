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

variable "improver_code_deploy" {
  type = string
  default = "lambda_improver_code"
}
variable "optimizer_code_deploy" {
  type = string
  default = "lambda_optimizer_code"
}
