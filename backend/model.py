import torch
from transformers import AutoModelForImageClassification
from transformers import AutoImageProcessor, AutoModelForImageClassification


processor = AutoImageProcessor.from_pretrained("./backend/")
model = AutoModelForImageClassification.from_pretrained("./backend/")

def infer(image):
    inputs = processor(image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    values, indexes = torch.topk(logits, 5)
    results = []
    for value, index in zip(values[0], indexes[0]):
        result = {
            "label": model.config.id2label[index.item()],
            "confidence_score": value.item()
        }
        results.append(result)
    return results
