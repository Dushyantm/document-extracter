from transformers import pipeline

# Create NER pipeline
ner_pipeline = pipeline(
    "token-classification",
    model="yashpwr/resume-ner-bert-v2",
    aggregation_strategy="simple"
)

# Extract entities  
text = """
Sarah Johnson holds a Master's degree in Computer Science from Stanford University. Skills: Python, TensorFlow, SQL.
"""
results = ner_pipeline(text)

for entity in results:
    print(f"{entity['entity_group']}: {entity['word']} (confidence: {entity['score']:.3f})")
