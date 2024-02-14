resource "null_resource" "poetry_dependecy_copy_fast" {
  triggers = {
    # Adding a constant trigger that always changes
    always_run = timestamp()
  }

  provisioner "local-exec" {
     command = "mkdir -p ${path.module}/${var.lambda_deploy_fast}/python && cp -r ${path.module}/../../${var.site_packages_path2}/lib/python3.12/site-packages/* ${path.module}/${var.lambda_deploy_fast}/python" 
  }
}

data "archive_file" "lambda_poetry_dependencies_fast" {
  type        = "zip"
  source_dir  =  "${path.module}/${var.lambda_deploy_fast}"
  output_path = "${path.module}/${var.lambda_deploy_fast}.zip"
  depends_on = [ null_resource.poetry_dependecy_copy_fast ]
}

# Create a lambda layer
resource "aws_lambda_layer_version" "vsync_lambda_layer_fast" {
  filename   = data.archive_file.lambda_poetry_dependencies_fast.output_path
  layer_name = "vsync_lambda_layer_fast"
  compatible_runtimes = [
    "python3.12",
  ]
  source_code_hash = data.archive_file.lambda_poetry_dependencies_fast.output_base64sha256
}

output "fast_rank_zip_check" {
  value = "${path.module}/src"
}

data "archive_file" "fast_embed_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/${var.lambda_code_fast}.zip"
}

# Create a lambda function
resource "aws_lambda_function" "fast_rank_lambda" {
 filename                       = data.archive_file.fast_embed_zip.output_path
 function_name                  = "Fast-Rank-Lambda"
 role                           = aws_iam_role.vsync_fast_lambda_role.arn
 handler                        = "fastembed_wrap.gen_embedding_lambda_handler"
 runtime                        = "python3.12"
 layers = [aws_lambda_layer_version.vsync_lambda_layer_fast.arn]
 depends_on                     = [aws_iam_role_policy_attachment.vsync_fast_attach_iam_policy_to_iam_role]
 source_code_hash = data.archive_file.fast_embed_zip.output_base64sha256
}