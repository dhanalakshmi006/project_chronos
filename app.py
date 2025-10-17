from flask import Flask, render_template, request
import os
import json
import requests

try:
    from google import genai
except ImportError:
    raise ImportError("Install google-genai (pip install google-genai)")

app = Flask(__name__)

# Environment variables
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_CSE_KEY = os.environ.get("GOOGLE_CSE_KEY")
GOOGLE_CX = os.environ.get("GOOGLE_CX")

# Prompt to get the reconstructed text, explanation and the key words.
PROMPT_TEMPLATE = """
Imagine that you are an AI Archeologist. You will be provided with an incomplete fragment, written in obscure slang, or filled with cultural references that are no longer understood. 

Your task:
1. Reconstruct it into a clearer, modern English sentence.
2. Give short explanations for any slang, abbreviation, or cultural reference you used while reconstructing it.
3. Suggest 5-7 relevant web search keywords or phrases that could help me in finding historical or cultural context about it.

Respond only with a valid JSON object in this format:
{
  "reconstruction": "string",
  "explanations": ["string", "string", ...],
  "keywords": ["string", "string", ...]
}

Example:
Fragment: "smh at the top 8 drama. ppl need to chill. g2g, ttyl."

Output:
{
  "reconstruction": "Shaking my head at the drama surrounding the 'Top 8' friends list on MySpace. People need to relax. I have to go; talk to you later.",
  "explanations": ["smh = shaking my head", "top 8 = MySpace feature", "ppl = people", "g2g = got to go", "ttyl = talk to you later"],
  "keywords": ["MySpace", "Top 8 drama", "early social media slang", "2000s internet culture"]
}

Fragment: "{fragment}"
"""

def call_gemini(fragment: str):
    client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else genai.Client()
    prompt = PROMPT_TEMPLATE.replace("{fragment}", fragment)
    resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    text = getattr(resp, "text", str(resp))

    # Safe JSON parse
    try:
        parsed = json.loads(text)
    except Exception:
        import re
        m = re.search(r'\{[\s\S]*\}', text)
        parsed = json.loads(m.group(0)) if m else {
            "reconstruction": text.strip(),
            "explanations": [],
            "keywords": []
        }
    return parsed


def google_custom_search(query: str, num=5):
    if not GOOGLE_CSE_KEY or not GOOGLE_CX:
        return []
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_CSE_KEY, "cx": GOOGLE_CX, "q": query, "num": num}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    items = r.json().get("items", [])
    return [{"title": it.get("title"), "link": it.get("link")} for it in items]


@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    if request.method == "POST":
        fragment = request.form.get("fragment")
        parsed = call_gemini(fragment)
        reconstructed = parsed.get("reconstruction", "")
        explanations = parsed.get("explanations", [])
        keywords = parsed.get("keywords", [])

        # Use Gemini’s keywords for better search relevance
        query = " ".join(keywords) if keywords else reconstructed
        links = google_custom_search(query)

        report = {
            "original": fragment,
            "reconstructed": reconstructed,
            "explanations": explanations,
            "links": links
        }

    return render_template("index.html", report=report)


if __name__ == "__main__":
    app.run(debug=True)
