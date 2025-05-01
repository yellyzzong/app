from typing import Dict, List
from PIL import Image
import base64
import io
import openai
import re
import random

# 🛠️ Create OpenAI client
def get_openai_client():
    return openai.OpenAI(api_key=openai.api_key)

# === 1. Analyze user's personality ===
def analyze_personality(intro_text: str) -> Dict:
    if intro_text and len(intro_text.strip()) > 10:
        client = get_openai_client()
        prompt = (
            f"Analyze the personality in this self-introduction: '{intro_text}'\n\n"
            f"Provide results in this JSON format:\n"
            f"{{\"Rational/Emotional\": \"[Choose one]\", "
            f"\"Adventurous/Cautious\": \"[Choose one]\", "
            f"\"Independent/Collaborative\": \"[Choose one]\", "
            f"\"Core Values\": [\"Value1\", \"Value2\"], "
            f"\"Decision Style\": \"[Brief description]\"}}"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            import json
            content = response.choices[0].message.content
            json_match = re.search(r'{.*}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error analyzing personality: {e}")
    
    return {
        "Rational/Emotional": "Balanced",
        "Adventurous/Cautious": "Moderately Adventurous",
        "Independent/Collaborative": "Balanced",
        "Core Values": ["Personal Growth", "Connection"],
        "Decision Style": "Thoughtful"
    }

# === 2. Generate alternate life timeline ===
# Modify the generate_dynamic_life_timeline function in utils.py
def generate_dynamic_life_timeline(name: str, intro_text: str, decision_text: str, emotions: List[str]) -> List[str]:
    client = get_openai_client()
    emotion_phrase = ", ".join(emotions) if emotions else "Neutral"
    
    # Extract the decision age from the decision text
    decision_age = 23  # Default fallback
    age_match = re.search(r'At the age of (\d+)', decision_text)
    if age_match:
        decision_age = int(age_match.group(1))
    
    # Extract the actual decision for inversion
    decision_description = ""
    if "I " in decision_text:
        decision_description = decision_text.split("I ", 1)[1].strip()
        if decision_description.endswith("."):
            decision_description = decision_description[:-1]
    
    prompt = (
        f"You are a parallel universe life simulator showing realistic alternate paths.\n"
        f"- Name: {name}\n"
        f"- Self-introduction: {intro_text}\n"
        f"- Major life decision they made in real life: {decision_text}\n"
        f"- Starting age for timeline: {decision_age}\n"
        f"- Feelings about their real-life decision: {emotion_phrase}\n\n"
        f"Generate a realistic, emotionally complex alternate life timeline where this person made the OPPOSITE choice at age {decision_age}. "
        f"For example, if they said 'I left my job', in this timeline they stayed at the job. If they said 'I moved to a new city', "
        f"in this timeline they remained in their original city.\n\n"
        f"The decision they made was: '{decision_description}'\n"
        f"In this timeline, they did the OPPOSITE.\n\n"
        f"IMPORTANT GUIDELINES:\n"
        f"1. Show BOTH positive developments AND the challenges/struggles that came with each life stage\n"
        f"2. Include a mix of joys and hardships - no overly idealized or perfect life\n"
        f"3. Show that even this 'other path' includes its own forms of loss, pressure, and uncertainty\n"
        f"4. End each timeline entry with a subtle reflection that this life, like their real one, has its own imperfections\n"
        f"5. Convey that no matter which path we take, there will always be both joy and hardship\n\n"
        f"Start from age {decision_age} and include 6 major life events spanning the next 15-20 years.\n"
        f"For each age, write 3-4 narrative sentences that flow naturally and describe:\n"
        f"1. The specific location where they are (city, country, setting)\n"
        f"2. Their current life situation (job, relationships, achievements)\n"
        f"3. Their emotional state including both positive feelings AND struggles/challenges\n"
        f"4. A brief reflection acknowledging that this path, like any, has its own bittersweet beauty\n\n"
        f"Format: Each entry MUST start with 'Age XX - ' followed by the detailed narrative. DO NOT use any HTML tags or special formatting."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000  # Increased token limit to accommodate more nuanced responses
        )
        timeline_text = response.choices[0].message.content.strip()
        timeline_lines = [line.strip() for line in timeline_text.split("\n") if line.strip()]
        formatted_lines = []

        for line in timeline_lines:
            # Clean up any HTML-like tags that might be in the response
            line = re.sub(r'<[^>]+>', '', line)
            
            if re.match(r'^Age\s+\d+\s+-', line, re.IGNORECASE):
                formatted_lines.append(line)
            else:
                age_match = re.search(r'\b(\d+)\b', line)
                if age_match:
                    age = age_match.group(1)
                    description = re.sub(r'\b' + age + r'\b', '', line, 1).strip()
                    description = re.sub(r'^[-:]\s*', '', description).strip()
                    formatted_lines.append(f"Age {age} - {description}")
                else:
                    # If no age found, use the decision age plus an increment
                    next_age = decision_age + len(formatted_lines) * 5
                    formatted_lines.append(f"Age {next_age} - {line}")

        return formatted_lines if formatted_lines else timeline_lines

    except Exception as e:
        print(f"Error generating timeline: {e}")
        # Fallback timeline starting from decision age
        return [
            f"Age {decision_age} - Made the opposite choice at the crossroads of life. While excited about the new path, uncertainty lingers about what might have been.",
            f"Age {decision_age + 5} - Discovered unexpected talents and opportunities, though not without facing some difficult adjustments and moments of doubt.",
            f"Age {decision_age + 10} - Found a rhythm in this life path, with both rewarding accomplishments and persistent challenges that require continuous growth.",
            f"Age {decision_age + 15} - Built something meaningful, yet still wrestle with occasional thoughts of the road not taken.",
            f"Age {decision_age + 20} - Looking back with wisdom gained from both successes and failures, recognizing that no path is perfect—just differently imperfect."
        ]

# === 3. Render Instagram-style HTML ===
def generate_instagram_html(uploaded_image: Image.Image, caption: str, username: str = "ParallelYou") -> str:
    print("📸 generate_instagram_html CALLED")
    print("📸 type of uploaded_image:", type(uploaded_image))

    try:
        if not isinstance(uploaded_image, Image.Image):
            uploaded_image = Image.open(uploaded_image).convert("RGB")

        buffered = io.BytesIO()
        uploaded_image = uploaded_image.convert("RGB")
        uploaded_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        html_content = f"""
        <div style="width:100%; max-width:500px; margin:auto; border-radius:12px; overflow:hidden; font-family:sans-serif; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border:1px solid #FFD166;">
            <div style="padding:12px 16px; background-color:#FFF6E0; display:flex; align-items:center;">
                <div style="width:40px; height:40px; border-radius:50%; background-color:#FFD166; display:flex; justify-content:center; align-items:center; font-weight:bold; color:#5E4B28; margin-right:10px;">
                    {username[0].upper()}
                </div>
                <span style="font-weight:bold; color:#5E4B28;">{username}</span>
                <span style="margin-left:auto; color:#E09F3E;">•••</span>
            </div>
            <img src="data:image/png;base64,{img_base64}" style="width:100%; max-height:500px; object-fit:cover; display:block;">
            <div style="padding:15px; background:white;">
                <div style="display:flex; margin-bottom:10px; font-size:22px;">
                    <span style="margin-right:15px;">❤️</span>
                    <span style="margin-right:15px;">💬</span>
                    <span style="margin-right:15px;">🔄</span>
                    <span style="margin-left:auto;">🔖</span>
                </div>
                <p style="margin:5px 0;"><strong style="color:#5E4B28;">{username}</strong> {caption}</p>
                <div style="display:flex; margin-top:8px;">
                    <span style="margin-right:15px; color:#999;">❤️ {random.randint(24, 86)} likes</span>
                    <span style="color:#999;">💬 {random.randint(3, 14)} comments</span>
                </div>
                <p style="color:#999; font-size:12px; margin-top:8px;">Posted in your alternate universe • 2 hours ago</p>
            </div>
        </div>
        """
        return html_content

    except Exception as e:
        print("❌ Error generating Instagram HTML:", e)
        return "<p>Unable to render post.</p>"