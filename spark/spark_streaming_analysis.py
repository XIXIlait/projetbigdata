from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, avg, max, min, when, sum as spark_sum
from pyspark.sql.functions import from_json, schema_of_json, to_timestamp

spark = SparkSession.builder \
    .appName("SmartHomeAnalysis") \
    .master("local[*]") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .config("spark.hadoop.io.native.lib.available", "false") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("[OK] Spark Session creee")

KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"
KAFKA_TOPIC = "home_sensors"

schema_str = """
{
    "room": "string",
    "sensor_type": "string",
    "value": "double",
    "timestamp": "string",
    "device_id": "string"
}
"""

df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

print("[OK] Connexion Kafka etablie")

df_parsed = df_kafka.select(
    from_json(col("value").cast("string"), schema_of_json(schema_str)).alias("data")
).select("data.*")

df_parsed = df_parsed.withColumn("timestamp_parsed", to_timestamp("timestamp"))
# S'assurer que value est bien numérique
df_parsed = df_parsed.withColumn("value", col("value").cast("double"))

# Ajouter un watermark pour permettre les agrégations en mode append
df_parsed = df_parsed.withWatermark("timestamp_parsed", "0 seconds")

print("[INFO] Schema parse :")
df_parsed.printSchema()

stats_by_room = df_parsed \
    .filter(col("sensor_type").isin("temperature", "humidity")) \
    .groupBy(
        window(col("timestamp_parsed"), "1 minute"),
        col("room"),
        col("sensor_type")
    ).agg(
        avg("value").alias("avg_value"),
        min("value").alias("min_value"),
        max("value").alias("max_value"),
        count("value").alias("count")
    ) \
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("room"),
        col("sensor_type"),
        col("avg_value"),
        col("min_value"),
        col("max_value"),
        col("count")
    )

anomalies = df_parsed.groupBy(
    window(col("timestamp_parsed"), "30 seconds"),
    col("room")
).agg(
    spark_sum(
        ((col("sensor_type") == "light") & (col("value") == 1)).cast("int")
    ).alias("lights_on"),
    
    spark_sum(
        ((col("sensor_type") == "presence") & (col("value") == 1)).cast("int")
    ).alias("presence_detected"),
    
    avg(
        when(col("sensor_type") == "temperature", col("value"))
    ).alias("avg_temp"),
    
    avg(
        when(col("sensor_type") == "humidity", col("value"))
    ).alias("avg_humidity")
) \
.select(
    col("window.start").alias("window_start"),
    col("window.end").alias("window_end"),
    col("room"),
    col("lights_on"),
    col("presence_detected"),
    col("avg_temp"),
    col("avg_humidity")
)

query1 = stats_by_room \
    .writeStream \
    .format("console") \
    .option("truncate", False) \
    .outputMode("update") \
    .start()

import os
import tempfile

checkpoint_path = "/data/output/checkpoint/anomalies_checkpoint"

output_path = "/data/output/anomalies"
os.makedirs(output_path, exist_ok=True)

query2 = anomalies \
    .writeStream \
    .format("csv") \
    .option("path", output_path) \
    .option("checkpointLocation", checkpoint_path) \
    .outputMode("append") \
    .start()

print("[OK] Spark Streaming demarre. Appuyez sur Ctrl+C pour arreter.")

query2.awaitTermination()

