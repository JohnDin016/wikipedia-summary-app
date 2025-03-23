from flask import Flask, request, render_template
import requests

app = Flask(__name__)


def get_wikipedia_data(page_title, data_type):
    base_url = "https://en.wikipedia.org/w/api.php"

    if data_type in ["summary", "full"]:
        # Use extracts to get the text content
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "redirects": True,
            "titles": page_title
        }
        if data_type == "summary":
            # For summary, get only the introduction
            params["exintro"] = True
        # For full article, we simply omit exintro (or set it to False)

    elif data_type == "images":
        # Use pageimages to fetch the main image (if available)
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "redirects": True,
            "titles": page_title,
            "piprop": "original"
        }
    else:
        return {"error": "Invalid data type selected."}

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        return {"error": f"Error fetching data (status code {response.status_code})."}

    data = response.json()
    page = next(iter(data['query']['pages'].values()))

    if "missing" in page:
        return {"error": "Page not found. Please check the title and try again."}

    if data_type in ["summary", "full"]:
        extract = page.get('extract')
        if not extract:
            return {"error": "No extract available for this page."}
        return {"content": extract}

    elif data_type == "images":
        # Try to fetch the original image URL
        image_info = page.get("original")
        if image_info and "source" in image_info:
            return {"content": image_info["source"]}
        else:
            return {"error": "No image available for this page."}


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        page_title = request.form.get("page_title", "").strip()
        data_type = request.form.get("data_type", "summary")

        if not page_title:
            result = {"error": "Please enter a Wikipedia page title."}
        else:
            # Format title (replace spaces with underscores)
            formatted_title = page_title.replace(" ", "_")
            result = get_wikipedia_data(formatted_title, data_type)

    return render_template("index.html", result=result)

@app.route("/", methods=["GET", "HEAD"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)