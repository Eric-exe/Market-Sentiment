from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# https://huggingface.co/ProsusAI/finbert
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

text = "Some financial text."

results = nlp(text)
print(results)