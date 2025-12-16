import json
import time
import random
import os
from datetime import datetime
from pathlib import Path

# Configuration
OUTPUT_DIR = "data/streaming_input"
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
    """Génère des événements et les écrit dans des fichiers JSON."""
    # Créer le dossier de sortie s'il n'existe pas
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Producteur démarré. Génération de flux de données...")
    print(f"📁 Destination : {OUTPUT_DIR}\n")
    
    try:
        count = 0
        batch_events = []
        
        while True:
            event = generate_sensor_event()
            batch_events.append(event)
            
            count += 1
            print(f"[{count}] 📤 Événement généré : {event['room']} - {event['sensor_type']} = {event['value']}")
            
            # Écrire un batch toutes les 10 secondes
            if count % 5 == 0:
                timestamp = int(time.time())
                filename = f"{OUTPUT_DIR}/events_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    for evt in batch_events:
                        f.write(json.dumps(evt) + '\n')
                
                print(f"💾 Batch de {len(batch_events)} événements sauvegardé : {filename}\n")
                batch_events = []
            
            time.sleep(2)
    
    except KeyboardInterrupt:
        # Sauvegarder les événements restants
        if batch_events:
            timestamp = int(time.time())
            filename = f"{OUTPUT_DIR}/events_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                for evt in batch_events:
                    f.write(json.dumps(evt) + '\n')
            
            print(f"\n💾 Derniers événements sauvegardés : {filename}")
        
        print("\n⏹️  Producteur arrêté.")

if __name__ == "__main__":
    main()

