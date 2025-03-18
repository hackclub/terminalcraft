def generate(prompt: str):
  from io import BytesIO
  from os import getenv

  from ascii_magic import from_image
  from dotenv import load_dotenv
  from google import genai
  from google.genai import types
  from PIL import Image

  load_dotenv()

  client = genai.Client(api_key=getenv("GENAI_API_KEY"))
  response = client.models.generate_images(
    model="imagen-3.0-generate-002",
    prompt=prompt,
    config=types.GenerateImagesConfig(
      number_of_images=1,
    ),
  )
  image = Image.open(BytesIO(response.generated_images[0].image.image_bytes))
  image.save("response.jpg")
  my_art = from_image("response.jpg")
  my_art.to_terminal()
