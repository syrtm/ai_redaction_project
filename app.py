import spacy
import re
import logging
from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger, swag_from
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logging.error("Failed to load spaCy model: %s", e)
    raise e

def mask_sensitive_info(text, mode="partial", return_details=False):
    """
    Masks sensitive information in the text.
    
    Parameters:
      - text (str): The input text.
      - mode (str): "partial" (default) shows the first character and masks the rest; "full" redacts completely.
      - return_details (bool): If True, returns detailed info about each masked item.
    
    Returns:
      - If return_details is False: a string with masked text.
      - If True: a dict with 'masked_text' and 'details' (a list of dictionaries).
    """
    doc = nlp(text)
    masked_text = text
    details = []

    # Process spaCy entities: PERSON, ORG, GPE, LOC
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]:
            if mode == "partial":
                replacement = f"{ent.text[0]}{'*' * (len(ent.text) - 1)}"
            else:
                replacement = "[REDACTED]"
            masked_text = masked_text.replace(ent.text, replacement)
            if return_details:
                details.append({
                    "source": "spaCy",
                    "category": ent.label_,
                    "original_text": ent.text,
                    "replacement": replacement,
                    "start": ent.start_char,
                    "end": ent.end_char
                })

    # Additional regex patterns for sensitive data
    patterns = {
        "PASSPORT": r"\b[0-9]{9}\b",  # 9-digit passport number
        "EMAIL": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
        "PHONE": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",  # e.g., 123-456-7890
        "DATE": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",    # e.g., 12/31/2020 or 12-31-2020
        "ADDRESS": r"\b\d{1,5}\s(?:[A-Za-z0-9.-]+\s){1,3}(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln)\b"
    }

    for key, pattern in patterns.items():
        for match in re.finditer(pattern, masked_text):
            original_match = match.group(0)
            if mode == "partial":
                replacement = original_match[0] + "*" * (len(original_match) - 1)
            else:
                replacement = f"[{key} REDACTED]"
            masked_text = masked_text.replace(original_match, replacement)
            if return_details:
                details.append({
                    "source": "regex",
                    "category": key,
                    "original_text": original_match,
                    "replacement": replacement,
                    "start": match.start(),
                    "end": match.end()
                })
    
    if return_details:
        return {"masked_text": masked_text, "details": details}
    else:
        return masked_text

# Create Flask app
app = Flask(__name__)

# Configure caching
cache_config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Setup rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per minute"]
)
limiter.init_app(app)

# Conditional decorator: disable caching & rate limiting in testing mode.
def conditional_decorator(func):
    if app.config.get("TESTING"):
        return func
    else:
        # Apply caching and rate limiting if not testing
        return cache.cached(timeout=60, query_string=True)(limiter.limit("5 per minute")(func))

# Setup Swagger for interactive API documentation
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, config=swagger_config)

# GET endpoint: API status and documentation
@app.route("/", methods=["GET"])
def home():
    """
    API Home
    ---
    responses:
      200:
        description: API is running. See /docs/ for documentation.
    """
    return jsonify({"message": "API is running. Check /docs/ for documentation."})

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    """
    Health Check
    ---
    responses:
      200:
        description: API is healthy.
    """
    return jsonify({"status": "healthy"})

# POST endpoint: mask text
@app.route("/mask", methods=["POST"])
@swag_from({
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "mode": {"type": "string", "enum": ["partial", "full"], "default": "partial"},
                    "return_details": {"type": "boolean", "default": False}
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Masked text returned.",
            "schema": {
                "type": "object",
                "properties": {
                    "original_text": {"type": "string"},
                    "masked_text": {"type": "string"},
                    "details": {"type": "array", "items": {"type": "object"}}
                }
            }
        },
        "400": {
            "description": "Bad Request."
        }
    }
})
@conditional_decorator
def mask_text():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data.get("text")
        mode = data.get("mode", "partial")
        return_details = data.get("return_details", False)
        result = mask_sensitive_info(text, mode=mode, return_details=return_details)

        app.logger.info("Original: %s", text)
        app.logger.info("Result: %s", result)

        if return_details:
            return jsonify(result)
        else:
            return jsonify({"original_text": text, "masked_text": result})
    except Exception as e:
        app.logger.error("Error processing /mask: %s", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from config import DEBUG, HOST, PORT
    app.run(debug=DEBUG, host=HOST, port=PORT)
