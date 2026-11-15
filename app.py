import os
import time
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/", methods=["POST"])
def proxy():
    data = request.get_json() or {}
    user_prompt = data.get("prompt")
    
    if not user_prompt:
        return jsonify({"error": "Missing prompt"}), 400

    max_retries = 3
    delay = 2
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
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
            last_error = str(e)
            print(f"Attempt {attempt + 1} failed: {e}")
            # Si c'est une erreur 503 / surcharge, on attend un peu et on réessaie
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                time.sleep(delay)
                delay *= 2  # Délai exponentiel (2s, puis 4s)
                continue
            else:
                break

    return jsonify({"answer": f"⚠️ DEBUG ERROR: {last_error}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
