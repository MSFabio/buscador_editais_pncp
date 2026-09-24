import re, os

DOCS_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\processo_docs"

with open(os.path.join(DOCS_DIR, "relatorio_preliminar_full.txt"), "r", encoding="utf-8") as f:
    text = f.read()

print("Length of text:", len(text))

# Let's search for Achados, Sumário, Conclusão, Recomendações
lines = text.split("\n")
print("\n--- TABLE OF CONTENTS / HEADINGS ---")
for line in lines:
    if any(k in line.lower() for k in ["sumário", "1.", "2.", "3.", "4.", "5.", "6.", "achado", "conclusão", "recomendaç"]):
        if len(line.strip()) < 80 and len(line.strip()) > 3:
            print(line.strip())
