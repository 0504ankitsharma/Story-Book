import os
import streamlit as st
from transformers import pipeline
from typing import Dict
from gtts import gTTS
from together import Together
from googletrans import Translator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define supported Indian languages
SUPPORTED_LANGUAGES = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "தமிழ் (Tamil)": "ta",
    "తెలుగు (Telugu)": "te",
    "മലയാളം (Malayalam)": "ml",
    "ಕನ್ನಡ (Kannada)": "kn",
    "বাংলা (Bengali)": "bn",
    "ગુજરાતી (Gujarati)": "gu",
    "मराठी (Marathi)": "mr",
    "ਪੰਜਾਬੀ (Punjabi)": "pa"
}

# Custom color theme
THEME = {
    'primary': '#FF6B6B',     # Warm Red
    'secondary': '#4ECDC4',   # Turquoise
    'accent': '#FFE66D',      # Sunny Yellow
    'background': '#F7F7F7',  # Light Gray
    'text': '#2C3E50'         # Dark Blue-Gray
}

def set_custom_theme():
    """Apply custom CSS styling"""
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {THEME['background']};
            color: {THEME['text']};
        }}
        .stButton>button {{
            background-color: {THEME['primary']};
            color: white;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stSelectbox {{
            border-radius: 8px;
            border: 2px solid {THEME['secondary']};
        }}
        .stExpander {{
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        h1, h2, h3 {{
            color: {THEME['primary']};
        }}
        .story-container {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin: 10px 0;
        }}
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "story_english" not in st.session_state:
        st.session_state.story_english = None
    if "story_translated" not in st.session_state:
        st.session_state.story_translated = None
    if "audio_file_path" not in st.session_state:
        st.session_state.audio_file_path = None
    if "caption" not in st.session_state:
        st.session_state.caption = None
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False

def img2txt(url: str) -> str:
    """Generate caption from image"""
    try:
        captioning_model = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        text = captioning_model(url, max_new_tokens=20)[0]["generated_text"]
        return text
    except Exception as e:
        st.error(f"Error in image captioning: {str(e)}")
        return None

def txt2story(prompt: str) -> str:
    """Generate story from prompt"""
    try:
        client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))
        
        story_prompt = f"Write a short story of no more than 250 words based on the following prompt: {prompt}"
        
        stream = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": '''As an experienced short story writer, write a meaningful story 
                influenced by the provided prompt. Ensure the story does not exceed 250 words.'''},
                {"role": "user", "content": story_prompt}
            ],
            top_k=5,
            top_p=0.8,
            temperature=1.5,
            stream=True
        )
        
        story = ''
        for chunk in stream:
            story += chunk.choices[0].delta.content
        return story
    except Exception as e:
        st.error(f"Error in story generation: {str(e)}")
        return None

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language"""
    if target_lang == "en":
        return text
    
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    except Exception as e:
        st.warning(f"Translation failed: {str(e)}. Showing original text.")
        return text

def create_audio(text: str, language_code: str) -> bool:
    """
    Create audio file from text in specified language
    Args:
        text (str): Text to convert to speech
        language_code (str): Language code (e.g., 'hi' for Hindi, 'en' for English)
    Returns:
        bool: Success status of audio creation
    """
    try:
        # Create audio file in specified language
        tts = gTTS(text=text, lang=language_code)
        tts.save("story_audio.mp3")
        return True
    except Exception as e:
        st.error(f"Error in audio generation: {str(e)}")
        return False

def get_user_preferences() -> Dict[str, str]:
    """Get user preferences for story generation"""
    return {
        'region': st.selectbox("🗺️ Region", ["North India", "South India", "East India", "West India", "Central India"]),
        'genre': st.selectbox("📚 Genre", ["Mythology", "Historical Fiction", "Bollywood-inspired Drama", "Folklore"]),
        'setting': st.selectbox("🏛️ Setting", ["Ancient India", "Modern-day City", "Village Life", "Freedom Struggle Era"]),
        'plot': st.selectbox("📝 Plot", ["Overcoming obstacles", "Family saga", "Love story", "Friendship and loyalty"]),
        'tone': st.selectbox("🎭 Tone", ["Emotional", "Inspirational", "Humorous", "Mysterious"]),
        'theme': st.selectbox("💫 Theme", ["Karma", "Unity in Diversity", "Tradition vs. Modernity", "Hope"]),
        'conflict': st.selectbox("⚔️ Conflict Type", ["Class struggles", "Internal moral dilemma", "Man vs. Nature", "Generational conflict"]),
        'twist': st.selectbox("🌀 Mystery/Twist", ["Reincarnation", "Hidden lineage", "Unexpected sacrifice", "Spiritual revelation"]),
        'ending': st.selectbox("🎬 Ending", ["Happy", "Bittersweet", "Open-ended", "Tragic"])
    }

def main():
    # Page configuration
    st.set_page_config(
        page_title="🎨 Magical Indian Stories ✨",
        page_icon="🖼️",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Apply custom theme
    set_custom_theme()
    
    # App header
    st.markdown("""
        <h1 style='text-align: center; padding: 20px;'>
            ✨ मंत्रमुग्ध कहानियाँ | Enchanted Stories ✨
        </h1>
    """, unsafe_allow_html=True)

    # Language selector in sidebar
    selected_language = st.sidebar.selectbox(
        "🗣️ Select Story Language",
        list(SUPPORTED_LANGUAGES.keys()),
        index=0
    )

    # Get the language code for the selected language
    current_lang_code = SUPPORTED_LANGUAGES[selected_language]

    # Main layout
    col1, col2 = st.columns([2, 3])

    with col1:
        # Image upload
        st.markdown("## 📷 Upload Your Magic Portal")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

        # Story preferences
        st.markdown("## 🎭 Customize Your Tale")
        preferences = get_user_preferences()

    with col2:
        if uploaded_file is not None:
            # Display image
            st.markdown("## 🖼️ Your Magical Image")
            bytes_data = uploaded_file.read()
            with open("uploaded_image.jpg", "wb") as file:
                file.write(bytes_data)
            st.image(uploaded_file, use_column_width=True)

            # Generate story button
            if st.button("✨ Weave Your Story ✨"):
                with st.spinner("🪄 Crafting your magical tale..."):
                    try:
                        # Generate image caption
                        scenario = img2txt("uploaded_image.jpg")
                        if scenario:
                            st.session_state.caption = translate_text(
                                scenario, 
                                current_lang_code
                            )

                            # Generate story
                            prompt = f"""Based on the image description: '{scenario}', 
                            create a {preferences['genre']} story set in {preferences['setting']} 
                            in {preferences['region']}. The story should have a {preferences['tone']} 
                            tone and explore the theme of {preferences['theme']}. The main conflict 
                            should be {preferences['conflict']}. The story should have a {preferences['twist']} 
                            and end with a {preferences['ending']} ending."""
                            
                            story = txt2story(prompt)
                            if story:
                                # Store English version
                                st.session_state.story_english = story
                                
                                # Create translated version
                                st.session_state.story_translated = translate_text(
                                    story, 
                                    current_lang_code
                                )
                                
                                # Generate audio in the selected language
                                if create_audio(st.session_state.story_translated, current_lang_code):
                                    st.session_state.audio_file_path = "story_audio.mp3"
                                
                                st.session_state.processing_complete = True

                    except Exception as e:
                        st.error(f"✖️ An error occurred: {str(e)}")
                        st.warning("🔄 Please try again or contact support if the problem persists.")

        # Display results
        if st.session_state.processing_complete:
            st.markdown("---")
            
            # Display caption
            if st.session_state.caption:
                with st.expander("📜 The Vision", expanded=True):
                    st.markdown(
                        f"<div class='story-container'>{st.session_state.caption}</div>",
                        unsafe_allow_html=True
                    )
            
            # Display story
            if st.session_state.story_translated:
                with st.expander("📖 Your Tale Unfolds", expanded=True):
                    st.markdown(
                        f"<div class='story-container'>{st.session_state.story_translated}</div>",
                        unsafe_allow_html=True
                    )
            
            # Display audio player with correct language indication
            if st.session_state.audio_file_path and os.path.exists(st.session_state.audio_file_path):
                with st.expander(f"🎧 Listen to the Magic ({selected_language})", expanded=True):
                    st.audio(st.session_state.audio_file_path)

    # Footer
    st.markdown("""
        <div style='text-align: center; padding: 20px; margin-top: 50px;'>
            <p>🪔 Created with love for Indian storytelling 🪔</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()