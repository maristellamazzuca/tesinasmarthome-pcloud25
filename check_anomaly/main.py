from google.cloud import firestore
import joblib
import numpy as np
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

# Parte 4 - Controllo anomalie e invio email

db = firestore.Client()

SOGLIA_DELTA = 0.5
MODELLO_PATH = "model.joblib"

# Credenziali per inviare email 
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# === DEBUG: stampa le variabili (solo per test temporaneo) ===
print("DEBUG - EMAIL_FROM:", EMAIL_FROM)
print("DEBUG - EMAIL_TO:", EMAIL_TO)
print("DEBUG - EMAIL_PASSWORD:", "SET" if EMAIL_PASSWORD else "MISSING")

# Funzione che verifica se la data è nel weekend
def is_weekend(timestamp_iso):
    data = datetime.fromisoformat(timestamp_iso)
    return int(data.weekday() >= 5)

# Funzione principale della Cloud Function: controlla se il valore ricevuto è anomalo
def check_anomaly(request):
    dati = request.get_json()
    if not dati or "timestamp" not in dati or "use [kW]" not in dati:
        return "Dati mancanti", 400

    try:
        modello = joblib.load(MODELLO_PATH)
        documento = db.collection("sensors").document("sensor1").get()
        storico = documento.to_dict().get("data", [])

        # Controllo che ci siano almeno 3 valori per costruire i lag
        last_values = [float(x["use [kW]"]) for x in storico if "use [kW]" in x]
        if len(last_values) < 3:
            return "Dati insufficienti per la previsione", 200

        # Preparo i valori precedenti (lag)
        lag1 = last_values[-1]
        lag2 = last_values[-2]
        lag3 = last_values[-3]
        weekend = is_weekend(dati["timestamp"])

        # Prelevo le altre feature necessarie per il modello
        temperature = float(dati.get("temperature", 0))
        humidity = float(dati.get("humidity", 0))
        windSpeed = float(dati.get("windSpeed", 0))
        microwave = float(dati.get("Microwave [kW]", 0))
        furnace1 = float(dati.get("Furnace 1 [kW]", 0))
        solar = float(dati.get("Solar [kW]", 0))

        # Input finale da passare al modello
        input_model = np.array([[lag1, lag2, lag3, weekend,
                                 temperature, humidity, windSpeed,
                                 microwave, furnace1, solar]])

        # Calcolo previsione e confronto con il valore reale
        previsto = modello.predict(input_model)[0]
        reale = float(dati["use [kW]"])

        # Se la differenza è troppo alta, invio una email
        if abs(reale - previsto) > SOGLIA_DELTA:
            invia_email(dati["timestamp"], reale, previsto)
            return "Anomalia rilevata", 200
        return "Valore regolare", 200
    except Exception as errore:
        return f"Errore interno: {errore}", 500

# Funzione che invia una email di notifica quando viene rilevata un'anomalia
def invia_email(timestamp, valore, previsto):
    contenuto = (
        f"Ciao!\n\n"
        f"Abbiamo rilevato una possibile anomalia nei consumi della smart tua home.\n\n"
        f"Data e ora: {timestamp}\n"
        f"Consumo reale: {valore:.3f} kW\n"
        f"Consumo previsto: {previsto:.3f} kW\n"
        f"Differenza nel consumo: {abs(valore - previsto):.3f} kW\n\n"
        f"Ti consigliamo di controllare se tutto è regolare."
    )

    messaggio = MIMEText(contenuto)
    messaggio["Subject"] = "Attenzione: anomalia nei consumi della tua smart home."
    messaggio["From"] = EMAIL_FROM
    messaggio["To"] = EMAIL_TO

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(messaggio)