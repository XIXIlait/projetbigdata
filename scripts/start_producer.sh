#!/bin/bash

echo "🚀 Démarrage du producteur Python..."
echo "⏳ Attente que Kafka soit prêt (15 secondes)..."
sleep 15

cd /producer
python sensor_producer.py

