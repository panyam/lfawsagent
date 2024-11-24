import os
import requests

MODEL = "mistral"
url = "http://localhost:11434/api/generate"

class LLM:
    def call(self, prompt):
        payload = {"model": MODEL, "prompt": prompt, "stream": False}
        response = requests.post(url, json=payload)
        j = response.json()
        resp = j["response"]
        return resp
        
