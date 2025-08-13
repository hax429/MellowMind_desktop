import speech_recognition as sr
import re
import time

class CountdownGame:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = False
        self.microphone = sr.Microphone()
        self.current_number = 4000
        self.step = 7
        self.microphone_calibrated = False
        
    def setup_microphone(self):
        if not self.microphone_calibrated:
            with self.microphone as source:
                print("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.microphone_calibrated = True
        print("Ready! Starting countdown from 4000. Subtract 7 each time.")
        print(f"First number: {self.current_number}")
    
    def get_expected_number(self):
        return self.current_number - self.step
    
    def listen_for_speech(self):
        with self.microphone as source:
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=2)
                speech_text = self.recognizer.recognize_google(audio)
                return speech_text
            except sr.WaitTimeoutError:
                print("No speech detected within timeout.")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None
    
    def extract_number(self, text):
        numbers = re.findall(r'\b\d+\b', text)
        if numbers:
            return int(numbers[0])
        return None
    
    def validate_response(self, spoken_number):
        expected = self.get_expected_number()
        if spoken_number == expected:
            self.current_number = expected
            return True
        return False
    
    def run_game(self):
        self.setup_microphone()
        
        while True:
            speech = self.listen_for_speech()
            
            if speech is None:
                continue
                
            print(f"You said: '{speech}'")
            
            spoken_number = self.extract_number(speech)
            
            if spoken_number is None:
                print("❌ No number detected in your speech. Please say a number.")
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
            
            print(f"Next number should be: {self.get_expected_number()}")
            print("-" * 40)

if __name__ == "__main__":
    game = CountdownGame()
    try:
        game.run_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")