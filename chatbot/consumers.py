from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from spacy import load
import nltk

nltk.download("punkt")
nltk.download("stopwords")

nlp = load("en_core_web_sm")


async def process_message(message):
    """Process and analyze the message without echoing it back."""
    doc = nlp(message)
    tokens = word_tokenize(message.lower())
    stop_words = set(stopwords.words("english"))
    tokens = [w for w in tokens if w not in stop_words]
    return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.lead_id = None
        self.current_question = None
        self.responses = {}
        self.user_name = None
        self.user_email = None
        self.pending_interactions = []

        await self.send_greeting()
        await self.start_flow()

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("message")

        await process_message(user_message)

        if self.current_question:
            # Store name and email when received
            if hasattr(self.current_question, "text"):
                if "name" in self.current_question.text.lower():
                    self.user_name = user_message
                elif "email" in self.current_question.text.lower():
                    self.user_email = user_message

            # Store the response
            self.responses[self.current_question.text] = user_message
            # Store interaction for later
            self.pending_interactions.append((self.current_question, user_message))

        next_question = await self.get_next_question()

        if next_question:
            await self.send_question(next_question)
        else:
            await self.end_flow()

    async def send_greeting(self):
        """Send initial greeting message to the user."""
        greeting = "👋 Welcome! I'm here to help you today. Let's get started with a few questions."
        await self.send(text_data=json.dumps({"message": greeting}))

    async def start_flow(self):
        """Initiate chatbot and ask the first question."""
        first_question = await self.get_next_question()
        if first_question:
            await self.send_question(first_question)
        else:
            await self.end_flow()

    @sync_to_async
    def get_next_question(self):
        """Fetch the next question from the database."""
        from .models import Question

        if self.current_question:
            next_question = Question.objects.filter(
                id=self.current_question.next_question_id
            ).first()
        else:
            next_question = Question.objects.first()

        self.current_question = next_question
        return next_question

    async def send_question(self, message):
        """Send the next question or message to the user."""
        if hasattr(message, "text"):  # If it's a Question object
            await self.send(text_data=json.dumps({"message": message.text}))
        else:  # If it's a string
            await self.send(text_data=json.dumps({"message": str(message)}))

    @sync_to_async
    def create_lead_and_interactions(self):
        """Create lead and all interactions at once."""
        from .models import Lead, UserInteraction

        # Create the lead
        lead = Lead.objects.create(name=self.user_name, email=self.user_email)

        # Create all interactions
        for question, answer in self.pending_interactions:
            UserInteraction.objects.create(lead=lead, question=question, answer=answer)

        return lead.id

    async def end_flow(self):
        """End the conversation and give a summary."""
        # Create lead and save all interactions
        self.lead_id = await self.create_lead_and_interactions()

        summary = "\n".join([f"{q}: {a}" for q, a in self.responses.items()])
        farewell_message = (
            f"🙏 Thank you {self.user_name}! "
            "Here's a summary of what we discussed:\n\n" + summary
        )
        await self.send(text_data=json.dumps({"message": farewell_message}))
        await self.close()
