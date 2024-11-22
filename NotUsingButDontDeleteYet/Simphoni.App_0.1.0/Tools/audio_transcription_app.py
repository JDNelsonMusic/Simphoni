import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import wave
from pydub import AudioSegment
import whisper

# Function to split audio into chunks
def split_audio(file_path, chunk_duration=300000):  # 300000 ms = 5 minutes
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_duration):
        chunk = audio[i:i + chunk_duration]
        chunks.append(chunk)
    return chunks

# Function to save chunks to temporary files
def save_chunks(chunks, output_dir="temp_chunks"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    chunk_files = []
    for idx, chunk in enumerate(chunks):
        chunk_file = os.path.join(output_dir, f"chunk_{idx}.wav")
        chunk.export(chunk_file, format="wav")
        chunk_files.append(chunk_file)
    return chunk_files

# Function to transcribe audio using Whisper
def transcribe_audio(file_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        return result['text']
    except Exception as e:
        return f"Error transcribing file: {str(e)}"

# Main GUI Application
class AudioTranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcription App")
        self.root.geometry("800x1200")
        
        self.label = tk.Label(root, text="Upload an audio file for transcription:", font=("Arial", 14))
        self.label.pack(pady=10)
        
        self.upload_button = tk.Button(root, text="Upload Audio File", command=self.upload_file, font=("Arial", 12))
        self.upload_button.pack(pady=10)
        
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), width=80, height=25)
        self.text_area.pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.m4a *.flac")])
        if file_path:
            messagebox.showinfo("Processing", "Splitting audio and starting transcription. This might take some time...")
            self.transcribe_file(file_path)
    
    def transcribe_file(self, file_path):
        try:
            chunks = split_audio(file_path)
            chunk_files = save_chunks(chunks)
            
            transcription = ""
            for chunk_file in chunk_files:
                transcription += transcribe_audio(chunk_file) + "\n"
            
            # Clean up temporary files
            for chunk_file in chunk_files:
                os.remove(chunk_file)
            os.rmdir("temp_chunks")
            
            # Display transcription
            self.text_area.insert(tk.END, transcription)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriptionApp(root)
    root.mainloop()
