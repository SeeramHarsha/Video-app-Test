from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import base64
import io
from PIL import Image
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# API endpoint to generate annotations
@app.route('/generate_annotations', methods=['POST'])
def generate_annotations():
    print("generate_annotations called")
    print(f"GOOGLE_API_KEY: {GOOGLE_API_KEY}")
    try:
        print("Received request at /generate_annotations")
        topic = request.form['topic']
        image_file = request.files['image']

        pass

    except Exception as e:
        print(f"Error getting data: {e}")
        return jsonify({"error": str(e)}), 400

    # Decode the image
    try:
        image = Image.open(io.BytesIO(image_file.read()))
    except Exception as e:
        print(f"Error decoding image: {e}")
        return jsonify({"error": "Invalid image data"}), 400
    
    print(f"Topic: {topic}")

    # Prepare the prompt for Gemini
    prompt = f"""You are an AI assistant that helps professors create annotations for educational videos.

    You are given:
    1. An image (video frame) that may contain a white box drawn on it.
    2. A topic that the professor wants to explain.

    Topic: "{topic}"

    Instructions:
    - Focus on the region marked by the white box in the image.
    - Understand the topic provided.
    - Generate exactly three concise annotation suggestions that describe or explain what is happening in the boxed region in the context of the topic.
    - Do not describe parts of the image outside the boxed region.
    - Return the response in JSON format as follows:

    {{
      "annotations": [
        "First annotation here",
        "Second annotation here",
        "Third annotation here"
      ]
    }}
    """
    try:
        response = model.generate_content([prompt, image])
        print(f"Raw response: {response.text}")
        text = response.text.replace("```json", "").replace("```", "")
        try:
            response_json = json.loads(text)
            print(f"Gemini response: {response_json}")
            response = jsonify(response_json)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw response: {response.text}")
            response = jsonify({"error": "Failed to decode JSON response from Gemini"})
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500
    except Exception as e:
        print(f"Error generating annotations: {e}")
        print(f"Raw response: {response.text}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
