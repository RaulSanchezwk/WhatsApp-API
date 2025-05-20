from app.usecases.message_flow.schemas import WebhookPayload
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class FlattenedData(BaseModel):
    business_account_id: Optional[str]
    messaging_product: Optional[str]
    display_phone_number: Optional[str]
    phone_number_id: Optional[str]
    field: Optional[str]
    profile_name: Optional[str]
    wa_id: Optional[str]
    message_id: Optional[str]
    whatsapp_received_at: Optional[str]
    we_received_at: datetime
    message_type: Optional[str]
    message_body: Optional[str]
    status: Optional[str]
    status_timestamp: Optional[str]
    recipient_id: Optional[str]
    conversation_id: Optional[str]
    conversation_type: Optional[str]
    billable: Optional[bool]
    pricing_model: Optional[str]
    category: Optional[str]
    expiration_timestamp: Optional[str]

class WebhookProcessor:
    def __init__(self, raw_data: dict):
        self.raw_data = raw_data
        self.payload = WebhookPayload(**raw_data)

    def categorize(self) -> str:
        value = self.payload.entry[0].changes[0].value
        if value.messages:
            return "message"
        elif value.statuses:
            return "status"

    def flatten_data(self, category: str) -> FlattenedData:
        entry = self.payload.entry[0]
        change = entry.changes[0]
        value = change.value

        base = {
            "business_account_id": entry.id,
            "messaging_product": value.messaging_product,
            "display_phone_number": value.metadata.display_phone_number,
            "phone_number_id": value.metadata.phone_number_id,
            "we_received_at": datetime.now()
        }

        if category == "message":
            msg = value.messages[0]
            contact = value.contacts[0]
            base.update({
                "profile_name": contact.profile.name,
                "wa_id": contact.wa_id,
                "message_id": msg.id,
                "whatsapp_received_at": msg.timestamp,
                "message_type": msg.type,
                "message_body": msg.text.body if msg.text else None,
            })

        elif category == "status":
            status = value.statuses[0]
            base.update({
                "message_id": status.id,
                "status": status.status,
                "status_timestamp": status.timestamp,
                "recipient_id": status.recipient_id,
                "conversation_id": status.conversation.id if status.conversation else None,
                "conversation_type": status.conversation.origin.type if status.conversation and status.conversation.origin else None,
                "billable": status.pricing.billable if status.pricing else None,
                "pricing_model": status.pricing.pricing_model if status.pricing else None,
                "category": status.pricing.category if status.pricing else None,
                "expiration_timestamp": getattr(status.conversation, "expiration_timestamp", None)
            })

        return FlattenedData(**base)
