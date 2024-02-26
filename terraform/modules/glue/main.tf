# resource "aws_iam_role" "glue_service_role" {
#   name = "glue_service_role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Effect = "Allow"
#       Principal = {
#         Service = "glue.amazonaws.com"
#       }
#     }]
#   })
# }

# resource "aws_iam_policy_attachment" "glue_service_policy" {
#   name       = "glue_service_policy"
#   roles      = [aws_iam_role.glue_service_role.name]
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
# }

# resource "aws_iam_policy_attachment" "s3_full_access_policy" {
#   name       = "s3_full_access_policy"
#   roles      = [aws_iam_role.glue_service_role.name]
#   policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
# }

# resource "aws_glue_catalog_database" "smartcity-db" {
#   name = "poc-smartcity"
# }

# resource "aws_glue_crawler" "smartcity-crawler" {
#   name          = "poc-smartcity-crawler"
#   role          = aws_iam_role.glue_service_role.arn
#   database_name = aws_glue_catalog_database.smartcity-db.name

#   s3_target {
#     path = "s3://poc-smartcity-spark-kafka/data/"
#   }
# }

# TODO: Add configuration to Glue Crawler: https://docs.aws.amazon.com/glue/latest/dg/crawler-configuration.html
