from flask import Flask, request, render_template
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

#CONFIGURATION
app = Flask(__name__)

load_dotenv()



#HELPERS


def extract_text_from_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    
    except Exception as e:
        return f"<Unreadable PDF content>"







def langchain_llm(content, api_key):
    if not api_key:
        return None

    # tell SDK what key to use
    os.environ["GOOGLE_API_KEY"] = api_key  

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.9,
        max_output_tokens=2048,
    )

    prompt_document_analysis = PromptTemplate.from_template("""
    You are a tax assistant. The following is a tax form. Your goal is to point out any issues.

    Tax Document:
    "{input_text}"

    Your response:
    """)

    chain = LLMChain(llm=llm, prompt=prompt_document_analysis)
    result = chain.run(input_text=content)
    return result








#ROUTES




@app.route('/upload', methods=['GET', 'POST'])
def document_upload():
    if request.method=="POST":
        uploaded_file = request.files['pdfFile']
        api_key = request.form.get('apiKey')

        
        if api_key:
            key_to_use = api_key
        else:
            key_to_use = os.getenv("GOOGLE_API_KEY")

        if not key_to_use:
            return "<p>API key is required.</p>"
        
        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            content = extract_text_from_pdf(uploaded_file)
            result = langchain_llm(content, key_to_use)
            print (result)
            return render_template('document.html', llm_response=f"<h2>Analysis:</h2><pre>{result}</pre>", document_contents=f"<h2>File Contents:</h2><pre>{content}</pre>")
        return "<p>Please upload a valid PDF file.</p>"
    return render_template('document.html', llm_response=None, document_contents=None)



@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
