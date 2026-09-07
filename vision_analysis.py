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

def analyze_image(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()

    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.TAGS, VisualFeatures.OBJECTS]
    )

    analysis = {
        "tags": [tag.name for tag in result.tags.list] if result.tags else [],
        "objects": [obj.tags[0].name for obj in result.objects.list] if result.objects else []
    }
    return analysis

if __name__ == "__main__":
    result = analyze_image("test_images/screenshot_test.png")
    print("Tags:", result["tags"])
    print("Objects detected:", result["objects"])
