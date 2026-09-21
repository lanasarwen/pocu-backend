import requests

url = "https://pocu-backend.onrender.com/chat"

payload = {
    "usuario": "Arwen",
    "mensaje": "Hola Pocu, ¿notas alguna diferencia con tu nueva actualización en la nube?"
}

try:
    response = requests.post(url, json=payload)
    print("Estado:", response.status_code)
    print("Respuesta de Pocu:", response.json())
except Exception as e:
    print("Ocurrió un error:", e)