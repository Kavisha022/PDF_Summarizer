import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import fitz  # PyMuPDF
from transformers import pipeline
import re

# Load summarizer model from HF
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Extract full text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    page_text = []
    for page in doc:
        page_text.append(page.get_text())
    return page_text

# Split text into paragraph based chunks
def split_into_paragraphs(text, max_chunk=1000):
    paragraphs = re.split(r'\n{2,}', text)
    chunks = []
    current_chunk = ""

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

# Summarize and update GUI in real-time
def summarize_text_live(page_text, output_widget):
    summary = ""
    output_widget.insert(tk.END, f"🔄 Summarizing {len(page_text)} pages...\n\n")
    output_widget.update()

    for i, single_page_text in enumerate(page_text):
        single_page_text = single_page_text.strip()
        if len(single_page_text) < 200:
            continue
        try:
            # Split the current page into chunks
            chunks = split_into_paragraphs(single_page_text)
            output_widget.insert(tk.END, f"⏳ Summarizing Page {i+1} with {len(chunks)} chunks...\n")
            output_widget.update()

            page_summary = ""
            for chunk in chunks:
                if len(chunk) < 200:  # Skip too short chunks
                    continue
                if len(chunk) > 1024:
                    chunk = chunk[:1024]

                summary_piece = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
                page_summary += summary_piece[0]['summary_text'] + "\n\n"

            summary += f"Page {i+1} Summary:\n{page_summary}\n\n"
            output_widget.insert(tk.END, f"📄 Summary of Page {i+1}:\n{page_summary}\n\n")
            output_widget.update()

        except Exception as e:
            output_widget.insert(tk.END, f"\n❌ Error on Page {i+1}: {e}\n")
            output_widget.update()
            messagebox.showerror("Error", str(e))

    output_widget.insert(tk.END, "\n✅ Done summarizing.")
    output_widget.update()

# File open and summarization trigger
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        try:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"📂 Opening: {file_path}\n\n")
            output_text.update()

            page_text = extract_text_from_pdf(file_path)
            summarize_text_live(page_text, output_text)
            
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

# GUI Setup with ttkbootstrap
root = ttk.Window(themename="cosmo")  # Try: "superhero", "journal", "darkly", etc.
root.title("Smart PDF Summarizer")
root.geometry("950x700")

# Button
open_button = tk.Button(root, text="Open PDF and Summarize", command=open_file, font=('Arial', 12, 'bold'), bg="#4CAF50", fg="white")
open_button.pack(pady=10)

# Output area
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=35, font=("Arial", 10))
output_text.pack(padx=10, pady=10)

# Tag formatting
output_text.tag_config("page", foreground="blue", font=("Arial", 10, "bold"))
output_text.tag_config("summary", foreground="black", font=("Arial", 10))
output_text.tag_config("error", foreground="red", font=("Arial", 10, "italic"))
output_text.tag_config("info", foreground="gray", font=("Arial", 10, "italic"))

root.mainloop()