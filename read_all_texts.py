import os, glob, pypdf

DOCS_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\processo_docs"

# 1. Read all txt files
txt_files = sorted(glob.glob(os.path.join(DOCS_DIR, "*.txt")))
for tf in txt_files:
    print(f"\n==========================================")
    print(f"FILE: {os.path.basename(tf)}")
    print(f"==========================================")
    with open(tf, "r", encoding="utf-8", errors="ignore") as f:
        print(f.read().strip())

# 2. Extract text from key PDFs
def extract_pdf_summary(pdf_path, max_pages=10):
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"\n==========================================")
    print(f"PDF: {os.path.basename(pdf_path)} (Total pages: {total_pages})")
    print(f"==========================================")
    text = ""
    for i in range(min(total_pages, max_pages)):
        page_text = reader.pages[i].extract_text() or ""
        text += f"\n--- Page {i+1} ---\n" + page_text
    return text

# Check 2145425 (Comentários do Gestor), 2145441, 2145435, 2145422
for pf in [
    "2145425_Formulrio - Comentrios do Gestor (2145425).pdf",
    "2145435_Correspondncia - Encerramento (2145435).pdf",
    "2145419_Termo de Solicitao de Informaes e Documentos n 03 (2145419).pdf"
]:
    full_p = glob.glob(os.path.join(DOCS_DIR, f"*{pf.split('_')[0]}*.pdf"))
    if full_p:
        txt = extract_pdf_summary(full_p[0], max_pages=5)
        print(txt[:2500])
