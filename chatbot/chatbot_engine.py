import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from spacy import load

nlp = load("en_core_web_sm")
nltk.download("punkt")
nltk.download("stopwords")


async def process_message(message):
    # Basic NLP processing
    doc = nlp(message)
    tokens = word_tokenize(message.lower())
    stop_words = set(stopwords.words("english"))
    tokens = [w for w in tokens if w not in stop_words]

    # Add your chatbot logic here
    # This is a simple example - expand based on your needs
    return "Thank you for your message. How can I help you today?"
