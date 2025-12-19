# BIG DATA PROJECT: Smart Home IoT Analysis

This file presents our final Big Data project.

We chose **Option A (Technical Project)** to set up a real-time data processing pipeline.

---

# 1. Project Presentation

The objective is to simulate and monitor a "Smart Home" to detect anomalies in real-time (e.g., a light left on in an empty room).

Our technical architecture ("pipeline") consists of 3 parts:

1.  **The Producer (Python)**: It simulates the home's sensors. It sends data (Temperature, Light...) continuously.
2.  **Kafka**: This is the messaging system that receives and stores data temporarily.
3.  **Spark Streaming**: This is the calculation engine that reads the data, calculates statistics (averages), and detects problems.

**Project Interest**:
Demonstrate that we can process infinite data streams (Streaming) just like major companies do for live analysis.

---

# 2. Execution Guide

Here are the commands to launch the project on your machine.

## Step 1: Cleanup (Optional)
To start on a clean slate:
```powershell
docker-compose down
docker volume prune -f
```

## Step 2: Launch Infrastructure
In the project folder:
```powershell
docker-compose up -d
```
Wait about 30 seconds for the services (Zookeeper, Kafka, Spark) to be ready.
You can verify with `docker ps`.

## Step 3: Create Kafka Topic
We create the discussion channel "home_sensors" for our data.
```powershell
docker exec kafka kafka-topics --create --topic home_sensors --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
```

## Step 4: Launch Producer (Data)
Open a **second terminal**.
Activate the virtual environment and run the Python script.

```powershell
# 1. Create environment (if not already done)
python -m venv venv

# 2. Activate
.\venv\Scripts\Activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch
python producer/sensor_producer.py
```
Leave this terminal open to see the data being sent.

## Step 5: Launch Spark (Analysis)
Open a **third terminal**.
We run Spark via Docker to avoid Windows compatibility issues.

```powershell
docker exec spark /opt/spark/bin/spark-submit --conf spark.jars.ivy=/tmp/.ivy2 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 --master local[*] /home/spark_jobs/spark_streaming_analysis.py
```
The statistics tables will appear in this terminal.

**Verifying results:**
Alert files are generated in the folder: `c:\bigdata\projetbigdata\data\output\anomalies`.

---

# 3. Technical Explanation (Screenshots)

## SCREEN 1: Data Generation (Producer)
![alt text](image.png)

**What we see:**
Our Python script `sensor_producer.py` sending JSON messages to Kafka.

**How it works:**
The script randomly chooses a room (e.g., Living Room) and a sensor (e.g., Temperature), generates a realistic value (between 18 and 28°C for temperature), and sends it to the Kafka server. This simulates the activity of the house.

---

## SCREEN 2: Spark Processing (Batches)
![alt text](image-1.png)

**What we see:**
Spark displays the statistics calculated on the data received during the last minute.

**How it works:**
Spark uses "Structured Streaming". It slices the continuous data stream into small groups (1-minute windows). For each group, it calculates the average, min, and max. The "Update" mode allows displaying only what changes.

---

## SCREEN 3: Anomaly Detection
*Example of generated file*
![alt text](image-3.png)

**What we see:**
CSV files created automatically when an anomaly is detected.

**Detection Logic:**
We programmed a simple rule: If `Light = On` AND `Presence = 0` (no one in the room), then it is an anomaly.
Spark writes these critical cases to the hard drive so we keep a trace (unlike stats which are just displayed).

**Note on file names (`part-000...`)**:
Spark gives these complex names (UUID) because it is designed to work on multiple servers at the same time, which avoids file name conflicts.

---

# 4. Compliance (Option A)

This project respects the guidelines of Option A:

1.  **Docker**: Utilization of `docker-compose.yml` for the entire infrastructure.
2.  **Streaming**: Utilization of Kafka and a Python producer script.
3.  **Spark**: Processing with PySpark and Structured Streaming (windowing).
4.  **Storage**: Saving results in CSV.

---

## Installation Notes (Problems encountered)
During the project, we had to solve a few technical issues:
*   **Ivy Error on Docker**: Spark couldn't write its temporary files. We added the option `--conf spark.jars.ivy=/tmp/.ivy2`.
*   **Kafka Connection**: For the producer (Windows) and Spark (Docker) to talk to the same Kafka, we had to configure the `ADVERTISED_LISTENERS` correctly in the docker-compose.
*   **Winutils.exe**: We didn't need to install this Windows patch because we use Spark via Docker (Linux), which is more stable.

---
**Authors:** Alexis & Rodin
**Date:** 19/12/2025
**Technos:** Python, Kafka, Spark Structured Streaming, Docker.
