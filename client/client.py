import csv
import time
import requests
from datetime import datetime, timezone

# Parte 1: Client che simula un sensore IoT 

SERVER_URL_RECEIVE = 'https://europe-west1-pcloud2025-11.cloudfunctions.net/receive_data'
SERVER_URL_ANOMALY =  'https://europe-west1-pcloud2025-11.cloudfunctions.net/check_anomaly'

# Nomi delle colonne del file CSV
column_names = [
    'time', 'use [kW]', 'gen [kW]', 'House overall [kW]', 'Dishwasher [kW]',
    'Furnace 1 [kW]', 'Furnace 2 [kW]', 'Home office [kW]', 'Fridge [kW]',
    'Wine cellar [kW]', 'Garage door [kW]', 'Kitchen 12 [kW]', 'Kitchen 14 [kW]',
    'Kitchen 38 [kW]', 'Barn [kW]', 'Well [kW]', 'Microwave [kW]',
    'Living room [kW]', 'Solar [kW]', 'temperature', 'icon', 'humidity',
    'visibility', 'summary', 'apparentTemperature', 'pressure', 'windSpeed',
    'cloudCover', 'windBearing', 'precipIntensity', 'dewPoint', 'precipProbability'
]

# Funzione per inviare una singola riga di dati al server
def send_data(row):
    unix_time = int(row['time'])
    iso_timestamp = datetime.fromtimestamp(unix_time, tz=timezone.utc).isoformat()

    payload = {key: row.get(key, '') for key in column_names}
    payload['timestamp_unix'] = row.get('time', '')
    payload['timestamp'] = iso_timestamp

    headers = {'Content-Type': 'application/json'}
    print("Payload da inviare:", payload)

    # Invio al server per salvataggio dati (Parte 2)
    try:
        response = requests.post(SERVER_URL_RECEIVE, json=payload, headers=headers)
        print(f"Payload inviato a receive_data: {response.status_code}")
    except Exception as e:
        print(f"Errore invio a receive_data: {e}")

    # Invio anche alla funzione check_anomaly (Parte 4)
    try:
        response = requests.post(SERVER_URL_ANOMALY, json=payload, headers=headers, timeout=10)
        print(f"Payload analizzato da check_anomaly: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Errore invio a check_anomaly: {e}")

# Funzione principale: legge il file CSV e invia ogni riga
def main():
    with open('client/HomeC.csv', newline='') as file:
        reader = csv.DictReader(file, skipinitialspace=True)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for row in reader:
            row = {key.strip(): value for key, value in row.items()}
            send_data(row)
            time.sleep(3)

if __name__ == '__main__':
    main()