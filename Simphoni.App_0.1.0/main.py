# main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Read OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("Please set the OPENAI_API_KEY environment variable.")

# Define request models
class ChatRequest(BaseModel):
    prompt: str
    model: Optional[str] = "gpt-4o-txt"  # Default to KEE1:txt

class OllamaRequest(BaseModel):
    model: str
    prompt: str

class StableDiffusionRequest(BaseModel):
    prompt: str

# CORS Configuration (Adjust origins as needed)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ChatGPT endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4",  # Use "gpt-4o" or your custom model if available
        "messages": [
            {"role": "user", "content": request.prompt}
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            return {"reply": reply}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

# Ollama endpoint
@app.post("/ollama")
async def ollama(request: OllamaRequest):
    ollama_url = "http://localhost:11434/api/generate"  # Ensure Ollama server is running
    data = {
        "model": request.model,
        "prompt": request.prompt
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(ollama_url, json=data)
        if response.status_code == 200:
            result = response.json()
            # Assuming response has 'generated_text'
            generated_text = result.get('generated_text', '')
            return {"reply": generated_text}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

# Stable Diffusion endpoint
@app.post("/stable-diffusion")
async def stable_diffusion(request: StableDiffusionRequest):
    sd_url = "http://localhost:7860/sdapi/v1/txt2img"  # Ensure Stable Diffusion is running with API
    data = {
        "prompt": request.prompt,
        "sampler_name": "Euler a",
        "batch_size": 1,
        "steps": 50,
        "cfg_scale": 7,
        "width": 512,
        "height": 512,
        "seed": -1,
        "negative_prompt": ""
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(sd_url, json=data)
        if response.status_code == 200:
            result = response.json()
            # Assuming response has 'images' which are base64 encoded
            images = result.get('images', [])
            if images:
                # Return the first image
                image_data = images[0]
                # To display the image, the frontend needs to handle base64
                return {"image": image_data}
            else:
                raise HTTPException(status_code=500, detail="No image generated.")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
