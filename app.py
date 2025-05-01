# app.py
import os
import ssl  # Add this line

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import streamlit as st
import random
import openai
import re
import time
from PIL import Image
from io import BytesIO
from genai import generate_text, generate_audio, generate_cartoon_image_from_selfie, generate_instagram_caption
from utils import analyze_personality, generate_dynamic_life_timeline, generate_instagram_html
from genai import generate_parallel_letter

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set page configuration
st.set_page_config(
    page_title="Mirrorverse: Meet Your Other Self",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dreamy, mindful healing theme
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Raleway:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
    /* Primary dreamy gradient colors */
    :root {
        --gradient-start: #EEDCF5;
        --gradient-end: #FFF8E1;
        --accent-color: #9076B5;
        --text-color: #5D4E6D;
        --light-border: #D4C1EC;
    }
    
    /* Custom title styling with Playfair Display */
    .playfair-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 36px !important;
        font-weight: 600 !important;
        text-align: center !important;
        color: #6A4C93 !important; /* Darker purple for better contrast */
        margin-bottom: 20px !important;
        line-height: 1.4 !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(to bottom right, var(--gradient-start), var(--gradient-end));
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-12oz5g7 {
        background: linear-gradient(to bottom, rgba(238, 220, 245, 0.7), rgba(255, 248, 225, 0.7));
        backdrop-filter: blur(5px);
    }
    
    /* Headers with improved readability */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #6A4C93 !important; /* Darker purple */
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8) !important; /* White text shadow for contrast */
    }
    
    /* Body text with Raleway font */
    body, p, div, span, li {
        font-family: 'Raleway', sans-serif !important;
        color: var(--text-color);
    }
    
    /* Glowing effect for titles - more subtle for readability */
    .glow-text {
        text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8), 0 0 10px rgba(179, 157, 219, 0.3) !important;
        animation: glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8), 0 0 10px rgba(179, 157, 219, 0.3);
        }
        to {
            text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8), 0 0 15px rgba(179, 157, 219, 0.5);
        }
    }
    
    /* Buttons with gradient and animation */
    .stButton>button {
        background: linear-gradient(45deg, #9076B5, #F5E6AB) !important;
        color: #3D3354 !important; /* Darker text for better readability */
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-family: 'Raleway', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 10px rgba(177, 156, 217, 0.3) !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 15px rgba(177, 156, 217, 0.5), 0 0 20px rgba(177, 156, 217, 0.3) !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border: 2px solid var(--light-border) !important;
        border-radius: 15px !important;
        background-color: rgba(255, 255, 255, 0.7) !important;
        font-family: 'Raleway', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 10px rgba(177, 156, 217, 0.4) !important;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed var(--accent-color) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        background-color: rgba(255, 255, 255, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        background-color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #8669AD, #D4C1EC) !important;
        border-radius: 10px !important;
    }
    
    /* Card layout for content areas */
    .content-card {
        background-color: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 25px !important;
        border-left: 5px solid var(--accent-color) !important;
        transition: all 0.3s ease !important;
    }
    
    .content-card:hover {
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Success message */
    .success-message {
        background-color: rgba(228, 255, 228, 0.7) !important;
        border-left: 5px solid #9ED9B2 !important;
        padding: 15px !important;
        border-radius: 12px !important;
        margin: 20px 0 !important;
        backdrop-filter: blur(5px) !important;
    }
    
    /* Active sidebar item */
    .active-page {
        border-left: 4px solid var(--accent-color) !important;
        padding-left: 12px !important;
        font-weight: 600 !important;
        color: var(--accent-color) !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Custom container for the next button area */
    .next-button-container {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        margin-top: 30px !important;
        padding: 20px !important;
        border-radius: 20px !important;
        background: linear-gradient(to top, rgba(238, 220, 245, 0.5), rgba(255, 248, 225, 0.5)) !important;
        backdrop-filter: blur(5px) !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: var(--accent-color) !important;
        border-radius: 20px !important;
    }
    
    /* Navigation menu items - more readable */
    .css-1n543e5 {
        color: #533D7F !important;
        font-weight: 500 !important;
    }
    
    /* Chat bubbles styling */
    .bubble-left {
        background: rgba(255, 255, 255, 0.8) !important;
        padding: 12px 18px !important;
        border-radius: 18px !important;
        border-bottom-left-radius: 5px !important;
        margin: 5px 0 !important;
        max-width: 80% !important;
        align-self: flex-start !important;
        color: var(--text-color) !important;
        display: inline-block !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05) !important;
        backdrop-filter: blur(5px) !important;
    }
    
    .bubble-right {
        background: linear-gradient(to right, #8669AD, #A995C9) !important;
        padding: 12px 18px !important;
        border-radius: 18px !important;
        border-bottom-right-radius: 5px !important;
        margin: 5px 0 5px auto !important;
        max-width: 80% !important;
        color: white !important;
        display: block !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Chat title styling */
    .chat-title {
        padding: 15px !important;
        background: linear-gradient(to right, rgba(177, 156, 217, 0.3), rgba(245, 230, 171, 0.3)) !important;
        border-bottom: 1px solid rgba(212, 193, 236, 0.5) !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
        color: #533D7F !important;
        border-radius: 15px 15px 0 0 !important;
    }
    
    /* Instagram container styling */
    [style*="border:1px solid #FFD166"] {
        border: 1px solid var(--accent-color) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Letter box styling */
    .letter-box {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #D4C1EC !important;
        padding: 30px 35px !important;
        border-radius: 15px !important;
        font-family: 'Raleway', serif !important;
        line-height: 1.7 !important;
        color: #3D3354 !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
        white-space: pre-wrap !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Section headers - improved readability */
    .content-card h3, .content-card h4 {
        color: #533D7F !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state - Improved with default values and proper structure
def initialize_session_state():
    # Main state dictionaries
    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            'name': '',
            'gender': 'Male',
            'age': 25,
            'intro': ''
        }
    
    if "decision_info" not in st.session_state:
        st.session_state.decision_info = {
            'decision': '',
            'decision_age': 23,
            'decision_description': '',
            'emotion': []
        }
    
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = {}
    
    # Page navigation and progress
    if "page" not in st.session_state:
        st.session_state.page = 1
    
    if "progress" not in st.session_state:
        st.session_state.progress = 0
    
    # Content generation
    if "timeline" not in st.session_state:
        st.session_state.timeline = []
    
    if "selfie_image" not in st.session_state:
        st.session_state.selfie_image = None
    
    if "cartoon_photo" not in st.session_state:
        st.session_state.cartoon_photo = None
    
    if "generated_caption" not in st.session_state:
        st.session_state.generated_caption = ""
    
    if "letter_text" not in st.session_state:
        st.session_state.letter_text = ""
    
    if "audio_file" not in st.session_state:
        st.session_state.audio_file = None
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# Call the initialization function at app startup
initialize_session_state()

# Navigation
def go_to_page(page_num):
    st.session_state.page = page_num
    st.session_state.progress = min((page_num - 1) * 25, 100)  # 4 pages = 25% each

def go_next():
    st.session_state.page += 1
    st.session_state.progress = min((st.session_state.page - 1) * 25, 100)

def go_back():
    if st.session_state.page > 1:
        st.session_state.page -= 1
        st.session_state.progress = max((st.session_state.page - 1) * 25, 0)

# Generate timeline if needed - centralized function
def ensure_timeline_generated():
    if not st.session_state.timeline and st.session_state.user_info.get('name') and st.session_state.decision_info.get('decision'):
        with st.spinner("Generating your alternate timeline..."):
            st.session_state.analysis_result = analyze_personality(st.session_state.user_info.get('intro', ''))
            st.session_state.timeline = generate_dynamic_life_timeline(
                name=st.session_state.user_info.get('name', ''),
                intro_text=st.session_state.user_info.get('intro', ''),
                decision_text=st.session_state.decision_info.get('decision', ''),
                emotions=st.session_state.decision_info.get('emotion', [])
            )
        return True
    return False

# Generate cartoon photo if needed - centralized function
def ensure_cartoon_generated():
    if not st.session_state.cartoon_photo and st.session_state.selfie_image:
        with st.spinner("Creating your Parellel Instagram..."):
            try:
                timeline_content = "\n".join(st.session_state.timeline) if st.session_state.timeline else ""
                st.session_state.cartoon_photo = generate_cartoon_image_from_selfie(
                    st.session_state.selfie_image,
                    st.session_state.decision_info.get('decision', '')
                )
                # Generate caption along with the image
                timeline_text = "\n".join(st.session_state.timeline) if st.session_state.timeline else ""

                st.session_state.generated_caption = generate_instagram_caption(
                     st.session_state.decision_info.get('decision', ''),
                     timeline_text
                )

                return True
            except Exception as e:
                st.error(f"Error creating portrait: {e}")
                return False
    return False

# Sidebar Navigation
with st.sidebar:
    st.image("/Users/apple/Desktop/2025 Spring/MGT 575 AI and Social Media/app/logo.png", width=80)  # Replace the emoji icon with your logo
    st.title("🌌 Mirrorverse")
    st.markdown("---")
    
    # Navigation menu
    pages = {
        1: "📝 Your Story",
        2: "📜 Alternate Timeline",
        3: "📸 Parallel Instagram",
        4: "✉️ Letter from Future"
    }
    
    st.markdown("### Navigation")
    
    # Show user data summary in sidebar if available
    if st.session_state.user_info.get('name'):
        st.markdown(f"**Name:** {st.session_state.user_info.get('name')}")
        
    if st.session_state.user_info.get('age'):
        st.markdown(f"**Age:** {st.session_state.user_info.get('age')}")
        
    if st.session_state.decision_info.get('decision'):
        decision_text = st.session_state.decision_info.get('decision')
        if len(decision_text) > 50:
            decision_text = decision_text[:47] + "..."
        st.markdown(f"**Decision:** {decision_text}")
    
    st.markdown("---")
    
    for page_num, page_title in pages.items():
        if page_num == st.session_state.page:
            st.markdown(f"<div class='active-page'>{page_title}</div>", unsafe_allow_html=True)
        else:
            # Only disable future pages if required data is missing
            disabled = False
            if page_num > 1:
                if not st.session_state.user_info.get('name') or not st.session_state.decision_info.get('decision'):
                    disabled = True
                if page_num > 2 and not st.session_state.timeline:
                    disabled = True
            
            if st.button(page_title, key=f"nav_{page_num}", disabled=disabled, use_container_width=True):
                # Save current page data before navigation
                current_page = st.session_state.page
                
                # Navigate to the selected page
                go_to_page(page_num)
                
                # Generate required data if navigating forward
                if page_num > current_page:
                    if page_num >= 2:
                        ensure_timeline_generated()
                    
                    if page_num >= 3:
                        ensure_cartoon_generated()
    
    st.markdown("---")
    st.markdown("### Your Progress")
    st.progress(st.session_state.progress / 100)
    st.caption(f"{st.session_state.progress}% complete")
    
    st.markdown("---")
    st.caption("Made with ❤️ by Mirrorverse Team")

# Page 1: User Story Input
if st.session_state.page == 1:
    st.title("🌌 Mirrorverse: Meet Your Other Self")
    st.markdown("### Step 1: Upload your photo & Tell your story")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("#### 👤 About You")
        name = st.text_input("Your Name", value=st.session_state.user_info.get('name', ''), help="We'll use this to personalize your experience")
        st.session_state.user_info['name'] = name  # Update immediately
        
        cols = st.columns(2)
        with cols[0]:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.user_info.get('gender', 'Male')))
            st.session_state.user_info['gender'] = gender  # Update immediately
        with cols[1]:
            age = st.number_input("Age", min_value=10, max_value=100, value=st.session_state.user_info.get('age', 25))
            st.session_state.user_info['age'] = age  # Update immediately
        
        intro = st.text_area("Brief Self-Introduction", 
                            value=st.session_state.user_info.get('intro', ''),
                            placeholder="Tell us a little about yourself, your personality, and what matters to you...",
                            help="This helps us understand who you are")
        st.session_state.user_info['intro'] = intro  # Update immediately
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔀 The Turning Point")
        
        # New: Add numeric input for the age when decision happened
        decision_age = st.number_input("At what age did this decision happen?", 
                                      min_value=10, 
                                      max_value=100, 
                                      value=st.session_state.decision_info.get('decision_age', 23),
                                      help="The age when you made this life-changing decision")
        st.session_state.decision_info['decision_age'] = decision_age  # Update immediately
        
        # New: Use text area for the decision description
        decision_description = st.text_area("Describe a major life decision you made at that age", 
                                          value=st.session_state.decision_info.get('decision_description', ''),
                                          placeholder="Examples: Left my job to start a business, Moved to a new city, Changed my career path...",
                                          help="This is the decision we'll explore an alternate path for")
        st.session_state.decision_info['decision_description'] = decision_description  # Update immediately
        
        # Generate and store the combined decision text
        if decision_age and decision_description:
            combined_decision = f"At the age of {decision_age}, I {decision_description}."
            st.session_state.decision_info['decision'] = combined_decision
            
            # Display the combined text with a subtle background
            st.markdown(f"""
            <div style="background-color: rgba(255, 246, 224, 0.7); padding: 10px; border-radius: 10px; margin-top: 10px;">
                <p style="margin: 0; color: #6A4C93;"><i>{combined_decision}</i></p>
            </div>
            """, unsafe_allow_html=True)
        
        emotion = st.multiselect(
            "How do you feel about this decision?",
            ["Regret", "Curiosity", "Pride", "Contentment", "Bittersweet", "Uncertainty", "Gratitude", "Nostalgia"],
            default=st.session_state.decision_info.get('emotion', []),
            help="Select all that apply"
        )
        st.session_state.decision_info['emotion'] = emotion  # Update immediately
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("#### 📷 Your Photo")
        uploaded_selfie = st.file_uploader("Upload a clear front-facing photo", 
                                          type=["jpg", "jpeg", "png"],
                                          help="This will be used to create your parallel universe avatar")
        
        # Update the session state with the uploaded image
        if uploaded_selfie:
            st.session_state.selfie_image = uploaded_selfie
            st.image(uploaded_selfie, caption="Your Photo", use_container_width=True)
            st.success("✅ Photo uploaded successfully!")
        elif st.session_state.selfie_image:
            # Display the previously uploaded photo
            st.image(st.session_state.selfie_image, caption="Your Photo", use_container_width=True)
            st.success("✅ Photo already uploaded!")
        else:
            st.warning("⚠️ Please upload your personal photo to continue.")
            st.image("https://via.placeholder.com/300x400?text=Your+Photo+Here", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Next button area with progress indicator
    st.markdown("<div class='next-button-container'>", unsafe_allow_html=True)
    
    ready_to_proceed = (st.session_state.selfie_image is not None and 
                       st.session_state.user_info.get('name') and 
                       st.session_state.decision_info.get('decision'))
    
    if ready_to_proceed:
        st.success("✨ All set! Click Next to discover your parallel universe")
    else:
        missing_items = []
        if not st.session_state.selfie_image:
            missing_items.append("photo")
        if not st.session_state.user_info.get('name'):
            missing_items.append("name")
        if not st.session_state.decision_info.get('decision'):
            missing_items.append("life decision")
        
        if missing_items:
            st.info(f"⏳ Please complete your {' and '.join(missing_items)} to continue")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ NEXT: See Your Alternate Timeline", disabled=not ready_to_proceed, use_container_width=True):
            # Generate timeline and go to next page
            ensure_timeline_generated()
            go_next()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Page 2: Life Trajectory Simulation (Dynamic) - Visual Timeline
elif st.session_state.page == 2:
    # Ensure timeline is generated
    if not st.session_state.timeline:
        ensure_timeline_generated()
    
    st.title("📜 Your Alternate Life Timeline")
    
    # Extract the decision age and description
    decision_text = st.session_state.decision_info.get('decision', '')
    decision_age = st.session_state.decision_info.get('decision_age', 23)
    decision_description = ""
    
    if "I " in decision_text:
        decision_description = decision_text.split("I ", 1)[1].strip()
        if decision_description.endswith("."):
            decision_description = decision_description[:-1]
    
    # Add a summary of the user's input for reference
    st.markdown("<div class='content-card' style='background-color: #FFF6E0;'>", unsafe_allow_html=True)
    st.markdown("### 🔄 The Road Not Taken")
    st.markdown(f"<p><strong>Your real-life decision:</strong> {decision_text}</p>", unsafe_allow_html=True)
    
    # Add the alternate decision explanation
    st.markdown(f"""<p><strong>In this parallel universe:</strong> <span style="background-color: rgba(224, 159, 62, 0.2); padding: 5px 10px; border-radius: 8px;">
    At age {decision_age}, you made the opposite choice - what if you <i>hadn't</i> {decision_description}?</span></p>""", unsafe_allow_html=True)
    
    # Show emotions if they were selected
    if st.session_state.decision_info.get('emotion'):
        emotion_badges = " ".join([f"<span style='background-color: #FFD166; color: #5E4B28; padding: 3px 8px; border-radius: 10px; margin-right: 5px; font-size: 0.8em;'>{emotion}</span>" for emotion in st.session_state.decision_info.get('emotion', [])])
        st.markdown(f"<p><strong>Your feelings about your real-life choice:</strong> {emotion_badges}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Visual timeline
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("<h3>🌈 Parallel Universe Timeline</h3>", unsafe_allow_html=True)
    
    # Create visual timeline with alternating sides
    st.markdown("""
    <style>
    .timeline-container {
        position: relative;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .timeline-container::after {
        content: '';
        position: absolute;
        width: 6px;
        background-color: #FFD166;
        top: 0;
        bottom: 0;
        left: 50%;
        margin-left: -3px;
        border-radius: 10px;
    }
    
    .timeline-item {
        padding: 10px 40px;
        position: relative;
        width: 50%;
        box-sizing: border-box;
    }
    
    .timeline-left {
        left: 0;
    }
    
    .timeline-right {
        left: 50%;
    }
    
    .timeline-content {
        padding: 15px;
        background-color: white;
        position: relative;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #E09F3E;
    }
    
    .timeline-left .timeline-content {
        border-left: 5px solid #E09F3E;
        border-right: none;
    }
    
    .timeline-right .timeline-content {
        border-right: 5px solid #E09F3E;
        border-left: none;
    }
    
    .timeline-content::after {
        content: '';
        position: absolute;
        width: 20px;
        height: 20px;
        background-color: white;
        border: 4px solid #FFD166;
        top: 15px;
        border-radius: 50%;
        z-index: 1;
    }
    
    .timeline-left .timeline-content::after {
        right: -12px;
    }
    
    .timeline-right .timeline-content::after {
        left: -12px;
    }
    
    .timeline-age {
        font-weight: bold;
        color: #E09F3E;
        margin-bottom: 5px;
        font-size: 1.2em;
    }
    
    .keyword-badge {
        display: inline-block;
        background-color: #FFD166;
        color: #5E4B28;
        padding: 3px 8px;
        border-radius: 10px;
        margin-right: 4px;
        margin-bottom: 4px;
        font-size: 0.9em;
        font-weight: bold;
    }
    
    .timeline-description {
        color: #5E4B28;
    }
    
    @media screen and (max-width: 600px) {
        .timeline-container::after {
            left: 31px;
        }
        
        .timeline-item {
            width: 100%;
            padding-left: 70px;
            padding-right: 25px;
        }
        
        .timeline-left, .timeline-right {
            left: 0;
        }
        
        .timeline-content::after {
            left: -12px;
        }
    }
    </style>
    
    <div class="timeline-container">
    """, unsafe_allow_html=True)
    
    # Extract the timeline entries and parse them
    timeline_entries = []
    for line in st.session_state.timeline:
        # Remove any HTML tags from the line
        line = re.sub(r'<[^>]+>', '', line)
        
        # Try to parse the age from the timeline entry
        try:
            # Look for patterns like "Age XX" or "XX -" at the beginning of the line
            age_match = re.search(r'^(Age\s+)?(\d+)(\s*-\s*|\s*:\s*|\s+)', line, re.IGNORECASE)
            
            if age_match:
                age = age_match.group(2)
                # Get the description part (everything after age and delimiter)
                description = line[age_match.end():].strip() 
                timeline_entries.append((int(age), description))
            else:
                # If no age pattern found, use a default age and the whole line as description
                # Extract any numbers that might be ages
                any_number = re.search(r'\b(\d{1,2})\b', line)
                if any_number:
                    potential_age = int(any_number.group(1))
                    if 18 <= potential_age <= 90:  # Reasonable age range
                        # Remove the age from the description
                        description = re.sub(r'\b' + any_number.group(1) + r'\b', '', line, 1).strip()
                        description = re.sub(r'^[-:]\s*', '', description).strip()
                        timeline_entries.append((potential_age, description))
                    else:
                        # Use age progression based on position in timeline
                        default_age = decision_age + len(timeline_entries) * 4
                        timeline_entries.append((default_age, line))
                else:
                    # Use age progression based on position in timeline
                    default_age = decision_age + len(timeline_entries) * 4
                    timeline_entries.append((default_age, line))
        except:
            # If parsing fails, add with a calculated age
            default_age = decision_age + len(timeline_entries) * 4
            timeline_entries.append((default_age, line))
    
    # Sort entries by age
    timeline_entries.sort(key=lambda x: x[0])
    
    # Create sample timeline entries if none exist (for development/fallback)
    if not timeline_entries:
        timeline_entries = [
            (decision_age, "Decided to stay at TikTok UK as e-commerce key account manager. Found mentorship from senior colleagues and started building expertise in digital marketing."),
            (decision_age + 3, "Promoted to Team Lead at TikTok, managing a small team of account managers. Started dating Sam, whom I met at a company event."),
            (decision_age + 5, "Accepted a position at TikTok's headquarters in London. Managing larger accounts and building strong relationships with major brands."),
            (decision_age + 8, "Married Sam and bought our first home in London. Promoted to Regional Director for Northern Europe at TikTok."),
            (decision_age + 12, "Taking a sabbatical to travel with Sam. Exploring Southeast Asia while considering next career moves."),
            (decision_age + 15, "Returned from travels with a renewed perspective. Started my own digital marketing consultancy with contacts from my TikTok years.")
        ]
    
    # Display timeline entries with alternating sides
    import html  # Import the html module for escaping HTML characters
    
    for i, (age, description) in enumerate(timeline_entries):
        side_class = "timeline-left" if i % 2 == 0 else "timeline-right"
        
        # Generate more specific keywords
        keywords = []
        description_lower = description.lower()
        
        # Make sure "Age" doesn't appear in the description if it was part of the parsing
        if description.startswith("Age"):
            description = re.sub(r'^Age\s+\d+\s*[-:]\s*', '', description)
            description_lower = description.lower()

        # Location extraction - higher priority
        location_patterns = [
            r'(?:in|to|at|from)\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)', # City/Country names
            r'(?:moved to|relocated to|living in|settled in|journey to|traveled to|visiting|arrived in|residing in|based in)\s+([A-Za-z\s]+)'
        ]

        for pattern in location_patterns:
            location_matches = re.findall(pattern, description)
            if location_matches:
                location = location_matches[0].strip().split(',')[0].strip()  # Take just the city part if there's a comma
                if len(location.split()) <= 2:  # Only use if it's 1-2 words
                    keywords.append(location.upper())
                    break

        # If no specific location found, check for regional keywords
        if not any(keyword in keywords for keyword in ["MOVED", "RELOCATION", "TRAVEL"]):
            if any(word in description_lower for word in ["abroad", "overseas", "foreign", "international"]):
                keywords.append("INTERNATIONAL")
            elif any(word in description_lower for word in ["moved", "relocation", "moving"]):
                keywords.append("MOVED")
            elif any(word in description_lower for word in ["travel", "journey", "adventure", "exploring", "backpacking"]):
                keywords.append("TRAVEL")

        # Specific career/job extraction
        career_fields = {
            "TECH": ["software", "developer", "programmer", "coding", "tech", "startup", "digital", "computer", "IT", "technology", "tiktok"],
            "MEDICINE": ["doctor", "medical", "hospital", "nurse", "healthcare", "clinic", "patient", "physician", "surgery", "health"],
            "ARTS": ["artist", "painter", "exhibition", "gallery", "creative", "studio", "design", "music", "perform", "singing", "acting"],
            "FINANCE": ["finance", "bank", "investment", "market", "stock", "financial", "analyst", "accounting", "economy"],
            "EDUCATION": ["teacher", "professor", "lecturer", "school", "university", "college", "teaching", "education", "academic", "student"],
            "SCIENCE": ["research", "scientist", "laboratory", "experiment", "discovery", "phd", "science", "biology", "chemistry", "physics"],
            "BUSINESS": ["entrepreneur", "founder", "ceo", "business", "company", "startup", "venture", "corporation", "management"],
            "MEDIA": ["journalism", "writer", "author", "publisher", "media", "news", "editor", "blog", "publishing", "reporter"],
            "CULINARY": ["chef", "restaurant", "cooking", "food", "culinary", "kitchen", "bakery", "cuisine", "catering"],
        }

        for field, terms in career_fields.items():
            if any(term in description_lower for term in terms):
                keywords.append(field)
                break

        # If no career field found, try to extract job title
        if not any(field in keywords for field in career_fields.keys()) and any(word in description_lower for word in ["job", "career", "work", "profession", "hired", "company", "position", "role", "promoted", "director", "manager"]):
            job_matches = re.findall(r'(?:as a|as an|became a|hired as|position as|role as|job as|career as|promoted to) ([a-zA-Z\s]+)', description_lower)
            if job_matches:
                job_title = job_matches[0].strip().upper()
                if len(job_title.split()) <= 2:  # Only use if it's 1-2 words
                    keywords.append(job_title)
                else:
                    keywords.append("CAREER")
            else:
                keywords.append("CAREER")

        # Situation/life events extraction
        situation_categories = {
            "MARRIAGE": ["married", "wedding", "engagement", "proposal", "fiancé", "fiancée", "bride", "groom"],
            "DIVORCE": ["divorce", "separated", "split", "breakup", "broke up"],
            "RELATIONSHIP": ["dating", "relationship", "partner", "girlfriend", "boyfriend", "romance", "love"],
            "PARENTHOOD": ["baby", "child", "born", "pregnancy", "pregnant", "father", "mother", "parent", "adoption"],
            "GRADUATION": ["graduate", "graduated", "diploma", "degree", "commencement", "alumni"],
            "NEW HOME": ["new home", "house", "apartment", "moving in", "lease", "mortgage", "bought a"],
            "PROMOTION": ["promotion", "promoted", "raise", "advancement", "senior role", "leadership"],
            "SETBACK": ["setback", "failure", "rejected", "denial", "struggle", "obstacle", "difficulty", "challenge"],
            "ADVENTURE": ["adventure", "journey", "exploration", "discovered", "expedition", "wilderness", "trip"],
            "HEALTH ISSUE": ["health", "illness", "disease", "medical", "condition", "diagnosis", "hospital", "recovery"],
        }

        for situation, terms in situation_categories.items():
            if any(term in description_lower for term in terms):
                keywords.append(situation)
                break

        # Emotional state extraction
        emotion_categories = {
            "JOY": ["happy", "joy", "delighted", "thrilled", "ecstatic", "excited", "overjoyed", "elated", "jubilant"],
            "PRIDE": ["proud", "accomplished", "achievement", "success", "triumph", "victorious", "confident"],
            "LOVE": ["love", "passion", "devoted", "affection", "adoration", "tenderness", "fondness"],
            "RELIEF": ["relief", "relieved", "unburdened", "freed", "liberated", "relaxed", "eased"],
            "FEAR": ["fear", "afraid", "anxious", "worried", "concerned", "nervous", "frightened", "terrified"],
            "SADNESS": ["sad", "heartbroken", "grieving", "depressed", "melancholy", "sorrow", "unhappy", "upset"],
            "ANGER": ["angry", "frustrated", "annoyed", "irritated", "furious", "resentful", "outraged"],
            "HOPE": ["hope", "hopeful", "optimistic", "promising", "looking forward", "anticipation", "excitement"],
            "PEACE": ["peace", "peaceful", "calm", "tranquil", "serene", "content", "satisfied", "fulfilled"],
            "REGRET": ["regret", "remorse", "guilt", "sorry", "apologetic", "repentant", "shame"],
        }

        for emotion, terms in emotion_categories.items():
            if any(term in description_lower for term in terms):
                keywords.append(emotion)
                break

        # If we don't have at least one emotion detected, try harder to find emotional content
        if not any(emotion in keywords for emotion in emotion_categories.keys()):
            # Check for feeling words
            feeling_patterns = [
                r'(?:feeling|felt|feels|feel) ([a-z]+)',
                r'(?:was|is|am) ([a-z]+) (?:about|with|by)'
            ]
            
            for pattern in feeling_patterns:
                feeling_matches = re.findall(pattern, description_lower)
                if feeling_matches:
                    feeling = feeling_matches[0].strip().upper()
                    if len(feeling) > 3 and feeling not in ["ALSO", "THEN", "WHEN", "WHERE"]:
                        keywords.append(feeling)
                        break

        # Limit to max 3 keywords with priority for location, job/situation, and emotion
        # Ensure diversity of keyword types
        final_keywords = []

        # First priority: Location
        location_kws = [kw for kw in keywords if kw in ["INTERNATIONAL", "MOVED", "TRAVEL"] or re.match(r'^[A-Z]+$', kw)]
        if location_kws:
            final_keywords.append(location_kws[0])

        # Second priority: Career/Job
        career_kws = [kw for kw in keywords if kw in list(career_fields.keys()) + ["CAREER"]]
        if career_kws:
            final_keywords.append(career_kws[0])

        # Third priority: Situation
        situation_kws = [kw for kw in keywords if kw in situation_categories.keys()]
        if situation_kws:
            final_keywords.append(situation_kws[0])

        # Fourth priority: Emotion
        emotion_kws = [kw for kw in keywords if kw in emotion_categories.keys() or kw not in location_kws + career_kws + situation_kws]
        if emotion_kws and len(final_keywords) < 3:
            final_keywords.append(emotion_kws[0])

        # Fill remaining slots with other keywords
        remaining_kws = [kw for kw in keywords if kw not in final_keywords]
        while len(final_keywords) < 3 and remaining_kws:
            final_keywords.append(remaining_kws.pop(0))

        # Replace the original keywords with our improved ones
        keywords = final_keywords[:3]
        
        # Create keyword badges
        keyword_html = ""
        if keywords:
            keyword_html = "<div style='margin-top: 5px;'>"
            for kw in keywords:
                keyword_html += f"<span class='keyword-badge'>{kw}</span>"
            keyword_html += "</div>"
        
        # Escape HTML special characters in the description to avoid rendering issues
        escaped_description = html.escape(description)
        
        # Highlight the first timeline entry (decision point) with a special style
        highlight_style = ""
        if i == 0:
            highlight_style = "background-color: rgba(224, 159, 62, 0.1); border-left-width: 8px;"
        
        st.markdown(f"""
        <div class="timeline-item {side_class}">
            <div class="timeline-content" style="{highlight_style}">
                <div class="timeline-age">Age {age}</div>
                {keyword_html}
                <div class="timeline-description">{escaped_description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation buttons with improved layout
    st.markdown("<div class='next-button-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Your Story", use_container_width=True):
            go_back()
    with col2:
        # Next button to immediately navigate without generating image
        if st.button("Next: See Your Parallel Instagram ➡️", use_container_width=True):
            # Pre-generate cartoon for next page to improve user experience
            ensure_cartoon_generated()
            go_next()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Page 3: Parallel Universe Instagram Post
elif st.session_state.page == 3:
    st.title("📸 Your Parallel Universe Instagram Post")

    # Initialize chat state ONLY if not already present
    if "show_chat" not in st.session_state:
        st.session_state["show_chat"] = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_msg" not in st.session_state:
        st.session_state.user_msg = ""

    # Function to handle message sending without page rerun
    def send_message():
        if st.session_state.user_msg and st.session_state.user_msg.strip():
            user_input = st.session_state.user_msg
            
            # Add user message to history immediately to avoid delay
            temp_history = st.session_state.chat_history.copy()
            temp_history.append((user_input, "..."))
            st.session_state.chat_history = temp_history
            
            # Clear input field right away
            st.session_state.user_msg = ""
            
            # Generate response without spinner (which causes flickering)
            response = generate_text(
                f"You are the user's alternate self, who lived a different life described below. "
                f"Reply casually in a short, first-person, emotionally supportive way, like you're chatting with your real self as a friend. "
                f"If the user's message feels sad, insecure, or self-critical, show empathy and gently share that you've had hard times too. "
                f"End with an uplifting or comforting note if it feels right.\n\n"
                f"Alternate timeline:\n{st.session_state.timeline}\n\n"
                f"User said: {user_input}"
            )
            
            # Update chat history with the actual response
            st.session_state.chat_history[-1] = (user_input, response)

    # Layout: Left = Instagram Post, Right = Chat (if toggled)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)

        selfie_image = st.session_state.selfie_image
        timeline = st.session_state.timeline

        # Extract age from timeline line
        def extract_age(line):
            match = re.search(r'Age\s+(\d+)', line)
            return int(match.group(1)) if match else -1

        # Pick one event from age 20–30
        timeline_20s = [line for line in timeline if 20 <= extract_age(line) <= 30]
        chosen_event = random.choice(timeline_20s) if timeline_20s else "Enjoying the little things in life."

        # Generate caption if not yet generated
        if not st.session_state.get("generated_caption"):
            with st.spinner("Generating your Instagram caption..."):
                st.session_state.generated_caption = generate_instagram_caption(
                    chosen_event,
                    "\n".join(timeline)
                )

        # Toggle chat by clicking avatar-style button
        if st.button("👤 " + (st.session_state.user_info.get("name") or "Parallel You"), key="toggle_chat"):
            st.session_state["show_chat"] = not st.session_state["show_chat"]
            # Don't rerun - just let the state change apply on next frame

        # Render Instagram HTML post
        html_code = generate_instagram_html(
            selfie_image,
            st.session_state.generated_caption,
            username=st.session_state.user_info.get('name', 'ParallelYou')
        )
        st.components.v1.html(html_code, height=850, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)

    # Right side: chat (only when toggled)
    with col2:
        if st.session_state["show_chat"]:
            st.markdown("<div class='content-card' style='padding: 0; overflow: hidden;'>", unsafe_allow_html=True)
            
            # Updated Chat CSS to fix the yellowish background issue
            st.markdown("""
            <style>
            /* Chat title styling - keep this */
            .chat-title {
                padding: 15px;
                background: linear-gradient(to right, rgba(177, 156, 217, 0.3), rgba(245, 230, 171, 0.3));
                border-bottom: 1px solid rgba(212, 193, 236, 0.5);
                font-weight: bold;
                font-size: 1.1em;
                color: #533D7F;
                border-radius: 15px 15px 0 0;
            }
            
            /* Main chat container - removed fixed height and background */
            .chat-wrapper {
                display: flex;
                flex-direction: column;
                background: transparent;
            }
            
            /* Messages area - removed fixed height and yellowish background */
            .messages-container {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                background: transparent;
                display: flex;
                flex-direction: column;
                justify-content: flex-start;
                align-items: stretch;
                min-height: 400px;
            }
            
            /* Individual message bubbles - left bubble has white background */
            .bubble-left {
                background: rgba(255, 255, 255, 0.8);
                padding: 10px 15px;
                border-radius: 18px;
                border-bottom-left-radius: 5px;
                margin: 5px 0;
                max-width: 80%;
                align-self: flex-start;
                color: #5E4B28;
                display: inline-block;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            
            /* Right bubble maintains the gradient */
            .bubble-right {
                background: linear-gradient(to right, #8669AD, #A995C9);
                padding: 10px 15px;
                border-radius: 18px;
                border-bottom-right-radius: 5px;
                margin: 5px 0 5px auto;
                max-width: 80%;
                color: white;
                display: block;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            
            /* Input area - kept light background to distinguish input area */
            .input-container {
                padding: 15px;
                background-color: rgba(255, 246, 224, 0.3);
                border-top: 1px solid rgba(255, 232, 184, 0.3);
                display: flex;
                border-radius: 0 0 15px 15px;
            }
            
            /* Hide default Streamlit elements */
            .element-container {margin-bottom: 0 !important;}
            .st-emotion-cache-1wmy9hl {padding: 0 !important;}
            .st-emotion-cache-1kyxreq {margin-top: 0 !important; padding-top: 0 !important;}
            .stTextInput {margin-bottom: 0 !important;}
            .stForm {margin-bottom: 0 !important;}
            .stButton {margin-bottom: 0 !important;}
            
            /* Form styling */
            .chat-form {
                display: flex;
                width: 100%;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* Fix for form styling */
            .chat-form > div {
                width: 100%;
                margin: 0 !important;
                padding: 0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Chat header
            st.markdown('<div class="chat-title">💬 Chat with Your Parallel Self</div>', unsafe_allow_html=True)
            
            # Start the chat wrapper
            st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
            
            # Messages area container - fixed position
            messages_container = st.container()
            
            with messages_container:
                st.markdown('<div class="messages-container">', unsafe_allow_html=True)
                if st.session_state.chat_history:
                    for user_q, ai_a in st.session_state.chat_history:
                        st.markdown(f'<div class="bubble-right">{user_q}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="bubble-left">{ai_a}</div>', unsafe_allow_html=True)
                else:
                    # Welcome message if no chat history
                    st.markdown('<div class="bubble-left">Hi there! I\'m your parallel self from another timeline. What would you like to know about my life?</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Script to scroll to bottom of messages and handle Enter key press
            st.markdown("""
            <script>
            // Function to scroll to bottom of messages
            function scrollToBottom() {
                const messagesContainer = document.querySelector('.messages-container');
                if (messagesContainer) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }
            
            // Execute scroll immediately
            scrollToBottom();
            
            // Also scroll after the DOM is fully loaded
            document.addEventListener('DOMContentLoaded', function() {
                scrollToBottom();
                setTimeout(scrollToBottom, 100);
            });
            
            // MutationObserver to detect when new messages are added
            const targetNode = document.querySelector('.messages-container');
            if (targetNode) {
                const observer = new MutationObserver(function() {
                    scrollToBottom();
                });
                
                observer.observe(targetNode, { childList: true, subtree: true });
            }
            
            // Add event listener for Enter key on input field
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    const inputField = document.querySelector('input[aria-label="Ask your parallel self anything!"]');
                    const submitButton = document.querySelector('button[type="submit"]');
                    
                    if (inputField && submitButton && document.activeElement === inputField) {
                        event.preventDefault();
                        submitButton.click();
                    }
                }
            });
            </script>
            """, unsafe_allow_html=True)
            
            # Custom input area with form to prevent page refreshes
            st.markdown('<div class="input-container">', unsafe_allow_html=True)
            
            # Use a form to control submission and prevent page reloads
            with st.form(key="chat_form", clear_on_submit=False):
                st.markdown('<div class="chat-form">', unsafe_allow_html=True)
                cols = st.columns([5, 1])
                
                with cols[0]:
                    # Text input that updates session state directly
                    msg = st.text_input(
                        "Ask your parallel self anything!",
                        key="user_msg",
                        label_visibility="collapsed"
                    )
                
                with cols[1]:
                    # Submit button that calls our callback
                    submitted = st.form_submit_button("Send", on_click=send_message)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Close the chat wrapper
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Note about closing chat
            st.caption("👆 Click the avatar on the left to hide chat")
            
            st.markdown("</div>", unsafe_allow_html=True)

    # Navigation
    st.markdown("<div class='next-button-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Timeline", use_container_width=True):
            go_back()
    with col2:
        if st.button("Next: Read Letter from Future ➡️", use_container_width=True):
            go_next()
    st.markdown("</div>", unsafe_allow_html=True)

# Page 4: A Letter from Your Parallel Self
elif st.session_state.page == 4:
    st.title("📜 A Letter from Your Parallel Self")

    # Generate letter content if not already available
    if not st.session_state.letter_text:
        with st.spinner("Your other self is writing to you..."):
            timeline = "\n".join(st.session_state.timeline)
            name = st.session_state.user_info.get('name', 'you')
            st.session_state.letter_text = generate_parallel_letter(timeline, name)

    # Letter content - displayed in "paper" style (not editable)
    st.markdown("""
    <style>
    .letter-box {
        background-color: #fffdf6;
        border: 1px solid #f2e6c2;
        padding: 25px 30px;
        border-radius: 12px;
        font-family: 'Georgia', serif;
        line-height: 1.7;
        color: #4B3E2A;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='letter-box'>{st.session_state.letter_text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Audio playback
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.subheader("🎧 Listen to Your Letter")
    if not st.session_state.audio_file:
        with st.spinner('Generating your voice...'):
            gender = st.session_state.user_info['gender'].lower()
            voice = "nova" if gender == "female" else "onyx" if gender == "male" else "echo"
            st.session_state.audio_file = generate_audio(st.session_state.letter_text, voice)

    st.audio(st.session_state.audio_file, format="audio/mp3")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("⬅️ Back"):
            go_back()
    with col2:
        st.markdown("### Your Mirrorverse Journey is Complete! ✨")
        st.markdown("Thank you for exploring your parallel universe. Feel free to navigate to any previous page to revisit your alternate timeline.")