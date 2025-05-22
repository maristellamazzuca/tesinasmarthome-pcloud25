from flask import Flask, render_template, jsonify
from google.cloud import firestore
import os
import logging

# Parte 3 - Cloud Function: Visualizzazione dei dati salvati in Firestore

# Inizializzazione Flask e configurazione cartelle
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder="static"
)

# Connessione a Firestore
db = firestore.Client()

# Funzione per mostrare i dati quando visitiamo la pagina
@app.route("/", methods=["GET"])
def view_data(request):
    try:
        # Otteniamo il documento "sensor1" dalla collezione "sensors"
        doc_ref = db.collection("sensors").document("sensor1")
        doc = doc_ref.get()

        # Se il documento non esiste, mostriamo una pagina vuota
        if not doc.exists:
            logging.info("Documento 'sensor1' non trovato.")
            return render_template("view_data.html", data=[], headers=[])

        # Prendiamo i dati dal documento
        data = doc.to_dict().get("data", [])

        # Controlliamo che i dati siano in formato lista
        if not isinstance(data, list):
            logging.warning("I dati non sono una lista.")
            return render_template("view_data.html", data=[], headers=[])

        # Creiamo l'intestazione della tabella usando tutte le chiavi presenti nei dati
        headers = sorted(set().union(*(d.keys() for d in data if isinstance(d, dict))))

        # Mostriamo la pagina HTML con i dati
        return render_template("view_data.html", data=data, headers=headers)

    except Exception as e:
        # Se c'è un errore, lo stampiamo e mostriamo un messaggio JSON
        logging.exception("Errore durante la visualizzazione dei dati.")
        return jsonify({"error": f"Errore interno: {str(e)}"}), 500