from pydantic import BaseModel, Field
from typing import List, Optional

# ======= MENSAJES =======

class TextMessage(BaseModel):
    body: str

class WhatsAppMessage(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[TextMessage]

class ContactProfile(BaseModel):
    name: str

class Contact(BaseModel):
    profile: ContactProfile
    wa_id: str

# ======= ESTATUS =======

class MessageOrigin(BaseModel):
    type: str

class MessageConversation(BaseModel):
    id: str
    origin: Optional[MessageOrigin]

class MessagePricing(BaseModel):
    billable: bool
    pricing_model: Optional[str]
    category: Optional[str]

class MessageStatus(BaseModel):
    id: str
    status: str
    timestamp: str
    recipient_id: str
    conversation: Optional[MessageConversation]
    pricing: Optional[MessagePricing]

# ======= METADATA / VALUE / ENTRY =======

class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str

class ChangeValue(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]]
    messages: Optional[List[WhatsAppMessage]]
    statuses: Optional[List[MessageStatus]]

class Change(BaseModel):
    value: ChangeValue
    field: str

class Entry(BaseModel):
    id: str
    changes: List[Change]

class WebhookPayload(BaseModel):
    object: str
    entry: List[Entry]
