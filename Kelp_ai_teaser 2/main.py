from scripts.load_private_data import load_private_data
from scripts.scrape import extract_website_from_md
from scripts.scrape import scrape_public_data
from scripts.generate_text import generate_slide_text
from scripts.anonymize import check_anonymization
from scripts.generate_ppt import create_ppt
from scripts.citations import create_citations


def main():
    files= ["Kalyani Forge-OnePager.md","Centum-OnePager.md","Connplex Cinemas-OnePager.md",
    "Gati-OnePager.md","Ind Swift-OnePager.md","Ksolves-OnePager.md"]
    file_name = files[4]
    FILE_TO_READ = "data/private/" + file_name

    print("Loading private data...")
    private_data = load_private_data(FILE_TO_READ) #Loads .md file and stores text in variable named 'priva
    
    with open(FILE_TO_READ, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("Extracting text from MD...")
    base_url = extract_website_from_md(md_text) # Takes URL from .md file

    print("Extracting Public Data...")
    public_data = scrape_public_data(base_url) #Uses the URL to extract data, all the while storing citations for source document.

    print("Generating Text (JSON)...")
    slide_text = generate_slide_text(private_data,public_data) #Feeds raw text into API, to convert into ppt-ready bullet points

    print("Checking anonymization...")
    slide_text = check_anonymization(slide_text) #Checks anonymization, with active text replacement

    print("Creating PPT...")
    create_ppt(slide_text) # Puts text into a placeholder PPT, along with charts and visuals

    print("Creating Citations...")
    create_citations(private_data, public_data) # makes the citation document

    print("Completed")

if __name__ == "__main__":
    main()
