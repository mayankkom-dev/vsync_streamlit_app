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
  role                           = aws_iam_role.vysnc_lambda_role.arn
  layer_name = "vysnc_lambda_layer"
  compatible_runtimes = [
    "python3.10",
  ]
  source_code_hash = data.archive_file.lambda_poetry_dependencies.output_base64sha256
}