from app.usecases.webhook_processor import WebhookProcessor
from app.usecases.message_flow.steps.steps_factory import ConversationStepsFactory
from app.infrastructure.database import insertions, queries, updates
from app.core import constants

class MessageRouter:
    async def __init__(self, data: dict, webhook_DB_id: int) -> None:
        self.processor = WebhookProcessor(data)
        self.webhook_categorization = self.processor.categorize()
        self.webhook_data = self.processor.flatten_data(self.webhook_categorization)

        contact = await queries.contact_exists()

        if contact:
            self.handle_existing_contact(contact)
        else:
            self.handle_new_contact("sucursales")

    def handle_new_contact(self, step: str):

        insertions.save_contact(self.webhook_data.wa_id, 
                                self.webhook_data.profile_name,
                                0)
        
        step = ConversationStepsFactory().get_step(step)
        step.handle()

    def handle_existing_contact(self, id_contact: int):
        step = queries.get_step(id_contact)
        step = ConversationStepsFactory().get_step(step)
        step.handle()
        #await updates.cambiar_estado(self.id_contact, 2)