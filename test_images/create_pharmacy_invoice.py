from PIL import Image, ImageDraw

img = Image.new('RGB', (600, 500), color='white')
draw = ImageDraw.Draw(img)

lines = [
    "RIVERSIDE PHARMACY",
    "123 Main St, Springfield, State 12345",
    "Phone: (555) 987-6543",
    "",
    "Invoice #: RX-2026-08421",
    "Date: 08/15/2026",
    "",
    "Patient: Margaret Thompson",
    "Prescriber: Dr. Sarah Chen",
    "",
    "Item                          Qty     Price",
    "Lisinopril 10mg (30ct)         1      $12.50",
    "Metformin 500mg (60ct)         1      $18.00",
    "Acetaminophen 500mg (100ct)    1       $8.25",
    "",
    "Subtotal:                            $38.75",
    "Insurance Copay:                     $10.00",
    "Total Due:                           $10.00",
]

y = 15
for line in lines:
    draw.text((20, y), line, fill='black')
    y += 25

img.save('test_images/pharmacy_invoice.png')
print("Created test_images/pharmacy_invoice.png")
