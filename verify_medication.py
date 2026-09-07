import json
from ocr_reader import read_text_from_image
from rag_utils import CarePlanIndex
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(
    azure_endpoint="https://oai-echocare-b9328.openai.azure.com/",
    azure_ad_token=token.token,
    api_version="2024-10-21",
)

def verify_medication_photo(image_path):
    label_lines = read_text_from_image(image_path)
    label_text = "\n".join(label_lines)

    care_plan_index = CarePlanIndex(client)
    relevant_care_plan_section = care_plan_index.retrieve(label_text, top_k=3)

    prompt = f"""A photo of a medication label was read via OCR. Compare it against the person's
actual care plan and flag any discrepancy.

TEXT READ FROM PHOTOGRAPHED LABEL:
{label_text}

RELEVANT CARE PLAN SECTION (what they're actually prescribed):
{relevant_care_plan_section}

Respond in JSON:
{{
  "matches_care_plan": true or false,
  "discrepancy_detail": "specific description if there's a mismatch in medication name, dosage, or timing - or null if it matches"
}}"""

    response = client.chat.completions.create(
        model="gpt-4-1-deployment",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    result = verify_medication_photo("test_images/prescription_label.png")
    print(result)
