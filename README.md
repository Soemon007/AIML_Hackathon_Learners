# AIML_Hackathon_Learners

# Automated Investment Teaser Generator (Kelp AI Hackathon)
By Learners:
Rehan Mallik
Vedant Iyengar

## Overview

This project automatically generates anonymized investment teaser decks(PowerPoint) and a citation document from a mix of private company data and public information.

The system is designed to mirror how an investment banking / M&A analyst would create a teaser, but in a fully automated, reproducible pipeline.

Output:

* Editable PowerPoint teaser (`.pptx`)
* Source & citation document (`.docx`)

---

## Key Features

* End-to-end automation (one command run)
* Native, editable PowerPoint slides (no images of text)
* Financial charts generated programmatically
* Sector-relevant, anonymized visuals
* Soft Anonymization check
* Citation tracking for all major claims

---

## Project Structure

```
├── main.py                     # End-to-end pipeline
├── scripts/
│   ├── load_private_data.py    # Reads provided private files
│   ├── scrape.py               # Collects public information
│   ├── generate_text.py        # Generates slide-level content
│   ├── anonymize.py            # Leakage detection & replacement
│   ├── generate_ppt.py         # PowerPoint generation logic
│   └── citations.py            # Citation document generation
├── assets/
│   └── images                 # Downloaded, anonymized images
│   └── icons
├── output/
│   ├── company_teaser.pptx     # Final teaser deck
│   └── company_citations.docx  # Citation & sources document
└── README.md
```

---

## How It Works (Pipeline)

1. Load Private Data
   Reads financials and company-provided information (Markdown).

2. Collect Public Data
   Scrapes publicly available information using requests / BeautifulSoup (or APIs where available).

3. Generate Slide Content
   Converts raw data into investment-style language (titles, bullets, metrics).

4. Anonymization Check
   Automatically scans for forbidden terms (company names, locations, identifiers).

5. PowerPoint Generation
   Creates a 5-slide teaser with:

   * Business/Brand overview
   * Financial snapshot (with charts)
   * Investment Highlights

6. Citation Generation
   Produces a separate document mapping claims → sources.

---

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Then run this:

```bash
python -m spacy download en_core_web_lg
```

### 2. Run the Full Pipeline

```bash
python main.py
```

### 3. Outputs

After a successful run, you will find:

```
output/
├── company_teaser.pptx
└── company_citations.docx
```

Both files are fully editable.

---

## Anonymization Philosophy

The system is intentionally conservative.

The following are **not allowed** in outputs:

* Company names
* Cities / countries
* Customer names
* Exact plant locations
* Market rankings tied to geography

Instead, the system uses neutral investment language such as:

* "Domestic market"
* "International customers"
* "Multiple strategic locations"

If any forbidden term is detected, the script replaces the word with a suitable hard-coded replacement.

---

## Design Decisions

* Native PPT elements only (text boxes, charts)
* No screenshots or static images of text
* Minimalist layout to mirror real M&A teasers

---

## Limitations

* Visual design is intentionally conservative and limited
* Financial assumptions are only as accurate as provided data

---

## Future Improvements

* LLM-assisted language refinement to existing text
* Template-based slide theming

---

## Team Notes

This project was built under tight time constraints to demonstrate:

* Automation-first thinking
* Real-world financial deliverable generation

It prioritizes **correctness, safety, and clarity** over flashy visuals.

---

## License

This project is intended for hackathon evaluation only, and may be used for further purposes under the MIT license
