# 📚 Malicious Attachment Feature Extraction Toolkit

The repository contains all necessary feature extraction scripts needed to create a multi-format malicious attachment dataset.  
The project received support from the Canadian Institute for Cybersecurity (CIC) at the University of New Brunswick (UNB).  
The project aims to create a system which performs extensive feature-based evaluation of malicious and benign attachments within Word, Excel, PDF and HTML file formats.

---

## 🧩 Overview

Phishing and malware attacks now commonly use document attachments as their primary attack method.  
The scripts extract both static and content-based features from each file type to achieve three main objectives:
The system uses machine learning to detect malicious documents and performs cross-format feature comparison and generates research datasets for reproducibility.  

The repository contains four separate Jupyter notebooks which operate independently from each other.

| Notebook | Description |
|-----------|--------------|
The notebook **`Doc_Feature_Extraction.ipynb`** extracts features from Microsoft Word documents (`.doc`, `.docx`, `.docm`, `.dotm`) which include macro detection and embedded object analysis and metadata complexity assessment. |
The Excel_Feature_Extraction.ipynb notebook extracts features from Excel files (`.xls`, `.xlsx`, `.xlsm`) which include sheet organization and formula distribution and macro execution and content randomness. |
The PDF_Feature_Extraction.ipynb notebook performs object-based analysis of PDF files to detect embedded scripts and filters and metadata and compression patterns. |
The HTML_Feature_Extraction.ipynb notebook performs HTML web page analysis to extract structural elements and lexical patterns including tag distribution and script occurrence and suspicious word frequency. |

The notebooks generate CSV files which contain document-level feature vectors that can be used for ML classification tasks.

---

## ⚙️ Installation & Setup

### Requirements

The scripts operate under Python 3.9 and above versions and require Jupyter Notebook for execution.  
The scripts need to run in Google Colab or a virtual environment which includes these required packages:

```bash
pip install pandas numpy openpyxl xlrd olefile oletools PyMuPDF pdfminer.six fitz beautifulsoup4 lxml requests pillow pytesseract python-docx tqdm