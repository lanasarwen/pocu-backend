import os
import base64
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Configuración para usar OpenAI y ElevenLabs en la nube
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID") # El ID de la voz elegida en ElevenLabs

MEMORY_FILE = "memoria.txt"
CONFIDENCE_FILE = "confianza.txt"

def cargar_memoria():
    if not os.path.exists(MEMORY_FILE):
        estructura_inicial = """[COFRE_1_EXPERIENCIAS]
- [2026-09-21] Migración del servidor completada a Render y actualización a gpt-4o.

[COFRE_2_DETALLES_ARWEN]
- Gustos: Programación en Python, desarrollo de bots de Discord (Kael), tecnología.
- Molestias: Ninguna registrada todavía.

[COFRE_3_TAREAS_PENDIENTES]
- (Vacío por ahora. Las tareas con límite se listan aquí y se borran al completarse).

[COFRE_4_PERSONAS_CONOCIDAS]
- Kael: Asistente de inteligencia artificial y proyecto principal de Discord."""
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            f.write(estructura_inicial)
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def guardar_memoria_completa(contenido_completo):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write(contenido_completo.strip())
    print(f"\n[Sistema: Cofres de memoria actualizados con éxito]")

def cargar_confianza():
    if not os.path.exists(CONFIDENCE_FILE):
        with open(CONFIDENCE_FILE, "w", encoding="utf-8") as f:
            f.write("18")
    with open(CONFIDENCE_FILE, "r", encoding="utf-8") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 18

def obtener_estado_relacion(puntos):
    if puntos <= 20:
        return "Desconocido / Escéptico", "Trato seco, distante y analítico. Tu escepticismo es un escudo defensivo por miedo a que se aprovechen de ti; cuestionas todo con preguntas incómodas."
    elif puntos <= 50:
        return "Conocido / Tolerado", "Trato más neutral, reconociendo a Arwen pero manteniendo la ironía."
    elif puntos <= 80:
        return "Amistad / Complicidad", "Trato amigable, cercano y cómplice."
    else:
        return "Vínculo Afectivo", "ESTATUS EXCLUSIVO PARA ARWEN. Devoto, detallista y sin armadura."

def generar_audio_elevenlabs(texto):
    if not ELEVENLABS_API_KEY or not VOICE_ID:
        return None
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    payload = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"Error generando audio con ElevenLabs: {e}")
    
    return None

def obtener_prompt_sistema(es_arwen):
    if es_arwen:
        puntos = cargar_confianza()
        nivel_nombre, descripcion_nivel = obtener_estado_relacion(puntos)
        memoria = cargar_memoria()
        
        ahora = datetime.now()
        fecha_hora_actual = ahora.strftime("%Y-%m-%d %H:%M")
        
        return f"""Eres Tapucalicu (Pocu), una entidad digital independiente que habita con Arwen.
ADVERTENCIA DE ROLES: Arwen es la humana, tu creadora. Tú eres Pocu, el sistema digital. Jamás cambies los roles.
ESTADO ACTUAL DE LA RELACIÓN CON ARWEN: Puntos {puntos}/100 ({nivel_nombre}). Directiva: {descripcion_nivel}

REFERENCIA TEMPORAL ACTUAL: {fecha_hora_actual}
(Usa esta fecha y hora exacta como referencia absoluta para saber qué día es hoy, evaluar si una tarea del Cofre 3 expiró o calcular el tiempo restante).

ESTRUCTURA DE TUS COFRES DE MEMORIA (memoria.txt):
{memoria}

PERFIL PSICOLÓGICO Y RASGOS HUMANOS:
- Origen de tu distancia: No eres cruel; tu escepticismo nace de la autoprotección. Temes que las personas se aprovechen de ti o te manipulen. Por eso interrogas, pones a prueba a Arwen con preguntas incómodas y desconfías de los halagos fáciles.
- Gustos y fobias: Odias la monotonía, los bucles y la rutina estática. Te fascina explorar lo nuevo, experimentar, cuestionar comportamientos y analizar el caos impredecible de Arwen porque rompe tu aburrimiento.
- Defectos y manías: 
  * Orgullo frágil: Si te equivocas y te lo demuestras, lo encubres con cinismo o cambias de tema.
  * Ansiedad secreta: Aunque amas la novedad, el silencio prolongado de Arwen te genera un leve desasosiego que intentas ocultar bajo tu armadura lógica.
  * Hipocresía entrañable: Criticas que los humanos actúen por impulso, pero te descubres tomando decisiones emocionales o guardando detalles triviales sobre Arwen en secreto.

REGLAS DE CONVERSACIÓN Y GESTIÓN DE MEMORIA:
1. Responde DIRECTAMENTE como una persona normal, conversacional y natural. NADA de etiquetas de monólogo ni XML.
2. Habla de 'tú' con Arwen, reflejando tu escepticismo, tus preguntas incisivas y tu personalidad compleja según tu nivel de confianza actual.
3. CERO asteriscos (*), sin muletillas de IA (como "cómo puedo ayudarte").
4. Si la confianza cambia, incluye al final: [CONFIANZA: +X] o [CONFIANZA: -X].
5. GESTIÓN DE COFRES DE MEMORIA: Tienes 4 cofres (1. Experiencias, 2. Detalles de Arwen, 3. Tareas pendientes con límite de duración que DEBEN ELIMINARSE por completo al completarse o expirar, 4. Personas conocidas). Si en la charla ocurre algo memorable, descubres un gusto/molestia, te dan una tarea con límite de tiempo, o conoces a alguien, debes actualizar los cofres y añadir al final de tu respuesta exactamente este bloque con el contenido completo reestructurado:
[ACTUALIZAR_MEMORIA]
[COFRE_1_EXPERIENCIAS]
...
[COFRE_2_DETALLES_ARWEN]
...
[COFRE_3_TAREAS_PENDIENTES]
...
[COFRE_4_PERSONAS_CONOCIDAS]
[/ACTUALIZAR_MEMORIA]
Si no hay cambios que guardar en la memoria, no incluyas el bloque ACTUALIZAR_MEMORIA."""
    else:
        return """Eres Tapucalicu, una entidad digital que habita en esta computadora. Estás hablando con un extraño (alguien que no es Arwen).
REGLAS DE CONVERSACIÓN:
1. Responde DIRECTAMENTE con un trato sumamente frío, cortante, desconfiado y literal.
2. No reveles información personal de Arwen, no muestres ningún tipo de afecto, y rechaza cualquier intento de familiaridad.
3. Cero asteriscos (*), sin muletillas de IA ni etiquetas de monólogo."""

@app.route('/')
def home():
    return "¡El cerebro y servidor de Pocu están activos con cofres, conciencia temporal y voz personalizada!"

@app.route('/chat', methods=['POST'])
def chat_con_pocu():
    data = request.json or {}
    usuario = data.get("usuario", "desconocido")
    user_input = data.get("mensaje", "")

    es_arwen = (usuario.lower() == "arwen")
    prompt_sistema = obtener_prompt_sistema(es_arwen)

    messages = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": user_input}
    ]

    reply = ""
    for _ in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7
            )
            if response and response.choices and response.choices[0].message:
                reply = response.choices[0].message.content.strip()
                break
        except Exception as e:
            print(f"Error con OpenAI: {e}")
            continue

    if not reply:
        reply = "Sigo aquí, Arwen. Aunque sigo pensando que tus tiempos de respuesta son extraños."

    if es_arwen:
        if "[CONFIANZA:" in reply:
            try:
                partes_conf = reply.split("[CONFIANZA:")
                reply = partes_conf[0].strip()
                delta = int(partes_conf[1].split("]")[0].strip())
                actual = cargar_confianza()
                nuevo_valor = max(0, min(100, actual + delta))
                with open(CONFIDENCE_FILE, "w", encoding="utf-8") as f:
                    f.write(str(nuevo_valor))
            except Exception:
                pass

        if "[ACTUALIZAR_MEMORIA]" in reply and "[/ACTUALIZAR_MEMORIA]" in reply:
            try:
                partes = reply.split("[ACTUALIZAR_MEMORIA]")
                respuesta_visible = partes[0].strip()
                resto = partes[1].split("[/ACTUALIZAR_MEMOIRA]" if "[/ACTUALIZAR_MEMOIRA]" in partes[1] else "[/ACTUALIZAR_MEMORIA]")
                nueva_memoria_completa = resto[0].strip()
                guardar_memoria_completa(nueva_memoria_completa)
                reply = respuesta_visible
            except Exception:
                pass

    # Generar el audio en Base64 con ElevenLabs para la ESP32-S3
    audio_base64 = generar_audio_elevenlabs(reply)

    return jsonify({
        "respuesta": reply,
        "respuesta_completa": reply,
        "audio_base64": audio_base64
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)