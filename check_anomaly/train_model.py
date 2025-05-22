import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from joblib import dump

# Parte 4 - Addestramento del modello di previsione

# Carichiamo il dataset
data = pd.read_csv('client/HomeC.csv')

# Selezioniamo le colonne principali
df = data[[
    'time', 'use [kW]', 'temperature', 'humidity', 'windSpeed',
    'Microwave [kW]', 'Furnace 1 [kW]', 'Solar [kW]'
]].copy()

# Rimuoviamo righe con dati mancanti
df.dropna(inplace=True)

# Convertiamo 'time' in datetime e lo usiamo come indice
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# Aggiungiamo valori precedenti (lag)
df['lag1'] = df['use [kW]'].shift(1)
df['lag2'] = df['use [kW]'].shift(2)
df['lag3'] = df['use [kW]'].shift(3)

# Aggiungiamo se il giorno è weekend
df['is_weekend'] = df.index.weekday >= 5

# Rimuoviamo righe incomplete dopo le shift()
df.dropna(inplace=True)

# Definizione delle feature e del target
X = df[[
    'lag1', 'lag2', 'lag3', 'is_weekend',
    'temperature', 'humidity', 'windSpeed',
    'Microwave [kW]', 'Furnace 1 [kW]', 'Solar [kW]'
]]
y = df['use [kW]']

# Suddividiamo i dati in training e test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Creazione e addestramento del modello
model = LinearRegression()
model.fit(X_train, y_train)

# Salviamo il modello su file per usarlo nella Cloud Function
dump(model, 'model.joblib')
print("Modello addestrato e salvato come 'model.joblib'")