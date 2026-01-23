import os
from openai import OpenAI
from dotenv import load_dotenv

# Load keys
load_dotenv()

class AudioManager:
    def __init__(self):
        self.client = OpenAI()

    def speech_to_text(self, audio_file_path):
        """
        Transcribes audio file to text using OpenAI Whisper.
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            return f"Error in STT: {str(e)}"

    def text_to_speech(self, text, output_filename="response.mp3", voice="alloy"):
        """
        Converts text to an MP3 file using OpenAI TTS.
        voice options: alloy, echo, fable, onyx, nova, shimmer
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                speed=1.30,
                input=text
            )
            # Save the file to the data folder for the UI to play
            output_path = os.path.join("data", output_filename)
            response.stream_to_file(output_path)
            return output_path
        except Exception as e:
            print(f"Error in TTS: {str(e)}")
            return None

# Quick test script
if __name__ == "__main__":
    manager = AudioManager()
    
    # Test TTS
    print("🔊 Testing Text-to-Speech...")
    path = manager.text_to_speech("Welcome to Sunmarke School. How can I help you today?")
    if path:
        print(f"✅ Success! Audio saved to: {path}")
    else:
        print("❌ TTS Failed.")