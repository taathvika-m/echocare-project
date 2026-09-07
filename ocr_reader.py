from dotenv import load_dotenv
import os
load_dotenv()
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

VISION_ENDPOINT = os.environ["VISION_ENDPOINT"]
VISION_KEY = os.environ["VISION_KEY"]

client = ImageAnalysisClient(
    endpoint=VISION_ENDPOINT,
    credential=AzureKeyCredential(VISION_KEY)
)

def read_text_from_image(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()

    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.READ]
    )

    lines = []
    if result.read is not None:
        for block in result.read.blocks:
            for line in block.lines:
                lines.append(line.text)
    return lines

if __name__ == "__main__":
    lines = read_text_from_image("test_images/prescription_label.png")
    print("=== TEXT READ FROM LABEL ===")
    for line in lines:
        print(line)
