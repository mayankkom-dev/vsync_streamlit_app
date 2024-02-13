module "lambda_module" {
  source             = "./flash_lambda"
  site_packages_path = var.site_packages_path
  #   s3_bucket_name = "my-s3-bucket"
}