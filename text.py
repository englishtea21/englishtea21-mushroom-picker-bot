from os import getenv
import json

with open(getenv("TEXT_TEMPLATES_FILE"), "rb") as f:
    text_templates = json.loads(f.read().decode(getenv("TEXT_TEMPLATES_FILE_ENCODING")))
