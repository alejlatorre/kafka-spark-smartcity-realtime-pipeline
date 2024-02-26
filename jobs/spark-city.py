from helpers.utils import get_env
from main import GPS_TOPIC, VEHICLE_TOPIC
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

AWS_ACCESS_KEY_ID = get_env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET = get_env("AWS_BUCKET")


def main():
    spark = (
        SparkSession.builder.appName("SmartCityStreaming")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
            + "org.apache.hadoop:hadoop-aws:3.3.6,"
            + "com.amazonaws:aws-java-sdk:1.12.666",
        )
        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )
        .config(
            "spark.hadoop.fs.s3a.access.key",
            AWS_ACCESS_KEY_ID,
        )
        .config(
            "spark.hadoop.fs.s3a.secret.key",
            AWS_SECRET_ACCESS_KEY,
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        .getOrCreate()
    )

    # Adjust the log level to minimize the console output on executors
    spark.sparkContext.setLogLevel("WARN")

    # Vehicle schema
    vehicleSchema = StructType(
        [
            StructField("id", StringType(), True),
            StructField("deviceId", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("location", StringType(), True),
            StructField("speed", DoubleType(), True),
            StructField("direction", StringType(), True),
            StructField("make", StringType(), True),
            StructField("model", StringType(), True),
            StructField("year", IntegerType(), True),
            StructField("fuelType", StringType(), True),
        ]
    )

    # GPS schema
    gpsSchema = StructType(
        [
            StructField("id", StringType(), True),
            StructField("deviceId", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("speed", DoubleType(), True),
            StructField("direction", StringType(), True),
            StructField("vehicleType", StringType(), True),
        ]
    )

    def read_kafka_topic(topic, schema):
        return (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "broker:29092")
            .option("subscribe", topic)
            .option("startingOffsets", "earliest")
            .load()
            .selectExpr("CAST(value AS STRING)")
            .select(from_json(col("value"), schema).alias("data"))
            .select("data.*")
            .withWatermark("timestamp", "2 minutes")
        )

    def stream_writer(input, checkpoint_folder, output):
        return (
            input.writeStream.format("parquet")
            .option("path", output)
            .option("checkpointLocation", checkpoint_folder)
            .outputMode("append")
            .start()
        )

    vehicleDF = read_kafka_topic(VEHICLE_TOPIC, vehicleSchema).alias("vehicle")
    gpsDF = read_kafka_topic(GPS_TOPIC, gpsSchema).alias("gps")

    query_1 = stream_writer(
        input=vehicleDF,
        checkpoint_folder=f"s3a://{AWS_BUCKET}/checkpoints/{VEHICLE_TOPIC}",
        output=f"s3a://{AWS_BUCKET}/data/{VEHICLE_TOPIC}",
    )
    query_2 = stream_writer(
        input=gpsDF,
        checkpoint_folder=f"s3a://{AWS_BUCKET}/checkpoints/{GPS_TOPIC}",
        output=f"s3a://{AWS_BUCKET}/data/{GPS_TOPIC}",
    )
    query_2.awaitTermination()


if __name__ == "__main__":
    main()
