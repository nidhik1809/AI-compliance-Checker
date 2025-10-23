from google import genai
from google.genai import types
from pydantic import BaseModel
import json
import PyPDF2
import os
from dotenv import load_dotenv

load_dotenv()

def clause_extraction(file_path, output_file=None):
    """Extracts all clauses with their full text from a PDF using Gemini."""
    print("--- Starting Full Clause Extraction ---")

    class Clause(BaseModel):
        clause_id: str
        heading_title: str
        full_text: str

    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    client = genai.Client(api_key=os.getenv("GEMINI_API_PRO_KEY"))

    prompt = f"""
You are an expert in legal contract analysis. Your task is to extract all clauses from the following contract text.

### Guidelines:
- A clause may begin with a number/letter (e.g., "1.", "A."), the word "Clause" (e.g., "Clause 1"), or an ALL CAPS heading (e.g., "DEFINITIONS").
- Each extracted clause must include:
  - "clause_id": The exact numbering/label from the contract (e.g., "1.", "A.", "Clause 1", "EXHIBIT A").
  - "heading_title": Use the explicit heading if present; if not, use the first few words of the clause as a title.
  - "full_text": The complete, verbatim text of the clause, including all sub-clauses.
- Maintain precise clause boundaries. Do not merge multiple clauses.
- Include clauses from exhibits, appendices, and annexes.
- Do not omit any content unless it is clearly non-contractual (e.g., page numbers, headers, footers).
- Respond in valid JSON only (no explanations or extra text).

Input: {text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    print("--- Full Clause Extraction Complete ---")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json.loads(response.text), f, indent=4, ensure_ascii=False)
        print(f"✅ Clauses extracted and saved to {output_file}")

    return response.text

if __name__ == "__main__":
    # For SCC extraction
    clause_extraction("templates/Standard-Contractual-Clauses-SCCs.pdf", "templates/scc.json")
    print("Full-text template generation complete.")
