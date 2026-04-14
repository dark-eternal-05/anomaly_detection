# File: spark/stream_processor.py
# This reads from Kafka in micro-batches and processes each batch.

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# ── CREATE SPARK SESSION ───────────────────────────────
# SparkSession is the entry point to Spark
spark = SparkSession.builder \
    .appName("AnomalyDetectionStream") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

# Suppress noisy Spark log messages
spark.sparkContext.setLogLevel("WARN")
print("Spark session started")

# ── DEFINE MESSAGE SCHEMA ──────────────────────────────
# Tell Spark what structure to expect in each Kafka message
schema = StructType([
    StructField("timestamp", StringType(), True),    # "2013-12-10 06:00:00"
    StructField("value",     DoubleType(), True),    # 57.6
    StructField("row_id",    IntegerType(), True),   # 0
])

# ── READ FROM KAFKA ────────────────────────────────────
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "sensor-data") \
    .option("startingOffsets", "latest") \
    .load()

# raw_stream has columns: key, value (bytes), topic, partition, offset, timestamp
# We only need the "value" column — parse it using our schema
parsed_stream = raw_stream.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")   # flatten: data.timestamp → timestamp

# ── PROCESS: FILTER VALID READINGS ────────────────────
# Drop rows where value is null or unrealistic (basic data quality check)
clean_stream = parsed_stream.filter(
    (col("value").isNotNull()) &
    (col("value") > 0) &
    (col("value") < 200)
)

# ── OUTPUT TO CONSOLE (for testing) ───────────────────
query = clean_stream.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

print("Streaming started — press Ctrl+C to stop")
query.awaitTermination()