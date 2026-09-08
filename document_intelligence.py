import os
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

client = DocumentIntelligenceClient(
    endpoint=os.environ["DOCINTEL_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["DOCINTEL_KEY"])
)

def extract_invoice_fields(image_path):
    with open(image_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-invoice",
            body=f,
            content_type="application/octet-stream"
        )
    result = poller.result()

    extracted = {}
    for document in result.documents:
        for field_name, field in document.fields.items():
            extracted[field_name] = {
                "value": field.value_string or field.content,
                "confidence": round(field.confidence, 2) if field.confidence else None
            }
    return extracted

if __name__ == "__main__":
    fields = extract_invoice_fields("test_images/pharmacy_invoice.png")
    print("=== EXTRACTED INVOICE FIELDS ===")
    for name, data in fields.items():
        print(f"{name}: {data['value']} (confidence: {data['confidence']})")
