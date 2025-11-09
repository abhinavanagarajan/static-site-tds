import json

# Step 1: Load the JSON image data
with open("stego_image.json", "r") as f:
    data = json.load(f)

pixels = data["pixels"]

# Step 2: Extract LSBs from R, G, B of each pixel
bits = ""

for row in pixels:
    for pixel in row:
        for channel in pixel:  # R, G, B
            bits += str(channel & 1)  # LSB

# Step 3: Convert bits to ASCII
message = ""
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) < 8:
        break
    message += chr(int(byte, 2))
    if len(message) == 16:
        break

print("Extracted message:", message)
