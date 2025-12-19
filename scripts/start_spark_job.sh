#!/bin/bash

echo "Démarrage du job Spark Streaming..."
echo "Attente que Kafka soit prêt (20 secondes)..."
sleep 20

cd /spark
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 \
    --master local[*] \
    spark_streaming_analysis.py

