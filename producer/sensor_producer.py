import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "home_sensors"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

ROOMS = ["living_room", "bedroom", "kitchen", "bathroom"]
SENSOR_TYPES = ["temperature", "humidity", "presence", "light"]

def generate_sensor_event():
    """Génère un événement capteur fictif."""
    room = random.choice(ROOMS)
    sensor_type = random.choice(SENSOR_TYPES)
    
    if sensor_type == "temperature":
        value = round(random.uniform(18, 28), 1)
    elif sensor_type == "humidity":
        value = round(random.uniform(30, 70), 1)
    elif sensor_type == "presence":
        value = random.choice([0, 1])
    else:
        value = random.choice([0, 1])
    
    event = {
        "room": room,
        "sensor_type": sensor_type,
        "value": value,
        "timestamp": datetime.now().isoformat(),
        "device_id": f"{room}_{sensor_type}_001"
    }
    
    return event

def main():
    """Envoie des événements dans Kafka toutes les 2 secondes."""
    print(f"Producteur démarré. Envoi vers Kafka ({KAFKA_BROKER})...")
    print(f"Topic : {KAFKA_TOPIC}\n")
    
    try:
        count = 0
        while True:
            event = generate_sensor_event()
            
            producer.send(KAFKA_TOPIC, value=event)
            
            count += 1
            print(f"[{count}] Événement envoyé : {event['room']} - {event['sensor_type']} = {event['value']}")
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nProducteur arrêté.")
    finally:
        producer.close()

if __name__ == "__main__":
    main()

