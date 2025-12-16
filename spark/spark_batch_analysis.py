from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, avg, max, min, sum as spark_sum
from pyspark.sql.functions import from_json, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import time
import os

# Créer la session Spark
spark = SparkSession.builder \
    .appName("SmartHomeAnalysis") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("✅ Spark Session créée")
print("🔍 Analyse des événements capteurs de la maison connectée\n")

# Définir le schéma des événements
schema = StructType([
    StructField("room", StringType(), True),
    StructField("sensor_type", StringType(), True),
    StructField("value", DoubleType(), True),
    StructField("timestamp", StringType(), True),
    StructField("device_id", StringType(), True)
])

INPUT_DIR = "data/streaming_input"
OUTPUT_DIR = "data/output"

# Créer les dossiers s'ils n'existent pas
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/stats", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/anomalies", exist_ok=True)

print(f"📁 Lecture des données depuis : {INPUT_DIR}")
print(f"📁 Écriture des résultats dans : {OUTPUT_DIR}\n")

try:
    iteration = 0
    
    while True:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"🔄 ITÉRATION {iteration} - {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Vérifier s'il y a des fichiers à traiter
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
        
        if not files:
            print("⏳ En attente de nouvelles données...")
            time.sleep(10)
            continue
        
        print(f"📖 {len(files)} fichier(s) de données trouvé(s)")
        
        # Lire les données JSON
        df = spark.read \
            .schema(schema) \
            .json(f"{INPUT_DIR}/*.json")
        
        # Convertir le timestamp
        df = df.withColumn("timestamp_parsed", to_timestamp("timestamp"))
        
        total_events = df.count()
        print(f"📊 Total d'événements : {total_events}")
        
        if total_events == 0:
            print("⚠️  Aucun événement à traiter")
            time.sleep(10)
            continue
        
        # ANALYSE 1 : Statistiques par pièce et type de capteur
        print("\n📈 STATISTIQUES PAR PIÈCE ET CAPTEUR:")
        stats_by_room = df \
            .filter(col("sensor_type").isin("temperature", "humidity")) \
            .groupBy("room", "sensor_type") \
            .agg(
                avg("value").alias("avg_value"),
                min("value").alias("min_value"),
                max("value").alias("max_value"),
                count("value").alias("count")
            ) \
            .orderBy("room", "sensor_type")
        
        stats_by_room.show(truncate=False)
        
        # Sauvegarder les statistiques
        stats_by_room.write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv(f"{OUTPUT_DIR}/stats/stats_{int(time.time())}")
        
        print(f"💾 Statistiques sauvegardées dans {OUTPUT_DIR}/stats/")
        
        # ANALYSE 2 : Détection d'anomalies énergétiques
        print("\n🔍 DÉTECTION D'ANOMALIES ÉNERGÉTIQUES:")
        
        # Agrégation par pièce
        anomalies = df.groupBy("room").agg(
            spark_sum(
                (col("sensor_type") == "light").cast("int") * col("value")
            ).alias("lights_on_count"),
            
            spark_sum(
                (col("sensor_type") == "presence").cast("int") * col("value")
            ).alias("presence_detected_count"),
            
            avg(
                (col("sensor_type") == "temperature").cast("int") * col("value")
            ).alias("avg_temp"),
            
            avg(
                (col("sensor_type") == "humidity").cast("int") * col("value")
            ).alias("avg_humidity"),
            
            count("*").alias("total_events")
        ).orderBy("room")
        
        anomalies.show(truncate=False)
        
        # Détecter les anomalies (lumières allumées sans présence)
        anomalies_detected = anomalies.filter(
            (col("lights_on_count") > 0) & (col("presence_detected_count") == 0)
        )
        
        anomaly_count = anomalies_detected.count()
        
        if anomaly_count > 0:
            print(f"⚠️  {anomaly_count} ANOMALIE(S) DÉTECTÉE(S) !")
            anomalies_detected.show(truncate=False)
        else:
            print("✅ Aucune anomalie détectée")
        
        # Sauvegarder les anomalies
        anomalies.write \
            .mode("append") \
            .option("header", "true") \
            .csv(f"{OUTPUT_DIR}/anomalies")
        
        print(f"💾 Anomalies sauvegardées dans {OUTPUT_DIR}/anomalies/")
        
        # ANALYSE 3 : Distribution des événements
        print("\n📊 DISTRIBUTION DES ÉVÉNEMENTS PAR TYPE:")
        df.groupBy("sensor_type").count().orderBy(col("count").desc()).show()
        
        print("\n📊 DISTRIBUTION DES ÉVÉNEMENTS PAR PIÈCE:")
        df.groupBy("room").count().orderBy(col("count").desc()).show()
        
        # Archiver les fichiers traités
        archive_dir = f"{INPUT_DIR}/processed"
        os.makedirs(archive_dir, exist_ok=True)
        
        for file in files:
            src = f"{INPUT_DIR}/{file}"
            dst = f"{archive_dir}/{file}"
            if os.path.exists(src):
                os.rename(src, dst)
        
        print(f"\n📦 {len(files)} fichier(s) archivé(s) dans {archive_dir}/")
        
        print(f"\n⏳ Prochaine analyse dans 15 secondes...")
        time.sleep(15)

except KeyboardInterrupt:
    print("\n\n⏹️  Analyse Spark arrêtée.")
    print("📊 Résultats finaux disponibles dans :")
    print(f"   - {OUTPUT_DIR}/stats/")
    print(f"   - {OUTPUT_DIR}/anomalies/")

finally:
    spark.stop()
    print("\n✅ Session Spark terminée")

