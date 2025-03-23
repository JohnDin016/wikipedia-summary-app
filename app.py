from flask import Flask, render_template, request, abort
import requests
import logging

app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)


def get_wikipedia_data(page_title, data_type):
    base_url = "https://en.wikipedia.org/w/api.php"

    if data_type in ["summary", "full"]:
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "redirects": True,
            "titles": page_title
        }
        if data_type == "summary":
            params["exintro"] = True  # Only the introduction for summary
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return {"error": "Error fetching data from Wikipedia."}
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        if "missing" in page:
            return {"error": "Page not found. Please check the title."}
        extract = page.get("extract")
        if not extract:
            return {"error": "No extract available for this page."}
        return {"content": extract}

    elif data_type == "image":
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "redirects": True,
            "titles": page_title,
            "piprop": "original"
        }
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return {"error": "Error fetching data from Wikipedia."}
        data = response.json()
        page = next(iter(data['query']['pages'].values()))
        if "missing" in page:
            return {"error": "Page not found. Please check the title."}
        image_info = page.get("original")
        if image_info and "source" in image_info:
            return {"content": image_info["source"]}
        else:
            return {"error": "No image available for this page."}

    else:
        return {"error": "Invalid data type selected."}


@app.route("/", methods=["GET", "HEAD", "POST"])
def home():
    result = None
    if request.method == "POST":
        page_title = request.form.get("page_title", "").strip()
        data_type = request.form.get("data_type", "summary")

        if not page_title:
            result = {"error": "Please enter a Wikipedia page title."}
        else:
            # Replace spaces with underscores for proper formatting
            formatted_title = page_title.replace(" ", "_")
            result = get_wikipedia_data(formatted_title, data_type)
            app.logger.info("Fetched data for '%s' with type '%s'", page_title, data_type)

    try:
        return render_template("index.html", result=result)
    except Exception as e:
        app.logger.error("Error rendering template: %s", e)
        abort(500)


if __name__ == "__main__":
    app.run(debug=True)