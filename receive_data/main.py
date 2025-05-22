from flask import Flask, request, jsonify
from google.cloud import firestore
import logging

# Parte 2 - Cloud Function: ricezione e salvataggio dati

# Inizializziamo Flask e Firestore
app = Flask(__name__)
db = firestore.Client()

# Configuriamo i log per vedere eventuali errori
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route("/receive_data", methods=["POST"])
def receive_data(request):
    try:
        # Controlliamo che la richiesta sia in formato JSON
        if not request.is_json:
            logging.error("La richiesta non è in formato JSON.")
            return jsonify({"error": "Content-Type deve essere application/json"}), 415

        # Prendiamo i dati dal corpo della richiesta
        data = request.get_json()
        logging.info(f"Dati ricevuti: {data}")

        # Controlliamo che i campi richiesti siano presenti
        if not data or "timestamp" not in data or "use [kW]" not in data:
            logging.error("Dati mancanti: servono 'timestamp' e 'use [kW]'.")
            return jsonify({"error": "Dati incompleti: 'timestamp' e 'use [kW]' sono obbligatori."}), 400

        # Proviamo a convertire il valore in numero
        try:
            use_kw = float(data["use [kW]"])
        except ValueError:
            logging.error(f"Valore non valido per 'use [kW]': {data['use [kW]']}")
            return jsonify({"error": "'use [kW]' deve essere un numero."}), 400

        # Collezione e documento dove salvare i dati
        doc_ref = db.collection("sensors").document("sensor1")

        # Se il documento esiste, aggiungiamo i nuovi dati all'array "data"
        if doc_ref.get().exists:
            doc_ref.update({"data": firestore.ArrayUnion([data])})
            logging.info("Dato aggiunto al documento esistente.")
        else:
            # Se il documento non esiste, lo creiamo con il primo dato
            doc_ref.set({"data": [data]})
            logging.info("Creato nuovo documento con il primo dato.")

        return jsonify({"message": "Dati salvati con successo."}), 200

    except Exception as e:
        # In caso di errore generico
        logging.exception("Errore durante il salvataggio dei dati.")
        return jsonify({"error": "Errore interno del server."}), 500