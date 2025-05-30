from app.usecases.webhook_processor import WebhookProcessor, FlattenedData
from app.usecases.message_flow.steps.steps_factory import ConversationStepsFactory
from app.usecases.message_flow.steps.steps_interface import ConversationStep
from app.usecases.message_flow.steps import steps
from app.infrastructure.database import insertions, queries, updates
from app.domain.entities import Contact
from app.usecases.message_flow.flow_manager import FlowManager
from app.core import constants

class MessageRouter:
    def __init__(self, processor: WebhookProcessor, webhook_DB_id: int, webhook_categorization: str, webhook_data: FlattenedData, contact: Contact):
        self.processor = processor
        self.webhook_DB_id = webhook_DB_id
        self.webhook_categorization = webhook_categorization
        self.webhook_data = webhook_data
        self.contact = contact

    @classmethod
    async def create(cls, data: dict, webhook_DB_id: int):
        processor = WebhookProcessor(data)
        webhook_categorization = processor.categorize()
        webhook_data = processor.flatten_data(webhook_categorization)

        contact = await queries.get_contact_by_wa_id(webhook_data.wa_id)
        instance = cls(processor, webhook_DB_id, webhook_categorization, webhook_data, contact)

        if contact:
            print("\n\nContacto existente\n\n")
            await instance.handle_existing_contact()
        else:
            print("\n\nContacto nuevo\n\n")
            await instance.handle_new_contact()

        return instance

    async def handle_new_contact(self):
        
        contact_id = await insertions.save_contact(
            self.webhook_data.wa_id,
            self.webhook_data.profile_name,
            constants.INITIAL_STEP
        )

        self.contact = Contact(
            id = contact_id,
            wa_id=self.webhook_data.wa_id,
            phone_number="",
            name=self.webhook_data.profile_name,
            step=constants.INITIAL_STEP
        )

        await updates.update_webhook_contact(self.contact, self.webhook_DB_id)
        await insertions.save_appt_intention(self.contact)

        step = ConversationStepsFactory().get_step(constants.INITIAL_STEP)
        step_instance = step(self.contact, self.webhook_data.message_body)
        response = await step_instance.handle()

        if response.get("contacts") != None: 
            self.contact.phone_number = response["contacts"][0]["input"]
        else:
            self.contact.phone_number = "No phone number"

        await updates.update_phone_number(self.contact)

    async def handle_existing_contact(self):

        await updates.update_webhook_contact(self.contact, self.webhook_DB_id)

        current_step = self.contact.step

        self.contact.step = FlowManager.get_next_step(self, current_step)

        step = ConversationStepsFactory().get_step(self.contact.step)
        step_instance = step(self.contact, self.webhook_data.message_body)
        await step_instance.handle()

        await updates.change_step(self.contact)
