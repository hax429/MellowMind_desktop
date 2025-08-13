import pyaudio
import wave
import io
import re
import openai
from openai import OpenAI
import tempfile
import os
import numpy as np
import threading
import time

class CountdownGameWhisper:
    def __init__(self, openai_api_key=None):
        # Try to load API key from file, environment, or parameter
        api_key = openai_api_key
        if not api_key:
            try:
                with open('openai_key.txt', 'r') as f:
                    api_key = f.read().strip()
            except FileNotFoundError:
                api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please create 'openai_key.txt' file or set OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=api_key)
        self.current_number = 4000
        self.step = 7
        
        # Audio recording settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds = 3
        self.silence_threshold = 500  # Adjust based on environment
        
        self.audio = pyaudio.PyAudio()
        
    def play_loud_noise(self):
        def play_sound():
            # Generate a loud beep sound
            duration = 0.5  # seconds
            sample_rate = 44100
            frequency = 800  # Hz
            
            # Generate sine wave
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave_data = (np.sin(2 * np.pi * frequency * t) * 0.8 * 32767).astype(np.int16)
            
            # Play the sound
            stream = self.audio.open(format=pyaudio.paInt16,
                                   channels=1,
                                   rate=sample_rate,
                                   output=True)
            stream.write(wave_data.tobytes())
            stream.stop_stream()
            stream.close()
        
        # Play sound in separate thread so it doesn't block
        thread = threading.Thread(target=play_sound)
        thread.daemon = True
        thread.start()
        
    def record_audio(self):
        stream = self.audio.open(format=self.format,
                               channels=self.channels,
                               rate=self.rate,
                               input=True,
                               frames_per_buffer=self.chunk)
        
        print("Listening... (say your number clearly)")
        frames = []
        silent_chunks = 0
        max_silent_chunks = int(self.rate / self.chunk * 1.5)  # 1.5 seconds of silence
        
        # Record with voice activity detection
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
            
            # Check for silence to stop early
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.sqrt(np.mean(audio_data**2))
            
            if volume < self.silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0
            
            # Stop if we have enough audio and hit silence
            if i > int(self.rate / self.chunk * 0.5) and silent_chunks >= max_silent_chunks:
                break
        
        stream.stop_stream()
        stream.close()
        
        # Create temporary wav file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            wf = wave.open(temp_file.name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            return temp_file.name
    
    def transcribe_audio(self, audio_file_path):
        try:
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            os.unlink(audio_file_path)  # Clean up temp file
            return transcript.text
        except Exception as e:
            print(f"Transcription error: {e}")
            os.unlink(audio_file_path)  # Clean up temp file even on error
            return None
    
    def get_expected_number(self):
        return self.current_number - self.step
    
    def extract_number(self, text):
        text = text.lower().replace(',', '')
        
        # Handle written numbers
        word_to_digit = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
        }
        
        # Replace written numbers with digits
        for word, digit in word_to_digit.items():
            text = text.replace(word, digit)
        
        # First try to find 4-digit numbers (our target range)
        four_digit = re.findall(r'\b[123]\d{3}\b', text)
        if four_digit:
            return int(four_digit[-1])
        
        # Try to find any number in expected range
        numbers = re.findall(r'\b\d+\b', text)
        for num_str in reversed(numbers):
            num = int(num_str)
            if 2000 <= num <= 4500:
                return num
        
        # Extract all digits (including separated ones like "3, 9, 9, 3")
        all_digits = re.findall(r'\d', text)
        if len(all_digits) >= 4:
            # Try different combinations
            for i in range(len(all_digits) - 3):
                try:
                    combined = int(''.join(all_digits[i:i+4]))
                    if 2000 <= combined <= 4500:
                        return combined
                except ValueError:
                    continue
        
        # Try combining all digits
        if len(all_digits) >= 3:
            try:
                combined = int(''.join(all_digits))
                if 2000 <= combined <= 4500:
                    return combined
            except ValueError:
                pass
        
        return None
    
    def validate_response(self, spoken_number):
        expected = self.get_expected_number()
        if spoken_number == expected:
            self.current_number = expected
            return True
        return False
    
    def run_game(self):
        print("Ready! Starting countdown from 4000. Subtract 7 each time.")
        print(f"First number: {self.current_number}")
        print("Speak for 3 seconds when you hear 'Listening...'")
        
        while True:
            audio_file = self.record_audio()
            speech_text = self.transcribe_audio(audio_file)
            
            if speech_text is None:
                print("Could not transcribe audio. Try again.")
                continue
                
            print(f"You said: '{speech_text}'")
            
            spoken_number = self.extract_number(speech_text)
            
            if spoken_number is None:
                print("❌ No number detected in your speech. Please say a number.")
                self.play_loud_noise()
                continue
            
            expected = self.get_expected_number()
            
            if self.validate_response(spoken_number):
                print(f"✅ Correct! {spoken_number}")
                if self.current_number <= 0:
                    print("🎉 Countdown complete!")
                    break
            else:
                print(f"❌ Wrong! You said {spoken_number}, but the correct answer is {expected}")
                print(f"Current number stays at: {self.current_number}")
                self.play_loud_noise()
            
            print(f"Next number should be: {self.get_expected_number()}")
            print("-" * 40)
    
    def __del__(self):
        if hasattr(self, 'audio'):
            self.audio.terminate()

if __name__ == "__main__":
    # Create openai_key.txt file with your API key, or set OPENAI_API_KEY environment variable
    try:
        game = CountdownGameWhisper()
        game.run_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        if "API key not found" in str(e):
            print("\nTo fix this:")
            print("1. Create a file named 'openai_key.txt' and paste your OpenAI API key inside")
            print("2. Or set environment variable: export OPENAI_API_KEY=your_key_here")