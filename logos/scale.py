from PIL import Image
import os

dir = r"C:\Users\reich\Documents\GIT\katie\logos"
original_fname = os.path.join(dir, "favicon.png")
new_fname = os.path.join(dir, "favicon_scaled.png")

# Load image
img = Image.open(original_fname).convert("RGBA")

# Resize to 32x32
img_resized = img.resize((32, 32), Image.LANCZOS)

# Save resized image
img_resized.save(new_fname)