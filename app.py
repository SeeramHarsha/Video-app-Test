from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


@app.route('/generate_annotations', methods=['POST'])
def generate_annotations():
    try:
        # Normalize keys (strip whitespace)
        form_data = {k.strip(): v for k, v in request.form.items()}
        
        topic = form_data.get('topic')
        description = form_data.get('description')
        class_level = form_data.get('class')
        subject = form_data.get('subject')
        image_file = request.files.get('image')

        if not topic or not description or not class_level or not subject or not image_file:
            return jsonify({"error": "Missing topic, description, class, subject, or image"}), 400

        # Save temp file
        ext = image_file.filename.split('.')[-1]
        temp_path = f"temp_{uuid.uuid4()}.{ext}"
        image_file.save(temp_path)

        # SAFEST filename allowed by Gemini SDK
        safe_name = f"file-{uuid.uuid4().hex}"

        # Upload to Gemini
        uploaded = genai.upload_file(
            name=safe_name,                         # MUST be lowercase alphanumeric + dashes
            display_name=image_file.filename,       # original name shown in Gemini Studio
            mime_type=image_file.mimetype,
            path=temp_path
        )

        # Prompt
        prompt = f"""
        You are an AI assistant that generates detailed educational annotations.

        Generate a short title/headline describing the action in the white box.
        Then, generate EXACTLY 3 long, clear, explainable annotations providing details about this action.
        Each annotation must be a sentence.
        Focus ONLY on what is inside the white box.

        Class: "{class_level}"
        Subject: "{subject}"
        Topic: "{topic}"
        Description: "{description}"

        Return JSON only:

        {{
          "headline": "Short title describing the action",
          "annotations": [
            "First detailed annotation.",
            "Second detailed annotation.",
            "Third detailed annotation."
          ]
        }}
        """

        # Generate
        response = model.generate_content([prompt, uploaded])
        text = response.text.replace("```json", "").replace("```", "").strip()

        # Cleanup
        os.remove(temp_path)

        return jsonify(json.loads(text)), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Gemini returned invalid JSON"}), 500
    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
