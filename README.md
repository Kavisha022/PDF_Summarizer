🧠 **Project Title** : Smart PDF Summarizer
A Windows desktop application developed using Python and Tkinter, designed to automatically summarize PDF content using NLP. This tool helps students, researchers, and readers save time by generating quick summaries of long documents.


📌 **Key Features**
📁Load and read multi-page PDF files,
⚡Automatically summarize large text blocks using HuggingFace Transformers,
⏳Live progress tracking using a progress bar,
💾Option to save the summary as a .txt file,
🪟User-friendly GUI built using Tkinter.


🛠️ T**echnologies Used**
Component -	Library / Tool,
GUI - tkinter, ttkbootstrap (optional theme),
PDF Text Extraction - PyMuPDF (fitz),
Summarization Model	- transformers (DistilBART),
Machine Learning - torch,
Packaging - pyinstaller (to build .exe),
IDE - Visual Studio Code.


🔍 **How It Works**
User uploads a PDF using a file dialog.
The app reads each page's text via fitz (PyMuPDF).
Text is broken into manageable chunks (to handle HuggingFace model limits).
Each chunk is summarized using pipeline("summarization").
The summary is displayed live with progress tracking.
The full summary is saved optionally by the user.


🏗️ **Packaging with PyInstaller**
To make a standalone Windows .exe:
pyinstaller --onefile --windowed bestPDFSummarizer.py .
Output .exe will be in the dist/ folder.


▶️ **Usage Guide**
Run the application (python bestPDFSummarizer.py or double-click .exe),
Click 📁 "Open PDF and Summarize",
Wait while the summary is generated,
Click 💾 "Save Summary" to export it.