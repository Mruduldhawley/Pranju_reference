import gradio as gr
import json
import requests
import re
import os
from urllib.parse import urlparse

def parse_and_modify_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

def remove_html_tags(text):
    return re.sub('<.*?>', '', text)

def reformulate_json(data):
    # Extract relevant information from the original data
    authors = [
        {"given": name["given"], "family": name["family"], "literal": None}
        for name in data["results"][0]["metadata"]["author"]
    ]
    editors = [{"given": name["given"], "family": name["family"], "literal": None} for name in data["results"][0]["metadata"]["editor"]]
    issued_date = data["results"][0]["metadata"]["issued"]
    doi = data['results'][0].get('metadata', {}).get('doi', None)
    container_title = data['results'][0].get("metadata", {}).get("containerTitle", None)
    publisher = data['results'][0].get("metadata", {}).get("containerTitle", None)
    title = data['results'][0].get("metadata", {}).get("title", None)
    url_d = data['results'][0].get("metadata", {}).get("url", None)

    # Create the reformulated dictionary
    reformulated_data = {
        "metadata": {
            "author": authors,
            "collectionEditor": [],
            "composer": [],
            "containerAuthor": [],
            "director": [],
            "editor": editors,
            "editorialDirector": [],
            "illustrator": [],
            "interviewer": [],
            "originalAuthor": [],
            "recipient": [],
            "reviewedAuthor": [],
            "translator": [],
            "accessed": {"year": None, "month": None, "day": None},
            "eventDate": {"year": None, "month": None, "day": None},
            "issued": issued_date,
            "originalDate": {"year": None, "month": None, "day": None},
            "submitted": {"year": None, "month": None, "day": None},
            "abstract": None,
            "annote": None,
            "archive": None,
            "archiveLocation": None,
            "archivePlace": None,
            "authority": None,
            "callNumber": None,
            "citationLabel": None,
            "citationNumber": None,
            "collectionTitle": None,
            "containerTitle": container_title,
            "containerTitleShort": None,
            "dimensions": None,
            "doi": doi,
            "event": None,
            "eventPlace": None,
            "firstReferenceNoteNumber": None,
            "genre": None,
            "isbn": None,
            "issn": None,
            "jurisdiction": None,
            "keyword": None,
            "locator": None,
            "medium": None,
            "note": None,
            "originalPublisher": None,
            "originalPublisherPlace": None,
            "originalTitle": None,
            "page": None,
            "pageFirst": None,
            "pmcid": None,
            "pmid": None,
            "publisher": publisher,
            "publisherPlace": None,
            "references": None,
            "reviewedTitle": None,
            "scale": None,
            "section": None,
            "source": None,
            "status": None,
            "title": title,
            "titleShort": None,
            "url": url_d,
            "version": None,
            "yearSuffix": None,
            "chapterNumber": None,
            "collectionNumber": None,
            "edition": None,
            "issue": None,
            "number": None,
            "numberOfPages": None,
            "numberOfVolumes": None,
            "volume": None,
            "rawStr": None,
        },
        "sourceId": "webpage",
        "styleId": "default-harvard"
    }

    return reformulated_data

def generate_harvard_references(urls):
    urls = urls.split()  # Split input into a list of URLs
    base_get_url = "https://www.mybib.com/api/autocite/search?q={}&sourceId=webpage"
    references = ["REFERENCES\n"]
    count = 1
    for url in urls:
        try:
            original_data = requests.get(base_get_url.format(parse_and_modify_url(url))).json()
            reformulated_json_data = reformulate_json(original_data)
            res = requests.post(
                url='https://www.mybib.com/api/autocite/reference',
                json=reformulated_json_data
            )
            formatted_reference = remove_html_tags(res.json().get("result", {}).get("formattedReferenceStr", ""))
            references.append(f"{count}. {formatted_reference}")
            count += 1
        except Exception as e:
            references.append(f"Error processing URL {url}: {str(e)}")

    return "\n".join(references)

# Gradio interface
def harvard_reference_app(input_text):
    return generate_harvard_references(input_text)

interface = gr.Interface(
    fn=harvard_reference_app,
    inputs=gr.Textbox(lines=2, placeholder="Enter URLs separated by spaces..."),
    outputs="text",
    title="Pranju❤️ Referencing Generator",
    description="Enter URLs to generate Harvard-style references."
)

interface.launch(server_name="0.0.0.0",server_port=int(os.environ.get("PORT", 8080)))
