# ⚡ Instructions Rapides - Dès que Docker est prêt

## ✅ Vérifier que Docker a terminé

Dans Docker Desktop, vous devriez voir :
- ✅ Image `confluentinc/cp-zookeeper:7.4.0` téléchargée
- ✅ Image `confluentinc/cp-kafka:7.4.0` téléchargée

Ou dans le terminal :
```bash
docker-compose ps
```

Vous devriez voir :
```
NAME        STATUS
zookeeper   Up
kafka       Up
```

## 📋 ÉTAPES À SUIVRE (dans l'ordre)

### ÉTAPE 1 : Créer le topic Kafka (2 minutes)

```bash
cd d:\bigdata\projetbigdata

docker exec -it kafka bash

# Une fois dans le conteneur Kafka :
kafka-topics --create --topic home_sensors --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Vérifier que le topic est créé :
kafka-topics --list --bootstrap-server localhost:9092

# Sortir du conteneur :
exit
```

**✅ Résultat attendu :** Vous voyez `home_sensors` dans la liste

---

### ÉTAPE 2 : Lancer le producteur (Terminal 1)

```bash
cd d:\bigdata\projetbigdata
venv\Scripts\activate
python producer/sensor_producer.py
```

**✅ Résultat attendu :**
```
🚀 Producteur démarré. Envoi vers Kafka (localhost:9092)...
📍 Topic : home_sensors

[1] 📤 Événement envoyé : living_room - temperature = 22.5
[2] 📤 Événement envoyé : bedroom - humidity = 55.0
[3] 📤 Événement envoyé : kitchen - presence = 1
...
```

**⚠️ IMPORTANT :** Laisser tourner ce terminal !

---

### ÉTAPE 3 : Lancer Spark (Terminal 2 - NOUVEAU)

Ouvrir un **NOUVEAU terminal** :

```bash
cd d:\bigdata\projetbigdata
venv\Scripts\activate
python spark/spark_streaming_analysis.py
```

**✅ Résultat attendu :**
```
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

+-------------------+-------------------+-----------+-----------+---------+---------+---------+-----+
|window_start       |window_end         |room       |sensor_type|avg_value|min_value|max_value|count|
+-------------------+-------------------+-----------+-----------+---------+---------+---------+-----+
|2025-12-16 15:00:00|2025-12-16 15:01:00|living_room|temperature|22.7     |21.5     |24.1     |15   |
+-------------------+-------------------+-----------+-----------+---------+---------+---------+-----+
```

**🎉 SI VOUS VOYEZ ÇA : LE PROJET FONCTIONNE !**

---

### ÉTAPE 4 : Prendre les screenshots

1. **Terminal producteur** → Capture d'écran
2. **Terminal Spark** → Capture d'écran (avec les tableaux)
3. **Docker Desktop** → Onglet "Containers" montrant kafka et zookeeper "Running"
4. **Explorateur** → `data/output/` avec les fichiers générés

Sauvegarder dans `screenshots/`

---

### ÉTAPE 5 : Arrêter proprement

```bash
# Terminal producteur : Ctrl+C
# Terminal Spark : Ctrl+C

# Arrêter Docker :
docker-compose down
```

---

## 🐛 Problèmes courants

### "kafka: command not found"
→ Vous n'êtes pas dans le conteneur. Relancer `docker exec -it kafka bash`

### "Connection refused to localhost:9092"
→ Kafka n'est pas encore prêt. Attendre 15-20 secondes après `docker-compose up`

### "No module named kafka"
→ Activer le venv : `venv\Scripts\activate`

### Le producteur s'arrête immédiatement
→ Vérifier que Kafka tourne : `docker-compose ps`

---

## ⏱️ TEMPS TOTAL ESTIMÉ

- ✅ Docker terminé : DÉJÀ FAIT
- ⏱️ Créer topic : 2 minutes
- ⏱️ Tester producteur : 1 minute
- ⏱️ Tester Spark : 2 minutes
- ⏱️ Screenshots : 5 minutes
- ⏱️ Git push : 2 minutes

**TOTAL : ~15 minutes une fois Docker prêt !**

