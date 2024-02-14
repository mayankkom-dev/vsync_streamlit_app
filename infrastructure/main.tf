module "lambda_module_flash" {
  source             = "./flash_lambda"
  site_packages_path = var.site_packages_path
  #   s3_bucket_name = "my-s3-bucket"
}

module "lambda_module_fast" {
  source             = "./fast_lambda"
  site_packages_path2 = var.site_packages_path2
  #   s3_bucket_name = "my-s3-bucket"
}