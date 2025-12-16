# 🏠 Gardien d'une Maison Connectée - Projet Big Data

## Résumé du projet

Ce projet utilise **Kafka** et **Spark** pour surveiller en temps réel une maison connectée fictive.  
Des capteurs simulés envoient des événements (température, humidité, présence, lumières) via Kafka,  
et Spark les analyse en continu pour détecter des comportements et anomalies énergétiques.

## Architecture

```
Producteur Python → Kafka Topic → Spark Streaming → Fichiers CSV
```

## Outils utilisés

- **Apache Kafka** : Message broker temps réel
- **Apache Spark** : Moteur d'analyse distribué
- **Docker / Docker Compose** : Orchestration des services
- **Python** : Producteur Kafka et job Spark

## Structure du projet

```
projetbigdata/
├── docker-compose.yml
├── README.md
├── requirements.txt
├── producer/
│   └── sensor_producer.py
├── spark/
│   └── spark_streaming_analysis.py
├── data/
│   ├── input/
│   │   └── sample_events.csv
│   └── output/
├── scripts/
│   ├── start_producer.sh
│   └── start_spark_job.sh
└── screenshots/
```

## Installation

### 1. Clonage du dépôt

```bash
git clone https://github.com/TON_USERNAME/projetbigdata.git
cd projetbigdata
```

### 2. Création et activation de l'environnement virtuel

```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Installation des dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Lancer le projet

### 1. Démarrer l’infrastructure Docker (Kafka + Zookeeper)

```bash
docker-compose up -d
docker-compose ps
```

Vous devez voir au minimum les services :

- `zookeeper` en **Up**
- `kafka` en **Up**

### 2. Créer le topic Kafka

```bash
docker exec -it kafka bash

# Dans le conteneur kafka :
kafka-topics --create --topic home_sensors --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

kafka-topics --list --bootstrap-server localhost:9092

exit
```

Vous devez voir `home_sensors` dans la liste.

### 3. Lancer le producteur (Terminal 1)

Assurez-vous que votre venv est activé, puis :

```bash
cd projetbigdata   # si besoin
venv\Scripts\activate   # Windows

python producer/sensor_producer.py
```

Sortie attendue :

```text
🚀 Producteur démarré. Envoi vers Kafka (localhost:9092)...
📍 Topic : home_sensors

[1] 📤 Événement envoyé : living_room - temperature = 22.5
[2] 📤 Événement envoyé : bedroom - humidity = 55.0
[3] 📤 Événement envoyé : kitchen - presence = 1
...
```

### 4. Lancer Spark Streaming (Terminal 2)

Dans un **nouveau** terminal :

```bash
cd projetbigdata
venv\Scripts\activate   # Windows

python spark/spark_streaming_analysis.py
```

Sortie attendue :

```text
✅ Spark Session créée
📖 Connexion Kafka établie
🔍 Schéma parsé :
root
 |-- room: string
 |-- sensor_type: string
 |-- value: double
 |-- timestamp: string
 |-- device_id: string

✅ Spark Streaming démarré. Appuyez sur Ctrl+C pour arrêter.
```

Puis des tableaux de statistiques apparaissent régulièrement dans la console.

### 5. Résultats générés

Les résultats d’analyse sont écrits au format CSV dans :

```bash
data/output/anomalies/
```

Vous pouvez les afficher, par exemple :

```bash
dir data\output\anomalies   # Windows
cat data/output/anomalies/part-*.csv
```

### 6. Arrêt propre

```bash
# Terminal producteur
Ctrl+C

# Terminal Spark
Ctrl+C

# Services Docker
docker-compose down
```

## Captures d’écran

À déposer dans le dossier `screenshots/` :

### Producteur en action

Le producteur envoie des événements capteurs toutes les 2 secondes à Kafka.

![Producer](./screenshots/producer.png)

### Spark Streaming

Spark reçoit et analyse les données en temps réel et affiche les statistiques.

![Spark](./screenshots/spark.png)

### Docker containers

Vérification que les services tournent correctement.

![Docker](./screenshots/docker.png)

### Résultats générés

Les fichiers CSV contenant les détections / agrégations.

![Output](./screenshots/output.png)

## My Setup Notes

### Défi 1 : Communication Docker (résolu ✅)

**Problème** : Au départ, Spark ne pouvait pas se connecter à Kafka avec `localhost:9092` depuis certains environnements.  
**Cause** : En Docker, les conteneurs communiquent via les **noms de services** (`kafka`, `zookeeper`) et non via `localhost`.  
**Solution** : Utiliser `localhost:9092` côté scripts Python (car ils tournent en local) et s’assurer que le `docker-compose.yml` expose bien ce port depuis le conteneur Kafka.  
**Apprentissage** : Toujours distinguer l’hôte (machine locale) et le réseau interne Docker.

### Défi 2 : Virtual Environment Python (résolu ✅)

**Problème** : Difficultés à installer / utiliser `pyspark`.  
**Cause** : Conflits de versions Python / Java ou absence de JDK dans certains cas.  
**Solution** : Créer un venv dédié au projet, installer Java 11+ si nécessaire, puis installer `pyspark` dans ce venv.  
**Apprentissage** : Isoler les dépendances par projet simplifie énormément le débogage.

## Concepts Big Data

1. **Streaming** : Traitement continu de flux de données (événements capteurs en temps réel).  
2. **Windowing** : Agrégations sur des fenêtres temporelles (moyennes par minute, etc.).  
3. **Scalabilité** : Kafka + Spark peuvent gérer des volumes d’événements très importants.  
4. **Temps réel** : Faible latence entre la production de l’événement et son analyse.

## Auteur

Ton Nom – Décembre 2025

## Références

- [Apache Kafka – Documentation](https://kafka.apache.org/documentation/)
- [Apache Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
