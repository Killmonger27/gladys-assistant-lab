#!/usr/bin/env python3
"""
Client MQTT pour Gladys Assistant

Ce script simule un capteur de température et d'humidité et envoie
les données périodiquement à Gladys Assistant via MQTT.
"""
import paho.mqtt.client as mqtt # type: ignore
import time
import json
import random
import os
from datetime import datetime


MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")  
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")       
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "python_client")
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", 60))

# Fonction appelée lors de la connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    """Callback exécuté quand le client se connecte au broker MQTT"""
    if rc == 0:
        print(f"Connecté au broker MQTT ({MQTT_BROKER}:{MQTT_PORT})")
        client.subscribe("gladys/commands/#")
    else:
        print(f"Échec de connexion au broker, code retour {rc}")

# Fonction appelée lors de la réception d'un message MQTT
def on_message(client, userdata, msg):
    """Callback exécuté quand un message est reçu sur un topic auquel on est abonné"""
    print(f"Message reçu sur {msg.topic}: {msg.payload.decode()}")
    
    if msg.topic == "gladys/commands/device":
        try:
            command = json.loads(msg.payload.decode())
            print(f"Commande reçue: {command}")
        except json.JSONDecodeError:
            print("Format de commande invalide")

# Fonction pour générer et envoyer des données de capteur simulées
def send_temperature_data(client):
    """Génère des valeurs aléatoires et les publie sur les topics MQTT appropriés"""
    temperature = 20 + random.uniform(-3, 3)  # Entre 17 et 23 degrés
    humidity = 50 + random.uniform(-10, 10)   # Entre 40 et 60%
    
    payload = {
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1),
        "battery": random.randint(90, 100),
        "timestamp": datetime.now().isoformat()
    }
    
    client.publish(
        "gladys/master/device/mqtt:temp_sensor_1/feature/mqtt:temperature/state", 
        payload["temperature"]
    )
    client.publish(
        "gladys/master/device/mqtt:temp_sensor_1/feature/mqtt:humidity/state",
        payload["humidity"]
    )
    client.publish(
        "gladys/master/device/mqtt:temp_sensor_1/feature/mqtt:battery/state",
        payload["battery"]
    )
    
    print(f"Données envoyées: {payload}")

# Fonction principale
def main():
    """Fonction principale qui initialise le client MQTT et gère la boucle d'envoi"""

    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    

    print(f"Tentative de connexion à {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    

    client.loop_start()
    
    try:
        while True:
            # Envoyer des données simulées
            send_temperature_data(client)
            
            
            print(f"Attente de {PUBLISH_INTERVAL} secondes avant le prochain envoi...")
            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        print("Programme interrompu par l'utilisateur")
    finally:
        # Arrêter proprement le client MQTT
        client.loop_stop()
        client.disconnect()
        print("Déconnecté du broker MQTT")

# Point d'entrée du script
if __name__ == "__main__":
    main()