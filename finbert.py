"""The Python file for finBERT sentiment analysis."""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# https://huggingface.co/yiyanghkust/finbert-tone

NLP = None

def finbert_init():
    """Initialize finBERT."""
    tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
    model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

    global NLP
    NLP = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def finbert_sentiment(text):
    """Return the sentiment of the text."""
    if NLP is None:
        finbert_init()
    results = NLP(text)
    return results[0]

print(finbert_sentiment("IBM stocks plummet"))
