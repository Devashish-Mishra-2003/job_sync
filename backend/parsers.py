import io, pdfplumber, docx, re, logging
logger = logging.getLogger(__name__)
def extract_text(file_obj):
    try:
        content = file_obj.read()
        fname = getattr(file_obj, "name", "")
        if hasattr(file_obj, "type") and file_obj.type == "text/plain":
            try: return content.decode('utf-8', errors='ignore')
            except: return str(content)
        if fname.lower().endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                pages=[p.extract_text() or "" for p in pdf.pages]
                return "\n".join(pages)
        if fname.lower().endswith(('.docx','.doc')):
            doc = docx.Document(io.BytesIO(content))
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        try: return content.decode('utf-8', errors='ignore')
        except: return str(content)
    except Exception:
        logger.exception("extract_text failed"); return ""
def normalize_text(text):
    text = text.replace("\r"," ").replace("\n"," ")
    text = re.sub(r'[^\w\s\-\+\.\/,]', ' ', text)
    return re.sub(r'\s+',' ', text).strip().lower()
