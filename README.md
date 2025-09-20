# Data Redaction & Privacy Compliance API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-orange.svg)](https://spacy.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A REST API for automatic detection and masking of sensitive data (PII) to help ensure GDPR, CCPA, and data privacy compliance.

This API combines spaCy NLP models with regex patterns to identify and mask personal identifiable information including emails, phone numbers, names, organizations, addresses, passport numbers, and dates.

## Features

- **Data Protection**: Identifies and masks emails, phone numbers, passport numbers, dates, and addresses using spaCy NLP and regex patterns
- **Flexible Masking Modes**:
  - **Partial Mode**: Shows first character and masks the rest with asterisks (e.g., `j***@example.com`)
  - **Full Mode**: Complete redaction with typed placeholders (e.g., `[REDACTED:EMAIL]`)
- **Performance**: Caching system for improved response times on repeated requests
- **Rate Limiting**: 5 requests per minute per IP to prevent abuse
- **API Documentation**: Full Swagger/OpenAPI documentation available at `/docs/`
- **Health Monitoring**: Built-in health check endpoint for system monitoring
- **Multi-Entity Recognition**: Detects PERSON, ORG, GPE (countries/cities), LOC (locations) using spaCy models
- **Configuration**: Environment-based configuration with `.env` file support for DEBUG, HOST, PORT settings

## Use Cases

### Data Analytics Companies
- Clean customer datasets before analysis
- Ensure GDPR compliance for EU customers
- Protect sensitive information in reports

### Legal & Financial Services
- Redact contracts and legal documents
- Mask client information in case studies
- Comply with banking privacy regulations

### Healthcare & Research
- Anonymize patient records for research
- Remove PII from medical documents
- HIPAA compliance for health data

### E-commerce & SaaS Platforms
- Protect customer data in logs
- Mask emails in customer support tickets
- Anonymize user feedback and reviews

## API Endpoints

| Endpoint | Method | Purpose | Response Time |
|----------|---------|---------|---------------|
| `/mask` | POST | Advanced NLP-based entity masking | ~100ms |
| `/redact` | POST | Quick email/phone pattern masking | ~50ms |
| `/health` | GET | System status monitoring | ~10ms |
| `/docs` | GET | Interactive API documentation | Instant |

## Installation

1. **Obtain the Project Files:**
   - Clone this repository or download the project as a ZIP file.
   - If using GitHub Desktop, add your local repository and then create a new repository from it.

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## Demo

**Sample Business Email Input**
```text
Dear Client,

I'm Sarah Johnson, CEO of TechSecure Solutions Inc., located at 1247 Silicon Valley Blvd, San Francisco, CA 94102. 

Our confidential client meeting is scheduled for December 15, 2024. Please contact me directly at sarah.johnson@techsecure.com or call my direct line +1 (555) 123-4567. You can also reach our VP of Sales, Michael Chen, at m.chen@techsecure.com or +1 (415) 987-6543.

For urgent matters, text me at +1 (650) 555-9876. My passport number is 123456789 for international travel arrangements.

Best regards,
Sarah Johnson
CEO, TechSecure Solutions Inc.
Phone: +1 (555) 123-4567 | Mobile: +1 (650) 555-9876
Email: sarah.johnson@techsecure.com
Address: 1247 Silicon Valley Blvd, San Francisco, CA 94102
```

**API Call**
```bash
curl -s -X POST http://127.0.0.1:8000/redact \
  -H "Content-Type: application/json" \
  --data @demo/request.json > demo/output.json
```

**JSON Response (Partial Mode)**
```json
{
  "mode": "partial",
  "text": "Dear Client,\n\nI'm Sarah Johnson, CEO of TechSecure Solutions Inc., located at 1247 Silicon Valley Blvd, San Francisco, CA 94102.\n\nOur confidential client meeting is scheduled for December 15, 2024. Please contact me directly at s**************************m or call my direct line +* (***) ***-****. You can also reach our VP of Sales, Michael Chen, at m*******************m or +* (***) ***-****.\n\nFor urgent matters, text me at +* (***) ***-****. My passport number is +* (***) ***-**** for international travel arrangements.\n\nBest regards,\nSarah Johnson\nCEO, TechSecure Solutions Inc.\nPhone: +* (***) ***-**** | Mobile: +* (***) ***-****\nEmail: s**************************m\nAddress: 1247 Silicon Valley Blvd, San Francisco, CA 94102"
}
```

**Masked Output (Partial Mode)**
```text
Dear Client,

I'm Sarah Johnson, CEO of TechSecure Solutions Inc., located at 1247 Silicon Valley Blvd, San Francisco, CA 94102.

Our confidential client meeting is scheduled for December 15, 2024. Please contact me directly at s**************************m or call my direct line +* (***) ***-****. You can also reach our VP of Sales, Michael Chen, at m*******************m or +* (***) ***-****.

For urgent matters, text me at +* (***) ***-****. My passport number is +* (***) ***-**** for international travel arrangements.

Best regards,
Sarah Johnson
CEO, TechSecure Solutions Inc.
Phone: +* (***) ***-**** | Mobile: +* (***) ***-****
Email: s**************************m
Address: 1247 Silicon Valley Blvd, San Francisco, CA 94102
```

**🔐 Full Mode Example (Complete Redaction)**
```bash
# Request with "mode": "full"
curl -s -X POST http://127.0.0.1:8000/redact \
  -H "Content-Type: application/json" \
  -d '{"text":"Contact me at john.doe@company.com or +1 (555) 123-4567","mode":"full"}'

# Response:
{
  "mode": "full",
  "text": "Contact me at [REDACTED:EMAIL] or [REDACTED:PHONE]"
}
```

> **💡 Pro Tip:** `mode: "partial"` → Partial masking for readability | `mode: "full"` → Complete redaction for maximum security
