from transformers import pipeline

ner_pipe = pipeline(
    "token-classification",
    model="Clinical-AI-Apollo/Medical-NER",
    aggregation_strategy='simple'
)
