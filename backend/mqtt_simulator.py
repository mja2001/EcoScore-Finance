import paho.mqtt.client as mqtt
import time
import json
import random

client = mqtt.Client()
client.connect('localhost', 1883)

while True:
  data = {'loan_id': 'test-loan', 'carbon_est': random.uniform(5, 50), 'predicted_carbon_reduction': random.uniform(1000, 2000)}
  client.publish('ecoscore/iot/updates', json.dumps(data))
  time.sleep(10)  # Simulate periodic updates
