import moondream as md
from PIL import Image

# Initialize with local model path
model = md.vl(model="moondream-0_5b-int8.mf")

# Load and encode image
image = Image.open("IMG_3257.jpg")

# Since encoding an image is computationally expensive, you can encode it once
# and reuse the encoded version for multiple queries/captions/etc. This avoids
# having to re-encode the same image multiple times.
encoded_image = model.encode_image(image)

# Generate caption
caption = model.caption(encoded_image)["caption"]
print("Caption:", caption)

# Ask questions
answer = model.query(encoded_image, "What's in this image?")["answer"]
print("Answer:", answer)
