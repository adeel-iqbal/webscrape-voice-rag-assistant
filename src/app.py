import os
import asyncio
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from llm_chain import SchoolAgent
from audio_utils import AudioManager

# Page Configuration
st.set_page_config(
    page_title="Sunmarke School AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    h1 {
        color: #1f4788;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .response-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f4788;
    }
    .model-label {
        font-weight: 700;
        color: #616de8;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .response-text {
        color: #2c3e50;
        line-height: 1.6;
    }
    .user-query {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
        color: #1a1a1a;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4788;
        color: white;
        font-weight: 600;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #163a6f;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = SchoolAgent()
if 'audio_manager' not in st.session_state:
    st.session_state.audio_manager = AudioManager()
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'responses' not in st.session_state:
    st.session_state.responses = None
if 'audio_path_openai' not in st.session_state:
    st.session_state.audio_path_openai = None
if 'audio_path_gemini' not in st.session_state:
    st.session_state.audio_path_gemini = None

# Header
st.markdown("# 🎓 Sunmarke School AI Assistant")
st.markdown('<p class="subtitle">Ask me anything about admissions, curriculum, fees, and more!</p>', unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🎤 Voice Input")
    
    # Voice recorder
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e74c3c",
        neutral_color="#1f4788",
        icon_size="3x",
        key="voice_recorder"
    )
    
    # Process audio if recorded
    if audio_bytes and audio_bytes != st.session_state.get('last_audio_bytes'):
        st.session_state.last_audio_bytes = audio_bytes
        
        with st.spinner("🎧 Transcribing your voice..."):
            # Save audio temporarily
            temp_audio_path = "data/temp_recording.wav"
            os.makedirs("data", exist_ok=True)
            with open(temp_audio_path, "wb") as f:
                f.write(audio_bytes)
            
            # Transcribe
            transcribed = st.session_state.audio_manager.speech_to_text(temp_audio_path)
            st.session_state.transcribed_text = transcribed
            
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        
        # Auto-process after transcription
        if st.session_state.transcribed_text and st.session_state.transcribed_text.strip():
            query = st.session_state.transcribed_text.strip()
            
            # Reset previous responses
            st.session_state.responses = None
            st.session_state.audio_path_openai = None
            st.session_state.audio_path_gemini = None
            
            with st.spinner("🧠 Consulting AI models..."):
                # Get responses from both LLMs
                async def get_responses():
                    return await st.session_state.agent.ask(query)
                
                responses = asyncio.run(get_responses())
                st.session_state.responses = responses
                
                # Generate TTS for BOTH responses
                with st.spinner("🔊 Generating voice responses..."):
                    for response in responses:
                        if "OpenAI" in response['name']:
                            audio_path = st.session_state.audio_manager.text_to_speech(
                                response['answer'],
                                "openai_response.mp3",
                                voice="alloy"
                            )
                            st.session_state.audio_path_openai = audio_path
                        elif "Gemini" in response['name']:
                            audio_path = st.session_state.audio_manager.text_to_speech(
                                response['answer'],
                                "gemini_response.mp3",
                                voice="nova"
                            )
                            st.session_state.audio_path_gemini = audio_path
    
    st.markdown("---")
    st.markdown("### ✍️ Or Type Your Question")
    text_input = st.text_area(
        "Type here...",
        value=st.session_state.transcribed_text,
        height=100,
        key="text_query",
        placeholder="e.g., What are the school fees for Year 1?"
    )
    
    # Submit button
    if st.button("🚀 Get Answers", type="primary"):
        query = text_input.strip()
        
        if query:
            st.session_state.transcribed_text = query
            
            # Reset previous responses
            st.session_state.responses = None
            st.session_state.audio_path_openai = None
            st.session_state.audio_path_gemini = None
            
            with st.spinner("🧠 Consulting AI models..."):
                # Get responses from both LLMs
                async def get_responses():
                    return await st.session_state.agent.ask(query)
                
                responses = asyncio.run(get_responses())
                st.session_state.responses = responses
                
                # Generate TTS for BOTH responses
                with st.spinner("🔊 Generating voice responses..."):
                    for response in responses:
                        if "OpenAI" in response['name']:
                            audio_path = st.session_state.audio_manager.text_to_speech(
                                response['answer'],
                                "openai_response.mp3",
                                voice="alloy"
                            )
                            st.session_state.audio_path_openai = audio_path
                        elif "Gemini" in response['name']:
                            audio_path = st.session_state.audio_manager.text_to_speech(
                                response['answer'],
                                "gemini_response.mp3",
                                voice="nova"
                            )
                            st.session_state.audio_path_gemini = audio_path
        else:
            st.warning("⚠️ Please record a voice message or type a question first.")

with col2:
    st.markdown("### 💬 Response")
    
    # Display user query
    if st.session_state.transcribed_text:
        st.markdown(f"""
        <div class="user-query">
            <strong>Your Question:</strong><br>
            {st.session_state.transcribed_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Display responses
    if st.session_state.responses:
        # Create two columns for side-by-side responses
        resp_col1, resp_col2 = st.columns(2)
        
        for idx, response in enumerate(st.session_state.responses):
            target_col = resp_col1 if idx == 0 else resp_col2
            
            with target_col:
                st.markdown(f"""
                <div class="model-label">{response['name']}</div>
                """, unsafe_allow_html=True)
                
                # Stream the text response using Streamlit's built-in streaming
                def stream_data():
                    # If we have chunks from LLM streaming, use them
                    if 'chunks' in response and response['chunks']:
                        for chunk in response['chunks']:
                            yield chunk
                    else:
                        # Fallback: stream word by word
                        for word in response['answer'].split():
                            yield word + " "
                
                st.write_stream(stream_data)
                
                # Add audio player for each model - NO AUTOPLAY
                st.markdown("---")
                st.markdown("**🔊 Listen to Response:**")
                
                if "OpenAI" in response['name'] and st.session_state.audio_path_openai:
                    if os.path.exists(st.session_state.audio_path_openai):
                        with open(st.session_state.audio_path_openai, "rb") as audio_file:
                            audio_bytes_play = audio_file.read()
                            st.audio(audio_bytes_play, format="audio/mp3")
                
                elif "Gemini" in response['name'] and st.session_state.audio_path_gemini:
                    if os.path.exists(st.session_state.audio_path_gemini):
                        with open(st.session_state.audio_path_gemini, "rb") as audio_file:
                            audio_bytes_play = audio_file.read()
                            st.audio(audio_bytes_play, format="audio/mp3")
    else:
        st.info("👋 Ask a question using voice or text to get started!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>Powered by OpenAI GPT-4o & Google Gemini | Voice by OpenAI Whisper & TTS</small>
</div>
""", unsafe_allow_html=True)