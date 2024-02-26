module "s3" {
  source           = "./modules/s3"
  snowpipe_sqs_arn = var.snowpipe_sqs_arn
}

# module "glue" {
#   source           = "./modules/glue"
# }
