-- Create database
create or replace database smartcity;

-- Create parquet file format
create or replace file format sf_tut_parquet_format
type = parquet;

-- Create stage
create or replace stage poc_smartcity_spark_kafka
url = 's3://poc-smartcity-spark-kafka/data/'
credentials = (AWS_KEY_ID = '' AWS_SECRET_KEY = '')
file_format = 'sf_tut_parquet_format';
show stages;

-- Create target
create or replace table prd_kfk__vehicle_data (
    pk string primary key,
    timestamp_pet timestamp_ntz,
    payload object,
    inserted_at timestamp_ntz,
    md__filename string,
    md__file_row_number string,
    md__file_last_modified timestamp_ntz,
    md__start_scan_time timestamp_ntz
) cluster by (pk, timestamp_pet);

-- Test copy into operation (https://docs.snowflake.com/en/user-guide/querying-metadata)
copy into prd_kfk__vehicle_data
from (
    select
        $1:id::string as pk,
        $1:timestamp::timestamp_ntz as timestamp_pet,
        $1 as payload,
        sysdate() as inserted_at,
        metadata$filename as md__filename,
        metadata$file_row_number as md__file_row_number,
        metadata$file_last_modified as md__file_last_modified,
        metadata$start_scan_time as md__start_scan_time
    from @poc_smartcity_spark_kafka/vehicle_data/
    (file_format => 'sf_tut_parquet_format', PATTERN => '.*[.]parquet')
);
select * from prd_kfk__vehicle_data limit 10;

-- Create snowpipe
create or replace pipe pipe__smartcity__prd_kfk__vehicle_data auto_ingest=true as
copy into prd_kfk__vehicle_data
from (
    select
        $1:id::string as pk,
        $1:timestamp as timestamp_pet,
        $1 as payload,
        sysdate() as inserted_at,
        metadata$filename as md__filename,
        metadata$file_row_number as md__file_row_number,
        metadata$file_last_modified as md__file_last_modified,
        metadata$start_scan_time as md__start_scan_time
    from @poc_smartcity_spark_kafka/vehicle_data/
    (file_format => 'sf_tut_parquet_format', PATTERN => '.*[.]parquet')
);

show pipes;

-- Attach notification channel generated to S3 (by Terraform)
-- Send a new file to the S3 bucket to test the snowpipe
select * from prd_kfk__vehicle_data order by inserted_at desc;