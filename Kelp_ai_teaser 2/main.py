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
    file_name = files[4] #"Kalyani Forge-OnePager.md"
    FILE_TO_READ = "data/private/" + file_name

    print("Loading private data...")
    private_data = load_private_data(FILE_TO_READ)
    with open(FILE_TO_READ, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("Extracting text from MD...")
    base_url = extract_website_from_md(md_text)

    print("Extracting Public Data...")
    public_data = scrape_public_data(base_url)

    print("Generating Text (JSON)...")
    slide_text = generate_slide_text(private_data,public_data)

    print("Checking anonymization...")
    slide_text = check_anonymization(slide_text)

    print("Creating PPT...")
    create_ppt(slide_text)

    print("Creating Citations...")
    create_citations(private_data, public_data)

    print("Completed")

if __name__ == "__main__":
    main()