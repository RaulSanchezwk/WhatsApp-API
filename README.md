# Automated Scheduling Chatbot

This project is intended to create and manage a chatbot that allows clients to schedule appointments on their own, without requiring human assistance, while still enabling human intervention if an error occurs. It is built to support integration with various messaging platforms such as WhatsApp, Facebook Pages, and more.


## Getting Started

### Clone the repo
git clone https://github.com/RegioDental/automated-scheduling-chatbot.git
cd automated-scheduling-chatbot

### Create and activate a virtual environment (Python)
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

### Install dependencies
pip install -r requirements.txt

### Run the project
uvicorn app.interfaces.main:app --port 8000 --reload


## Testing Webhook Locally

### Emulate a Customer Message Locally Using PowerShell
$uri = "http://localhost:8000/webhook"
$headers = @{ "Content-Type" = "application/json" }

$json = @'
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "1224129935909135",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "5218134462645",
              "phone_number_id": "589111897626816"
            },
            "contacts": [
              {
                "profile": {
                  "name": "client_profile_name" # you could change this
                },
                "wa_id": "client_wa_id" # and this
              }
            ],
            "messages": [
              {
                "from": "client_wa_id", # also this
                "id": "wamid.HBgNNTIxODEzNTc0NTkxMBUCABIYFDNBNTgxMzI3MkYyRTlGOTgzNDNEAA==",
                "timestamp": "1746550314",
                "text": {
                  "body": "Hola"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
'@

Invoke-WebRequest -Uri $uri -Method POST -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($json))

### Emulate a Customer Message Locally Using curl
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [
      {
        "id": "1224129935909135",
        "changes": [
          {
            "value": {
              "messaging_product": "whatsapp",
              "metadata": {
                "display_phone_number": "5218134462645",
                "phone_number_id": "589111897626816"
              },
              "contacts": [
                {
                  "profile": {
                    "name": "client_profile_name"
                  },
                  "wa_id": "client_wa_id"
                }
              ],
              "messages": [
                {
                  "from": "client_wa_id",
                  "id": "wamid.HBgNNTIxODEzNTc0NTkxMBUCABIYFDNBNTgxMzI3MkYyRTlGOTgzNDNEAA==",
                  "timestamp": "1746550314",
                  "text": {
                    "body": "Hola"
                  },
                  "type": "text"
                }
              ]
            },
            "field": "messages"
          }
        ]
      }
    ]
  }'
