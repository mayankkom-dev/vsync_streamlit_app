module "lambda_module_fast" {
  source             = "./fast_lambda"
  site_packages_path2 = var.site_packages_path2
  #   s3_bucket_name = "my-s3-bucket"
}