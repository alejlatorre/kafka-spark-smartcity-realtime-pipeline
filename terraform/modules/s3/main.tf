resource "aws_s3_bucket" "bucket" {
  bucket = "poc-smartcity-spark-kafka"
}

resource "aws_s3_bucket_notification" "stream" {
  bucket = aws_s3_bucket.bucket.id
  queue {
    id            = "send-to-snowpipe"
    queue_arn     = var.snowpipe_sqs_arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "data/vehicle_data/"
    filter_suffix = ".parquet"
  }
}
