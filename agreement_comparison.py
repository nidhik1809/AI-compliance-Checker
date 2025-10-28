from google import genai
from google.genai import types
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from enum import Enum
import PyPDF2
import json
from groq import Groq

load_dotenv()

def document_type(file):
    
    class DocumentType(str, Enum):
        DPA= "Data Processing Agreement"
        JCA= "Joint Controller Agreement"
        C2C= "Controller-to-Controller Agreement"
        subprocessor= "Processor-to-Subprocessor Agreement"
        SCC= "Standard Contractual Clauses"
        NoOne="NoOne"
    
    class FindDocumentType(BaseModel):
        document_type: DocumentType
        
        
    text=""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
            
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_2"))
    # print(os.getenv("GEMINI_API_KEY"))
    prompt=f"""
        Tell me what type of document is this
        
        document should be type of between 
        
        1. Data Processing Agreement
        2. Joint Controller Agreement
        3. Controller-to-Controller Agreement
        4. Processor-to-Subprocessor Agreement
        5. Standard Contractual Clauses
        
        Input: {text}
        
        Response in this JSON Structure:
        [{{
            "document_type": "<type_of_document>"
        }},
        ]

    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
                response_schema=list[FindDocumentType],
            ),
        )
        json_object = json.loads(response.text)
        
    except Exception as e:
        # Fallback: call Groq if Gemini fails
        print("Gemini error:", e, "-- Switching to Groq AI")
        try:
            groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            groq_response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",  # Updated model name
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            groq_content = groq_response.choices[0].message.content
            json_object = json.loads(groq_content)
        except Exception as groq_error:
            print("Groq also failed:", groq_error)
            # Final fallback
            return "NoOne"
    
    return json_object[0]['document_type']


def compare_agreements(unseen_data, template_data):
    """Compares an unseen agreement with a template and provides a risk analysis."""
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an AI legal assistant specialized in GDPR compliance review.
    
    Compare the "New contract document" against the "Template document". Both documents contain the full text of their clauses.
    
    Template document (regulatory standard reference):
    {template_data}
    
    New contract document to review:
    {unseen_data}
    
    ### Tasks:
    1.  **Identify Missing Clauses**: List any clauses present in the template but missing from the new contract.
    2.  **Identify Altered Clauses**: List clauses that are present in both but have significant wording differences that could alter the legal meaning.
    3.  **Flag Compliance Risks**: Based on the differences, flag potential risks related to GDPR.
    4.  **Assign Risk Score**: Provide a risk score from 0 (no risk) to 100 (maximum risk).
    5.  **Reasoning**: Briefly explain the score based on the severity of the identified risks.
    6.  **Recommendations**: Suggest specific, actionable amendments to align the new contract with the template.
    
    ### Required Output Format:
    Provide the response in a concise, structured format.

    - **Missing Clauses**:
    - **Altered Clauses**:
    - **Potential Compliance Risks**:
    - **Risk Score (0-100)**:
    - **Reasoning**:
    - **Recommendations**:
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    print("\n--- Compliance Analysis Report ---")
    print(response.text)
    print("----------------------------------\n")
    return response.text