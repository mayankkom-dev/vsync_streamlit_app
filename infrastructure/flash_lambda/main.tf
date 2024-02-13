resource "null_resource" "poetry_dependecy_copy" {
  triggers = {
    # Adding a constant trigger that always changes
    always_run = timestamp()
  }

  provisioner "local-exec" {
     command = "mkdir -p ${path.module}/${var.lambda_deploy}/python && cp -r ${path.module}/../../${var.site_packages_path}/lib/python3.10/site-packages/* ${path.module}/${var.lambda_deploy}/python" 
  }
}

data "archive_file" "lambda_poetry_dependencies" {
  type        = "zip"
  source_dir  =  "${path.module}/${var.lambda_deploy}"
  output_path = "${path.module}/${var.lambda_deploy}.zip"
  depends_on = [ null_resource.poetry_dependecy_copy ]
}

# Create a lambda layer
resource "aws_lambda_layer_version" "vysnc_lambda_layer" {
  filename   = data.archive_file.lambda_poetry_dependencies.output_path
  layer_name = "vysnc_lambda_layer"
  compatible_runtimes = [
    "python3.10",
  ]
  source_code_hash = data.archive_file.lambda_poetry_dependencies.output_base64sha256
}

data "archive_file" "flash_rank_zip" {
  type        = "zip"
  source_dir  = " ${path.module}/src"
  output_path = "${path.module}/${var.lambda_code}.zip"
}

# Create a lambda function
resource "aws_lambda_function" "flash_rank_lambda" {
 filename                       = data.archive_file.flash_rank_zip.output_path
 function_name                  = "Flash-Rank-Lambda"
 role                           = aws_iam_role.vysnc_lambda_role.arn
 handler                        = "flash_rank.rank_query_lambda_handler"
 runtime                        = "python3.10"
 layers = [aws_lambda_layer_version.vysnc_lambda_layer.arn]
 depends_on                     = [aws_iam_role_policy_attachment.vsync_attach_iam_policy_to_iam_role]
 source_code_hash = data.archive_file.flash_rank_zip.output_base64sha256
}