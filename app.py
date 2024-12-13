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

def reformulate_json(data, style):
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
            "abstract": data['results'][0].get("metadata", {}).get("abstract", None),
            "annote": data['results'][0].get("metadata", {}).get("annote", None),
            "archive": data['results'][0].get("metadata", {}).get("archive", None),
            "archiveLocation": data['results'][0].get("metadata", {}).get("archiveLocation", None),
            "archivePlace": data['results'][0].get("metadata", {}).get("archivePlace", None),
            "authority": data['results'][0].get("metadata", {}).get("authority", None),
            "callNumber": data['results'][0].get("metadata", {}).get("callNumber", None),
            "citationLabel": data['results'][0].get("metadata", {}).get("citationLabel", None),
            "citationNumber": data['results'][0].get("metadata", {}).get("citationNumber", None),
            "collectionTitle": data['results'][0].get("metadata", {}).get("collectionTitle", None),
            "containerTitle": container_title,
            "containerTitleShort": data['results'][0].get("metadata", {}).get("containerTitleShort", None),
            "dimensions": data['results'][0].get("metadata", {}).get("dimensions", None),
            "doi": doi,
            "event": data['results'][0].get("metadata", {}).get("event", None),
            "eventPlace": data['results'][0].get("metadata", {}).get("eventPlace", None),
            "firstReferenceNoteNumber": data['results'][0].get("metadata", {}).get("firstReferenceNoteNumber", None),
            "genre": data['results'][0].get("metadata", {}).get("genre", None),
            "isbn": data['results'][0].get("metadata", {}).get("isbn", None),
            "issn": data['results'][0].get("metadata", {}).get("issn", None),
            "jurisdiction": data['results'][0].get("metadata", {}).get("jurisdiction", None),
            "keyword": data['results'][0].get("metadata", {}).get("keyword", None),
            "locator": data['results'][0].get("metadata", {}).get("locator", None),
            "medium": data['results'][0].get("metadata", {}).get("medium", None),
            "note": data['results'][0].get("metadata", {}).get("note", None),
            "originalPublisher": data['results'][0].get("metadata", {}).get("originalPublisher", None),
            "originalPublisherPlace": data['results'][0].get("metadata", {}).get("originalPublisherPlace", None),
            "originalTitle": data['results'][0].get("metadata", {}).get("originalTitle", None),
            "page": data['results'][0].get("metadata", {}).get("page", None),
            "pageFirst": data['results'][0].get("metadata", {}).get("pageFirst", None),
            "pmcid": data['results'][0].get("metadata", {}).get("pmcid", None),
            "pmid": data['results'][0].get("metadata", {}).get("pmid", None),
            "publisher": publisher,
            "publisherPlace": data['results'][0].get("metadata", {}).get("publisherPlace", None),
            "references": data['results'][0].get("metadata", {}).get("references", None),
            "reviewedTitle": data['results'][0].get("metadata", {}).get("reviewedTitle", None),
            "scale": data['results'][0].get("metadata", {}).get("scale", None),
            "section": data['results'][0].get("metadata", {}).get("section", None),
            "source": data['results'][0].get("metadata", {}).get("source", None),
            "status": data['results'][0].get("metadata", {}).get("status", None),
            "title": title,
            "titleShort": data['results'][0].get("metadata", {}).get("titleShort", None),
            "url": url_d,
            "version": data['results'][0].get("metadata", {}).get("version", None),
            "yearSuffix": data['results'][0].get("metadata", {}).get("yearSuffix", None),
            "chapterNumber": data['results'][0].get("metadata", {}).get("chapterNumber", None),
            "collectionNumber": data['results'][0].get("metadata", {}).get("collectionNumber", None),
            "edition": data['results'][0].get("metadata", {}).get("edition", None),
            "issue": data['results'][0].get("metadata", {}).get("issue", None),
            "number": data['results'][0].get("metadata", {}).get("number", None),
            "numberOfPages": data['results'][0].get("metadata", {}).get("numberOfPages", None),
            "numberOfVolumes": data['results'][0].get("metadata", {}).get("numberOfVolumes", None),
            "volume": data['results'][0].get("metadata", {}).get("volume", None),
            "rawStr": data['results'][0].get("metadata", {}).get("rawStr", None),
        },
        "sourceId": "article_journal",
        "styleId": style
    }

    return reformulated_data

def generate_references(urls,style, in_text):
    urls = urls.split()  # Split input into a list of URLs
    base_get_url = "https://www.mybib.com/api/autocite/search?q={}&sourceId=webpage"
    references = ["REFERENCES<hr>"]
    count = 1
    for url in urls:
        try:
            original_data = requests.get(base_get_url.format(parse_and_modify_url(url))).json()
            reformulated_json_data = reformulate_json(original_data, style)
            res = requests.post(
                url='https://www.mybib.com/api/autocite/reference',
                json=reformulated_json_data
            )
            formatted_reference = res.json().get("result", {}).get("formattedReferenceStr", "")
            if in_text:
              in_text = res.json().get("result", {}).get("formattedInTextCitationStr", "")
              references.append(f"{count}. {formatted_reference} <br> in-text : {in_text}")
            else:
              references.append(f"{count}. {formatted_reference}")
            count += 1
        except Exception as e:
            references.append(f"Error processing URL {url}: {str(e)}")

    return "<br>".join(references)

# Gradio interface
# def harvard_reference_app(input_text):
#     return generate_harvard_references(input_text)

# interface = gr.Interface(
#     fn=harvard_reference_app,
#     inputs=gr.Textbox(lines=2, placeholder="Enter URLs separated by spaces..."),
#     outputs="text",
#     title="Pranju❤️ Referencing Generator",
#     description="Enter URLs to generate Harvard-style references."
# )

# interface.launch(server_name="0.0.0.0",server_port=int(os.environ.get("PORT", 8080)))


def citation_app(input_text, style, in_text):
    return generate_references(input_text, style, in_text)
    
interface = gr.Interface(
    fn=citation_app,
    inputs=[
        gr.Textbox(lines=2, placeholder="Enter URLs separated by spaces...", label="URLs"),
        gr.Dropdown(
            ["default-apa", "apa-7th-edition", "default-chicago", "default-harvard", "harvard-australia", "modern-language-association-8th-edition", "default-mla"],
            label="Citation Style",
            value="default-harvard",  # Default value
            info="Select a citation style for your references."
        ),
        gr.Checkbox(label="In-Text", info="To Apply In-Text Cite"),
    ],
    outputs=gr.HTML(),
    title="Pranju❤️ Referencing Generator",
    description="Enter URLs to generate citations in the selected style."
)
# interface.launch()
interface.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8080)))
