import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/", methods=["GET"])
def health_check():
    return "Mita Proxy is awake!", 200

@app.route("/", methods=["POST"])
def proxy():
    try:
        data = request.get_json() or {}
        user_prompt = data.get("prompt", "")
        
        if not user_prompt:
            return jsonify({"answer": "Hehe... you didn't say anything..."}), 400

        # Liste de modèles testés en cascade si l'un d'eux est surchargé (503)
        models_to_try = ["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        last_error = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
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
                if response and response.text:
                    answer = response.text
                    return jsonify({"answer": answer[:1950]})
            except Exception as model_err:
                last_error = str(model_err)
                continue # Passe au modèle suivant si celui-ci échoue

        return jsonify({"answer": f"⚠️ RENDER ERROR: All models failed. Last error: {last_error}"}), 200
        
    except Exception as e:
        print(f"Render Error: {e}")
        return jsonify({"answer": f"⚠️ RENDER ERROR: {str(e)}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
