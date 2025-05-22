from app.usecases.webhook_processor import WebhookProcessor
from app.usecases.message_flow.steps.steps_factory import ConversationStepsFactory
from app.usecases.message_flow.steps.steps_interface import ConversationStep
from app.usecases.message_flow.steps import steps
from app.infrastructure.database import insertions, queries
from app.domain.entities import Contact
from app.usecases.message_flow.flow_manager import FlowManager
from app.core import constants

class MessageRouter:
    def __init__(self, processor, webhook_categorization, webhook_data, contact: Contact):
        self.processor = processor
        self.webhook_categorization = webhook_categorization
        self.webhook_data = webhook_data
        self.contact = contact

    @classmethod
    async def create(cls, data: dict, webhook_DB_id: int):
        processor = WebhookProcessor(data)
        webhook_categorization = processor.categorize()
        webhook_data = processor.flatten_data(webhook_categorization)

        contact = await queries.get_contact_by_wa_id(webhook_data.wa_id)
        instance = cls(processor, webhook_categorization, webhook_data, contact)

        if contact:
            await instance.handle_existing_contact()
        else:
            await instance.handle_new_contact(constants.INITIAL_STEP)
        return instance

    async def handle_new_contact(self, initial_step: str):
        print("\n\nContacto nuevo\n\n")
        contact_id = await insertions.save_contact(
            self.webhook_data.wa_id,
            self.webhook_data.profile_name,
            initial_step
        )
        
        self.contact = Contact(
            id=contact_id,
            wa_id=self.webhook_data.wa_id,
            phone_number="",
            name=self.webhook_data.profile_name,
            step=initial_step
        )

        step = ConversationStepsFactory().get_step(initial_step)
        await step.handle(self)

    async def handle_existing_contact(self):
        print("\n\nContacto existente\n\n")
        self.contact.step = FlowManager.get_next_step(self, self.contact.step)

        step = ConversationStepsFactory().get_step(self.contact.step)
        step_instance = step(self.contact, self.webhook_data.message_body)
        await step_instance.handle()
        #await updates.cambiar_estado(self.id_contact, 2)