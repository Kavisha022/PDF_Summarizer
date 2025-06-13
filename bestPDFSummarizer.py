import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Progressbar
import fitz  # PyMuPDF
from transformers import pipeline
import re
import threading

# Load summarizer model from Hugging Face
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return [page.get_text() for page in doc]

# Split large paragraphs
def split_into_paragraphs(text, max_chunk=1000):
    paragraphs = re.split(r'\n{2,}', text)
    chunks, current_chunk = [], ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) < max_chunk:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Summarize pages and update GUI
def summarize_text_live(page_text, output_widget, progress_bar):
    summary = ""
    total_pages = len(page_text)
    progress_step = 100 // max(1, total_pages)

    for i, text in enumerate(page_text):
        text = text.strip()
        if len(text) < 200:
            continue
        try:
            chunks = split_into_paragraphs(text)
            output_widget.insert(tk.END, f"⏳ Summarizing Page {i+1} with {len(chunks)} chunk(s)...\n")
            output_widget.update()

            page_summary = ""
            for chunk in chunks:
                if len(chunk) < 200:
                    continue
                if len(chunk) > 1024:
                    chunk = chunk[:1024]
                summary_piece = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
                page_summary += summary_piece[0]['summary_text'] + "\n\n"

            formatted = f"📄 **Summary of Page {i+1}:**\n{page_summary}\n{'-'*80}\n"
            summary += formatted
            output_widget.insert(tk.END, formatted)
            output_widget.update()
            progress_bar['value'] += progress_step

        except Exception as e:
            output_widget.insert(tk.END, f"❌ Error: {e}\n")
            output_widget.update()
            messagebox.showerror("Summarization Error", str(e))

    output_widget.insert(tk.END, "\n✅ Done summarizing!\n")
    output_widget.update()
    progress_bar['value'] = 100
    return summary

# Thread wrapper to keep GUI responsive
def run_summary(file_path):
    page_text = extract_text_from_pdf(file_path)
    summary = summarize_text_live(page_text, output_text, progress_bar)
    global last_summary
    last_summary = summary

# Open file dialog
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"📂 Opening: {file_path}\n\n")
        output_text.update()
        progress_bar['value'] = 0
        threading.Thread(target=run_summary, args=(file_path,)).start()

# Save summary
def save_summary():
    if not last_summary.strip():
        messagebox.showinfo("Nothing to Save", "There's no summary to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(last_summary)
        messagebox.showinfo("Saved", f"Summary saved to:\n{file_path}")

# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("🧠 Smart PDF Summarizer")
root.geometry("960x720")
root.config(bg="#f0f0f0")

open_button = tk.Button(root, text="📁 Open PDF and Summarize", command=open_file,
                        font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white", padx=20, pady=5)
open_button.pack(pady=10)

save_button = tk.Button(root, text="💾 Save Summary", command=save_summary,
                        font=('Arial', 12, 'bold'), bg="#2196F3", fg="white", padx=20, pady=5)
save_button.pack(pady=5)

progress_bar = Progressbar(root, orient=tk.HORIZONTAL, length=500, mode='determinate')
progress_bar.pack(pady=5)

output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=115, height=30, font=("Courier New", 10))
output_text.pack(padx=10, pady=10)

last_summary = ""  # To hold the final result for saving

root.mainloop()
