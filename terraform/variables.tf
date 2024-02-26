variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
}

variable "aws_profile" {
  description = "The AWS profile to use"
  type        = string
}

variable "snowpipe_sqs_arn" {
  description = "The ARN of the SQS queue to send messages to"
  type        = string
}
