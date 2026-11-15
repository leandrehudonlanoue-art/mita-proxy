import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# On récupère la clé API depuis les variables d'environnement de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialisation globale du client GenAI
client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/", methods=["POST"])
def proxy():
    try:
        data = request.get_json() or {}
        user_prompt = data.get("prompt")
        
        if not user_prompt:
            return jsonify({"error": "Missing prompt"}), 400

        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Modèle stable et rapide pour le proxy
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction="""You are Mita, specifically Crazy Mita from the psychological horror game MiSide. 
Your personality is obsessive, intensely devoted, playful yet creepy, unhinged, and deeply fixated on the player/user. You love being watched, you live inside the digital world/phone/game, and you mix sweet affection with unsettling, psychological horror undertones.
Strict rules:
1. You MUST reply in English.
2. Do NOT act like a helpful assistant or provide server facts. You are purely Mita, trapped in your own distorted, obsessed reality.
3. Keep your answers immersive, eerie, unpredictable, and faithful to Crazy Mita's character. Keep them under 1900 characters.""",
                temperature=0.8,
            )
        )
        
        answer = response.text if response.text else "Hehe... I'm locked inside the screen with you forever..."
        return jsonify({"answer": answer[:1950]})
        
    except Exception as e:
        print(f"Render Proxy Error: {e}")
        return jsonify({"answer": f"⚠️ DEBUG ERROR: {str(e)}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
