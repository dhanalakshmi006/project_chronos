import os
import json
import requests
from pathlib import Path

try:
    from google import genai
except ImportError:
    raise ImportError("Install google-genai (pip install google-genai)")

# --- Environment Variables ---
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

GOOGLE_CSE_KEY = os.environ.get("GOOGLE_CSE_KEY")
GOOGLE_CX = os.environ.get("GOOGLE_CX")

PROMPT_TEMPLATE ="""
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

def assemble_report(original, reconstructed, explanations, links):
    lines = []
    lines.append("--- RECONSTRUCTION REPORT ---")
    lines.append("[Original fragment]")
    lines.append(f"> {original}\n")
    lines.append("[AI-Reconstructed text]")
    lines.append(f"> {reconstructed}\n")
    if explanations:
        lines.append("[Explanations]")
        for e in explanations:
            lines.append(f"* {e}")
    lines.append("\n[Contextual sources]")
    for l in links:
        lines.append(f"* {l['link']} ({l['title']})")
    return "\n".join(lines)


def main():
    fragment = input("Enter the fragment you want me to reconstruct:\n> ")
    parsed = call_gemini(fragment)

    reconstructed = parsed.get("reconstruction", "")
    explanations = parsed.get("explanations", [])
    keywords = parsed.get("keywords", [])

    query = " ".join(keywords) if keywords else reconstructed
    links = google_custom_search(query)

    report = assemble_report(fragment, reconstructed, explanations, links)
    print("\n" + report)
    Path("report.txt").write_text(report, encoding="utf-8")
    print("\nSaved report.txt")

if __name__ == "__main__":
    main()
