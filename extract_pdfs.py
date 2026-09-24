import pypdf, sys, os

sys.stdout.reconfigure(encoding='utf-8')

DOCS_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\processo_docs"

def analyze_pdf(filename, max_p=30):
    path = os.path.join(DOCS_DIR, filename)
    reader = pypdf.PdfReader(path)
    print(f"=== {filename} (Pages: {len(reader.pages)}) ===")
    full_text = ""
    for idx, page in enumerate(reader.pages):
        t = page.extract_text() or ""
        full_text += f"\n--- Page {idx+1} ---\n" + t
    return full_text

import glob

def find_pdf_by_id(doc_id):
    files = glob.glob(os.path.join(DOCS_DIR, f"*{doc_id}*.pdf"))
    return files[0] if files else None

# Analyze 2145424
pdf_2145424 = find_pdf_by_id("2145424")
relatorio_text = analyze_pdf(os.path.basename(pdf_2145424))
with open(os.path.join(DOCS_DIR, "relatorio_preliminar_full.txt"), "w", encoding="utf-8") as f:
    f.write(relatorio_text)
print("Saved relatorio_preliminar_full.txt, total chars:", len(relatorio_text))

# Analyze 2145425
pdf_2145425 = find_pdf_by_id("2145425")
comentarios_text = analyze_pdf(os.path.basename(pdf_2145425))
with open(os.path.join(DOCS_DIR, "comentarios_gestor_form.txt"), "w", encoding="utf-8") as f:
    f.write(comentarios_text)
print("Saved comentarios_gestor_form.txt, total chars:", len(comentarios_text))

