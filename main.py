import json
import speech_recognition as sr
import pyttsx3
from brain import get_response, get_session_review
from memory_manager import load_memory, save_memory, memory_to_prompt, add_session_summary
from modes import get_mode_prompt

# Voice setup
engine = pyttsx3.init()
engine.setProperty('rate', 170)
recognizer = sr.Recognizer()

def speak(text):
    print(f"\nDivan: {text}\n")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"You: {text}")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("(couldn't hear you)")
            return None
        except sr.RequestError:
            print("(speech service error)")
            return None

def run_jarvis():
    memory = load_memory()
    current_mode = "friend"
    conversation_history = []
    feedback_on = False
    voice_mode = True

    print("\n🤖 DIVAN V0.2 — Online (Voice Mode)")
    print("Type /text to switch to typing")
    print("Type /voice to switch back to voice")
    print("Commands: /mode [friend|client|interviewer|debate|pressure]")
    print("          /feedback on|off")
    print("          /quit\n")

    def build_system_prompt():
        mode_prompt = get_mode_prompt(current_mode)
        mem_prompt = memory_to_prompt(memory)
        return f"{mode_prompt}\n\n{mem_prompt}"

    conversation_history.append({
        "role": "system",
        "content": build_system_prompt()
    })

    while True:
        if voice_mode:
            user_input = listen()
            if user_input is None:
                continue
        else:
            user_input = input("You: ").strip()
            if not user_input:
                continue

        if user_input.startswith("/"):
            parts = user_input.split()
            cmd = parts[0]

            if cmd == "/quit":
                print("\n🔁 Running session review...")
                review_json = get_session_review(conversation_history)
                review = json.loads(review_json)
                print(f"\n📊 Session Score: {review.get('score')}/10")
                print(f"⚠️  Weakness: {review.get('weakness')}")
                print(f"✅ Adjustment: {review.get('adjustment')}")
                add_session_summary(memory, review)
                print("\n💾 Memory updated. Goodbye.\n")
                break

            elif cmd == "/mode" and len(parts) > 1:
                current_mode = parts[1]
                conversation_history = [{
                    "role": "system",
                    "content": build_system_prompt()
                }]
                print(f"🎭 Mode switched to: {current_mode}\n")

            elif cmd == "/feedback":
                feedback_on = len(parts) > 1 and parts[1] == "on"
                print(f"🔁 Feedback: {'ON' if feedback_on else 'OFF'}\n")

            elif cmd == "/text":
                voice_mode = False
                print("⌨️  Switched to text mode\n")

            elif cmd == "/voice":
                voice_mode = True
                print("🎤 Switched to voice mode\n")

            continue

        conversation_history.append({"role": "user", "content": user_input})
        response = get_response(conversation_history)
        conversation_history.append({"role": "assistant", "content": response})

        speak(response)

        if feedback_on:
            fb_history = conversation_history + [{
                "role": "user",
                "content": "In one sentence, give quick feedback on my last message only."
            }]
            feedback = get_response(fb_history)
            print(f"💬 Feedback: {feedback}\n")

if __name__ == "__main__":
    run_jarvis()

