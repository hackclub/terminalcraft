def chat():
  from io import StringIO
  from os import getenv

  from dotenv import load_dotenv
  from google import genai
  from google.genai import types
  from markdown import Markdown

  load_dotenv()

  def unmark_element(element, stream=None):
    if stream is None:
      stream = StringIO()
    if element.text:
      stream.write(element.text)
    for sub in element:
      unmark_element(sub, stream)
    if element.tail:
      stream.write(element.tail)
    return stream.getvalue()

  Markdown.output_formats["plain"] = unmark_element
  __md = Markdown(output_format="plain")
  __md.stripTopLevelTags = False

  def unmark(text):
    return __md.convert(text)

  client = genai.Client(api_key=getenv("GENAI_API_KEY"))
  messages = []
  print("Welcome to the chat! Type 'exit' to leave the chat")
  while True:
    x = input("\33[0;34mYou > \033[0m")
    if x == "exit":
      messages.append("Byee Gemini! See you again.\n")
      response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
          system_instruction="Don't share personal information",
          temperature=1.6,
        ),
      )
      print("\33[0;34mGemini > \033[0m", unmark(response.text).strip())
      break
    else:
      messages.append(x + ". \n")
      response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
          system_instruction="Don't share personal information",
          temperature=1.2,
        ),
      )
      print("\33[0;34mGemini >\033[0m", unmark(response.text).strip())
