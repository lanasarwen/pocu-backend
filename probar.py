import requests

url = "https://pocu-backend.onrender.com/chat"

payload = {
    "usuario": "Arwen",
    "mensaje": "Pocu, ¿recuerdas qué odio y qué tarea tengo pendiente para hoy?"
}

try:
    response = requests.post(url, json=payload)
    print("Respuesta de Pocu:", response.json())
except Exception as e:
    print("Error:", e)