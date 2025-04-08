import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import speech_recognition as sr
import pyttsx3
from RAG_Gmail import load_emails, ask_question

print("Starting application...")  # Debug print

class VoiceThread(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.daemon = True

    def run(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source)
                query = recognizer.recognize_google(audio)
                self.callback(query)
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand audio")
        except sr.RequestError:
            messagebox.showerror("Error", "Could not request results; check your internet connection")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

class GmailAssistantUI:
    def __init__(self, root):
        print("Initializing GmailAssistantUI...")  # Debug print
        self.root = root
        self.root.title("Gmail Assistant")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.messages = None
        self.new_conversation = True
        self.engine = pyttsx3.init()
        
        # Configure the grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create chat display
        self.chat_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Arial", 10))
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        # Create input area
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.input_field = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=4, font=("Arial", 10))
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Create button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky="ns")
        
        # Create buttons
        self.send_button = ttk.Button(button_frame, text="Send", command=self.send_message)
        self.send_button.pack(pady=2)
        
        self.voice_button = ttk.Button(button_frame, text="🎤 Voice Input", command=self.start_voice_input)
        self.voice_button.pack(pady=2)
        
        self.new_chat_button = ttk.Button(button_frame, text="New Chat", command=self.start_new_chat)
        self.new_chat_button.pack(pady=2)
        
        # Style the UI
        self.style_ui()
        
        # Load initial emails
        self.load_initial_emails()
        
        print("GmailAssistantUI initialized successfully")  # Debug print
        
        # Bind Enter key to send message
        self.input_field.bind("<Return>", lambda e: self.send_message())
    
    def style_ui(self):
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=6)
        
        # Configure colors
        self.chat_display.configure(bg="#2b2b2b", fg="white")
        self.input_field.configure(bg="#2b2b2b", fg="white")
    
    def load_initial_emails(self):
        try:
            print("Loading initial emails...")  # Debug print
            load_emails()
            self.chat_display.insert(tk.END, "System: Emails loaded successfully. You can start chatting!\n")
            print("Emails loaded successfully")  # Debug print
        except Exception as e:
            print(f"Error loading emails: {str(e)}")  # Debug print
            messagebox.showerror("Error", f"Failed to load emails: {str(e)}")
    
    def send_message(self):
        query = self.input_field.get("1.0", tk.END).strip()
        if not query:
            return
            
        self.chat_display.insert(tk.END, f"You: {query}\n")
        self.input_field.delete("1.0", tk.END)
        
        try:
            if self.new_conversation:
                self.messages, response = ask_question(query)
                self.new_conversation = False
            else:
                self.messages, response = ask_question(query, messages=self.messages)
            
            self.chat_display.insert(tk.END, f"Assistant: {response}\n")
            self.chat_display.see(tk.END)
            
            # Use a thread for text-to-speech to avoid blocking
            threading.Thread(target=self.speak_text, args=(response,), daemon=True).start()
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")  # Debug print
            messagebox.showerror("Error", f"Failed to process query: {str(e)}")
    
    def speak_text(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
    
    def start_voice_input(self):
        self.voice_button.configure(state="disabled")
        self.voice_button.configure(text="Listening...")
        
        def voice_callback(query):
            self.voice_button.configure(state="normal")
            self.voice_button.configure(text="🎤 Voice Input")
            self.input_field.delete("1.0", tk.END)
            self.input_field.insert("1.0", query)
            self.send_message()
        
        VoiceThread(voice_callback).start()
    
    def start_new_chat(self):
        self.new_conversation = True
        self.messages = None
        self.chat_display.delete("1.0", tk.END)
        self.load_initial_emails()

def main():
    print("Starting main function...")  # Debug print
    root = tk.Tk()
    print("Tk root created")  # Debug print
    app = GmailAssistantUI(root)
    print("Window created")  # Debug print
    root.mainloop()
    print("Window shown")  # Debug print

if __name__ == "__main__":
    print("Script started")  # Debug print
    main() 