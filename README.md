# Advanced AI-Powered Data Compliance & Redaction System

This project provides an advanced API that detects and masks sensitive data in text to help ensure compliance with data protection standards (e.g., GDPR). The API uses a combination of spaCy for natural language processing and regex for pattern matching.

## Features

- **Sensitive Data Detection:** Identifies names, email addresses, phone numbers, passport numbers, dates, and addresses using spaCy and regex.
- **Masking Modes:**
  - **partial:** Shows the first character and masks the rest with asterisks.
  - **full:** Completely redacts sensitive data by replacing it with a placeholder.
- **Detailed Output:** Optionally returns detailed information about each masked element (e.g., category, source, positions).
- **Caching:** Caches responses for improved performance.
- **Rate Limiting:** Limits requests to 5 per minute per IP.
- **Swagger Documentation:** Provides interactive API documentation available at `/docs/`.
- **Health Check Endpoint:** Verify API status via `/health`.
- **Environment Configuration:** Uses a `.env` file for environment variable configuration (DEBUG, HOST, PORT).

## Installation

1. **Obtain the Project Files:**
   - Clone this repository or download the project as a ZIP file.
   - If using GitHub Desktop, add your local repository and then create a new repository from it.

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## 🔎 Demo — Metin Maskeleme Sonucu

**Örnek Giriş (Text)**
```text
Hello, I'm Jane Doe from Acme Corp.
You can reach me at jane.doe@acme.com or +1 (415) 555-2671.
I met John Smith in London on 2024-11-05.

```


Komut (cURL)

curl -s -X POST http://127.0.0.1:8000/redact -H "Content-Type: application/json" --data @demo/request.json > demo/output.json


Örnek Çıktı (JSON)

```json
{
  "mode": "partial",
  "text": "Hello, I'm Jane Doe from Acme Corp.\nYou can reach me at j***************m or +* (***) ***-****.\nI met John Smith in London on +* (***) ***-****."
}
```


Maskelenmiş Düz Metin

```text
Hello, I'm Jane Doe from Acme Corp.
You can reach me at j***************m or +* (***) ***-****.
I met John Smith in London on +* (***) ***-****.
```


> Not: `mode` "full" yapılırsa e-posta/telefon gibi PII değerleri `[REDACTED:TYPE]` olarak tamamen gizlenir.
