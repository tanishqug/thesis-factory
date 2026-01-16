# Thesis Template Factory 🏭

A programmatic system to generate strict, compliance-ready thesis templates for multiple universities without manual formatting.

## 🚀 Quick Start in < 60 Seconds

### **Add a New University**
1. Open `data.json`.
2. Copy an existing JSON object (block between `{` and `}`).
3. Paste it at the end of the list (add a comma before it!).
4. Update these 3 fields:
   - `"id"`: Format as `UNI_NAME_COURSE`.
   - `"uni_name"`: The real name.
   - `"margins"`: Update `left`, `right`, `top`, `bottom` from the guideline PDF.
5. Save the file.
6. Run:
   ```bash
   ./venv/bin/python multi_factory.py
   ```
   *Your new folder will appear in `Output/` immediately.*

---

## 🏗 System Architecture

- **`data.json`**: Single Source of Truth. Contains all rules, margins, and orders.
- **`multi_factory.py`**: The "Factory" logic. No hardcoded universities.
- **`Output/`**: Generated artifacts (ready for GitHub/Gumroad).

## ⚠️ Requirements
- Python 3.8+
- `python-docx`

## 📦 Installation
```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install python-docx
```


## 🛠 Features
- **Style-Based Formatting**: No manual font hacks. Uses Word Styles (`Heading 1`, `Normal`) exclusively.
- **Dynamic Headers/TOC**: Includes placeholder fields for Table of Contents.
- **Mirror Margins Ready**: Configured for official binding binding rules (e.g., 1.5" left margin).
- **Scalable**: Currently supports **19 Universities** across US, UK, Canada, Australia, Germany, Finland, Ireland, India, and UAE.
  - **Notable Entries**: MIT, Harvard, Yale, Oxford, Cambridge, Stanford.
  - **Global Tech**: TUM (Germany), Aalto (Finland), IIT Bombay (India).
  - **Commonwealth**: Melbourne, UBC, Toronto, Trinity College Dublin.

---
*Built by Agentic Automation for High-Scale Deployment.*
