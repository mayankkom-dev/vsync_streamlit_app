resource "aws_iam_role" "vysnc_lambda_role" {
 name   = "terraform_aws_lambda_role"
 assume_role_policy = file("${path.module}/policies/aws_lambda_iam_role.json")
}

# IAM policy for logging from a lambda
resource "aws_iam_policy" "vsync_iam_policy_for_lambda" {
  name         = "aws_iam_policy_for_terraform_aws_lambda_role"
  path         = "/"
  description  = "AWS IAM Policy for managing aws lambda role"
  policy = file("${path.module}/policies/aws_lambda_iam_policy.json")
}

# Policy Attachment on the role.
resource "aws_iam_role_policy_attachment" "magna_attach_iam_policy_to_iam_role" {
  role        = aws_iam_role.vysnc_lambda_role.name
  policy_arn  = aws_iam_policy.vsync_iam_policy_for_lambda.arn
}

