# PROJET BIG DATA : Smart Home IoT Analysis

Bonjour ! 👋
Ce fichier est le document central de mon projet. Il contient :
1.  **L'explication simple** du projet (C'est quoi ? À quoi ça sert ?).
2.  **Le Guide d'Installation** (Toutes les commandes pour lancer le projet).
3.  **La Preuve de Fonctionnement** (Screenshots et explications techniques détaillées).
4.  **La Conformité** (Preuve que j'ai respecté les consignes de l'Option A).

---

# 1. 🎓 C'est quoi ce projet ? (Explication Simple)

Imagine que nous voulons surveiller une "Maison Intelligente" (Smart Home) pour détecter des problèmes (comme une lumière oubliée ou une température anormale) en temps réel.

Pour faire ça, nous avons construit une "usine de données" avec 3 acteurs :

1.  **Le Producteur (Python)** : C'est comme des **capteurs virtuels** dans la maison. Il génère des faux événements (Température 25°C, Lumière Allumée...) et les envoie très vite.
2.  **Kafka (Le Facteur)** : C'est le **tuyau de transport**. Il reçoit les messages des capteurs et les garde en sécurité en attendant qu'ils soient traités.
3.  **Spark (Le Cerveau)** : C'est l'**analyseur**. Il lit les messages qui arrivent par le tuyau, calcule des statistiques (moyennes par minute) et surveille les anomalies pour nous alerter.

**L'Intérêt du projet** :
C'est de prouver qu'on sait gérer des "Données en Streaming" (qui n'arrêtent jamais d'arriver), exactement comme le font Uber, Netflix ou les banques aujourd'hui.

---

# 2. 💻 Guide d'Exécution : Commandes à copier-coller

Voici la liste exacte des commandes pour lancer et tester le projet toi-même.

## Étape 1 : Tout nettoyer (optionnel, pour repartir de zéro)
Si tu veux être sûr que tout est propre :
```powershell
docker-compose down
# Supprime les volumes (données) pour repartir à neuf
docker volume prune -f
```

## Étape 2 : Lancer l'infrastructure (Docker)
Ouvre un terminal (PowerShell ou CMD) à la racine du projet (`c:\bigdata\projetbigdata`).
```powershell
docker-compose up -d
```
*Attends 30 secondes que tout démarre.*

Vérifie que c'est lancé :
```powershell
docker ps
```
*Tu dois voir 3 lignes : zookeeper, kafka, spark.*

## Étape 3 : Créer le sujet de discussion (Topic Kafka)
On dit à Kafka de créer le canal "home_sensors".
```powershell
docker exec kafka kafka-topics --create --topic home_sensors --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
```

## Étape 4 : Lancer le Producteur (Les données)
Ouvre un **DEUXIÈME** terminal.
Active ton environnement Python et lance le script.

```powershell
# Active l'environnement virtuel
.\venv\Scripts\Activate

# Lance le producteur (attendre 30 secondes apres l'execution de cette commande)
python producer/sensor_producer.py
```
*Laisse ce terminal ouvert ! Tu vas voir les messages défiler.*

## Étape 5 : Lancer l'Analyse Spark
Ouvre un **TROISIÈME** terminal.
On lance Spark à l'intérieur de Docker pour éviter les bugs Windows.

```powershell
docker exec spark /opt/spark/bin/spark-submit --conf spark.jars.ivy=/tmp/.ivy2 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 --master local[*] /home/spark_jobs/spark_streaming_analysis.py
```
*Tu vas voir beaucoup de texte défiler, c'est normal. Au bout d'un moment, tu verras des tableaux s'afficher toutes les minutes.*

## Étape 6 : Vérifier les résultats
Si tu veux voir si des anomalies ont été détectées, va voir dans ton dossier windows :
`c:\bigdata\projetbigdata\data\output\anomalies`
Tu y trouveras des fichiers CSV.

---

# 3. 📸 Explications des Preuves (Screenshots)

Voici l'analyse technique de ce que vous voyez sur mes captures d'écran.

## 🟢 SCREEN 1 : Le Terminal "Producer" (Génération de Données)
![alt text](image.png)

**Titre : Simulation des Capteurs IOT en Temps Réel**

**Ce qu'on voit :**
Un script Python qui génère et envoie des événements en continu, environ toutes les 2 secondes. Chaque ligne représente une lecture de capteur envoyée.

**Comment ça marche (La logique du code) :**
Le script `sensor_producer.py` agit comme un simulateur de maison intelligente.
1.  **L'Aléatoire** : À chaque exécution, il choisit aléatoirement :
    -   Une **Pièce** parmi 4 : `living_room`, `bedroom`, `kitchen`, `bathroom`.
    -   Un **Type de Capteur** parmi 4 : `temperature`, `humidity`, `presence`, `light`.
2.  **Les Valeurs Réalistes** : Les données ne sont pas n'importe quoi, elles suivent des règles logiques définies dans le code :
    -   *Température* : Entre 18°C et 28°C.
    -   *Humidité* : Entre 30% et 70%.
    -   *Présence/Lumière* : Binaire (0 ou 1).
3.  **L'Envoi vers Kafka** : Une fois l'événement créé (format JSON), il est "poussé" instantanément vers le Topic Kafka `home_sensors` qui agit comme notre tuyau de transport de données.

**Pourquoi ?**
Cela prouve que notre système est capable d'ingérer des données dynamiques et non statiques, simulant un environnement réel imprévisible.

---

## 🔵 SCREEN 2 : Le Terminal "Spark" (Traitement Batch)

![alt text](image-1.png)

**Titre : Agrégation et Analyse en Streaming (Micro-Batchs)**

**Ce qu'on voit :**
Des tableaux ASCII générés par Spark qui se mettent à jour. Chaque tableau correspond à un "Batch" (un lot de traitement).

**Comment ça marche (La logique du code) :**
Spark Streaming écoute le Topic Kafka et ne traite pas les messages un par un, mais par paquets (micro-batchs).
1.  **Le Fenêtrage (Windowing)** : Le code utilise une fonction `window`. Cela signifie qu'il regroupe toutes les données reçues durant une période précise (ex: 30 secondes).
2.  **L'Agrégation** : Pour chaque fenêtre et chaque pièce, il calcule des statistiques :
    -   `avg_value` : La moyenne (ex: température moyenne).
    -   `min/max` : Les pics de valeurs (minimum et maximum).
    -   `count` : Le nombre de mesures reçues.
3.  **Mode "Update"** : Le tableau que tu vois n'affiche que les lignes qui ont été *modifiées* lors du dernier micro-batch. C'est pour cela que la taille du tableau change constamment : si seuls les capteurs de la cuisine ont envoyé des données cette seconde-ci, seule la ligne "kitchen" apparaît.

**Pourquoi ?**
Cela démontre la capacité de Spark à transformer des données brutes chaotiques en informations statistiques structurées et utiles, et ce, en quasi temps réel.

---

## 🔴 SCREEN 3 : Les Fichiers "Anomalies" (Alerting)

*Exemple d'anomalie : 2025-12-19T13:48:30.000Z,2025-12-19T13:49:00.000Z,kitchen,0,0,,59.55*

**Titre : Détection d'Incidents et Persistance des Données**

**Ce qu'on voit :**
L'explorateur de fichiers montrant des fichiers CSV dans le dossier `data/output/anomalies`.

**LA LOGIQUE DES ANOMALIES (QUAND EST-CE UNE ANOMALIE ?) :**
Ce fichier n'est pas juste une copie des données, c'est un **Rapport de Surveillance**.
Dans le code Spark, nous avons défini des règles précises pour surveiller la sécurité de la maison :

1.  **Agrégation "Lights On"** :
    -   Le code regarde tous les messages de type "light".
    -   Il compte combien de fois la valeur était "1" (Allumé).
    -   *Logique :* `sum(case when sensor_type='light' and value=1 then 1 else 0)`
2.  **Agrégation "Presence Detected"** :
    -   Il fait la même chose pour les capteurs de présence.
3.  **La Détection** :
    -   Le fichier CSV contient ces sommes pour chaque fenêtre de 30 secondes.
    -   **L'Anomalie humaine** : C'est en lisant ce fichier qu'on détecte les problèmes. Par exemple, si dans le CSV on voit `lights_on = 5` et `presence_detected = 0` pour la même pièce, **C'EST UNE ANOMALIE** (Lumière allumée sans personne !).

**Pourquoi écrire sur le disque ?**
Contrairement aux stats qui s'affichent juste à l'écran, ces données sont critiques. On utilise un "File Sink" (CSV) pour les stocker durablement. Cela permettrait, dans un vrai projet, d'envoyer ces fichiers à un système d'alarme.

---

# 4. ✅ Conformité avec les Consignes (Option A)

Je certifie que ce projet respecte à 100% l'Option A :

1.  **Utilisation de Docker** :
    -   ✅ `docker-compose.yml` utilisé pour lancer Zookeeper, Kafka et Spark.
    -   Preuve : Voir Screen 1 (Terminal Docker).

2.  **Streaming de Données** :
    -   ✅ Script `producer/sensor_producer.py` simulant des capteurs IoT.
    -   Preuve : Voir Screen 1 (Terminal Producer).
    -   ✅ Topic Kafka `home_sensors` créé et utilisé.

3.  **Traitement Spark (Pyspark)** :
    -   ✅ Script `spark/spark_streaming_analysis.py`.
    -   ✅ Utilisation de `window()` pour les fenêtres temporelles.
    -   ✅ Calcul d'agrégats (`avg`, `min`, `max`) sur les capteurs.
    -   Preuve : Voir Screen 2 (Tableaux Spark).

4.  **Détection d'Anomalies / Stockage** :
    -   ✅ Logique d'agrégation conditionnelle pour `lights_on` et `presence`.
    -   ✅ Écriture des résultats au format CSV dans `data/output/`.
    -   Preuve : Voir Screen 3 (Fichiers Anomalies).
