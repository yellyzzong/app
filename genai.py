import os
import openai
import json
import pandas as pd
import requests
import time
import re
import base64
from PIL import Image
from io import BytesIO

# === 1. Generate natural language text ===
def generate_text(prompt: str) -> str:
    client = openai.OpenAI(api_key=openai.api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating text: {e}")
        return "An error occurred while generating the text. Please try again."

# === 2. Generate audio from text ===
def generate_audio(text: str, voice: str = "nova") -> BytesIO:
    client = openai.OpenAI(api_key=openai.api_key)

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3"
        )
        return BytesIO(response.content)
    except Exception as e:
        print(f"Error generating audio: {e}")
        return BytesIO(b'')

# === 3. Generate realistic IG-style caption from timeline content ===
def generate_instagram_caption(decision_text: str, timeline_text: str = "") -> str:
    client = openai.OpenAI(api_key=openai.api_key)

    prompt = f"""
You are generating a casual Instagram caption for someone in an alternate life path.

Use this life decision as background: "{decision_text}"

Choose one specific event from the following timeline:
{timeline_text}

Now imagine the person is posting something about that event in a realistic, daily tone.

Make it sound like a real IG post someone would write after having a meaningful or ordinary day. Include a feeling (e.g., grateful, excited, tired, peaceful). Avoid sounding like a quote or generic reflection.

Style example:
"Clinic wrapped up early today so I finally had time to sit by the lake. Feeling calm and grounded. ☀️🌿"
or
"First patient smiled and said thank you. That made my entire day. 💙"

Keep it 1–2 sentences. Don't mention 'alternate universe'. Avoid hashtags unless they feel authentic.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=120
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating Instagram caption: {e}")
        return "Just another beautiful moment in this unexpected journey. ✨"

# === 4. Generate Pixar-style cartoon image using selfie and context ===
def generate_cartoon_image_from_selfie(uploaded_selfie, decision_text: str, timeline_text: str = "") -> Image.Image:
    if not uploaded_selfie:
        return None

    client = openai.OpenAI(api_key=openai.api_key)

    try:
        selfie_image = Image.open(uploaded_selfie).convert("RGB")

        decision_text_lower = decision_text.lower()

        if any(word in decision_text_lower for word in ["doctor", "medical", "hospital", "health", "nurse"]):
            background_scene = "inside a bright white modern hospital laboratory, with microscopes and computers"
        elif any(word in decision_text_lower for word in ["artist", "art", "creative", "paint", "design", "studio"]):
            background_scene = "an art studio filled with colorful paintings and bright sunlight"
        elif any(word in decision_text_lower for word in ["business", "finance", "corporate", "office", "entrepreneur"]):
            background_scene = "a luxury modern corporate office with large windows and city views"
        elif any(word in decision_text_lower for word in ["travel", "journey", "adventure", "explore", "abroad"]):
            background_scene = "a scenic overlook with mountains and a beautiful sunset"
        elif any(word in decision_text_lower for word in ["tech", "programmer", "software", "computer", "developer", "engineer"]):
            background_scene = "a modern tech workspace with multiple screens and ambient lighting"
        elif any(word in decision_text_lower for word in ["teach", "education", "school", "student", "professor"]):
            background_scene = "a bright classroom with bookshelves and educational posters"
        elif any(word in decision_text_lower for word in ["chef", "cook", "restaurant", "food", "culinary"]):
            background_scene = "a professional kitchen with stainless steel appliances and fresh ingredients"
        elif any(word in decision_text_lower for word in ["music", "musician", "band", "singer", "concert"]):
            background_scene = "a recording studio with musical instruments and warm lighting"
        elif any(word in decision_text_lower for word in ["sports", "athlete", "fitness", "coach", "gym"]):
            background_scene = "a modern training facility with sports equipment and trophies"
        elif any(word in decision_text_lower for word in ["nature", "environment", "outdoor", "wildlife", "conservation"]):
            background_scene = "a lush forest with sunlight streaming through the trees"
        else:
            background_scene = "a cozy cafe with soft lighting and a peaceful atmosphere, golden hour sunlight streaming through windows"

        prompt = f"""
Create a Pixar-style cartoon portrait based on this life decision: "{decision_text}".
The character should be in {background_scene}.
Style: Realistic 3D rendering with Pixar-like characteristics, expressive eyes, natural colors, cinematic lighting.
Make it warm and inspiring, showing a happy, fulfilled version of the person.
Use a warm color palette with golden yellows, soft oranges, and gentle browns.
"""

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            style="vivid"
        )

        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        img = Image.open(BytesIO(img_data))
        return img

    except Exception as e:
        print(f"Error generating cartoon image: {e}")

        placeholder = Image.new('RGB', (500, 500), color=(255, 246, 224))
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(placeholder)
            font = ImageFont.load_default()
            draw.text((100, 200), "Image generation in progress...", fill=(224, 159, 62), font=font)
            draw.text((150, 250), "Your parallel self awaits!", fill=(224, 159, 62), font=font)
        except:
            pass

        return placeholder
    

def generate_parallel_letter(timeline: str, name: str = "you") -> str:
    client = openai.OpenAI(api_key=openai.api_key)

    prompt = f"""
You are writing a heartfelt, emotionally healing letter from a PARALLEL SELF to the user {name}.
This is not a letter from the future, but from a version of yourself who took a different path in life.
Reflect on the following timeline of your life in the parallel universe:

{timeline}

Now write a first-person letter that:
- Feels like it's from a real person who has struggled, grown, and made peace with their path
- Acknowledges both highs and lows (don’t idealize everything)
- Gently comforts and supports the user who made a different choice
- Expresses empathy, emotional honesty, and quiet strength
- Sounds like a friend who understands without judgment
- Closes with warmth and encouragement

Avoid generic inspirational quotes. Make it real, specific, and emotionally resonant.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=900
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error generating parallel letter:", e)
        return "Dear me,\n\nEven if our lives are different, I want you to know I understand. I've stumbled too — and grown from it. You're doing better than you think.\n\nWith care,\nYour other self"