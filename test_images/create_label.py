from PIL import Image, ImageDraw

img = Image.new('RGB', (500, 300), color='white')
draw = ImageDraw.Draw(img)

lines = [
    "RIVERSIDE PHARMACY",
    "123 Main St, Springfield",
    "",
    "Margaret Thompson",
    "",
    "LISINOPRIL 20mg TABLETS",
    "Take ONE tablet by mouth",
    "every morning",
    "",
    "Qty: 30    Refills: 2",
    "Dr. Sarah Chen",
    "Exp: 12/2027"
]

y = 10
for line in lines:
    draw.text((20, y), line, fill='black')
    y += 22

img.save('test_images/prescription_label.png')
print("Created test_images/prescription_label.png")
