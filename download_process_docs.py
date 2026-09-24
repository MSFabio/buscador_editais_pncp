import json, os, time, re, websocket, requests
from bs4 import BeautifulSoup
import pypdf

DOCS_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\processo_docs"
os.makedirs(DOCS_DIR, exist_ok=True)

with open(r"C:\Users\11429149760\AppData\Local\Google\Chrome\User Data\DevToolsActivePort", "r") as f:
    port = f.readline().strip()
    browser_path = f.readline().strip()

ws = websocket.create_connection(f"ws://127.0.0.1:{port}{browser_path}", suppress_origin=True)
ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
res = json.loads(ws.recv())
target_id = [t["targetId"] for t in res["result"]["targetInfos"] if "002323" in t.get("title","")][0]
ws.send(json.dumps({"id": 2, "method": "Target.attachToTarget", "params": {"targetId": target_id, "flatten": True}}))

session_id = None
while True:
    msg = json.loads(ws.recv())
    if msg.get("method") == "Target.attachedToTarget":
        session_id = msg["params"]["sessionId"]
        break

# Get cookies
ws.send(json.dumps({"id": 3, "sessionId": session_id, "method": "Network.getCookies"}))
cookies = {}
while True:
    msg = json.loads(ws.recv())
    if msg.get("id") == 3:
        for c in msg["result"]["cookies"]:
            if "def.br" in c.get("domain", ""):
                cookies[c["name"]] = c["value"]
        break

sess = requests.Session()
sess.cookies.update(cookies)
sess.headers.update({"User-Agent": "Mozilla/5.0"})

req_id = 200
def eval_js(expr):
    global req_id
    req_id += 1
    cur_id = req_id
    ws.send(json.dumps({
        "id": cur_id,
        "sessionId": session_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True
        }
    }))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == cur_id:
            return msg.get("result", {}).get("result", {}).get("value")

# Key documents to extract
target_doc_ids = [
    "2050767", # Ofício CAD-TI 122/2026
    "2050773", # Termo TSID nº 01/2026
    "2050791", # Despacho Decisório 920
    "2053616", # Despacho EPD
    "2097794", # TSID 02
    "2097798", # Despacho CI 2097798
    "2106960", # Despacho DGI 2106960
    "2106972", # Despacho DGI 2106972
    "2108971", # Despacho CI 2108971
    "2145419", # TSID 03
    "2145422", # Formulário - Respostas do Questionário
    "2145424", # Relatório Individual Preliminar - DPGE
    "2145425", # Formulário - Comentários do Gestor
    "2145435", # Correspondência - Encerramento
    "2145441", # Despacho CI 2145441
    "2146497", # Despacho EPD 2146497
    "2223276"  # Despacho CI 2223276
]

print("Starting document extraction for targets:", target_doc_ids)

for doc_num in target_doc_ids:
    print(f"\n--- Extracting {doc_num} ---")
    click_code = f"""
    (() => {{
      const tree = document.getElementById('ifrArvore');
      if (!tree || !tree.contentDocument) return "no tree";
      const a = Array.from(tree.contentDocument.querySelectorAll('a')).find(el => el.innerText.includes('{doc_num}'));
      if (a) {{
        a.click();
        return a.innerText.trim();
      }}
      return "not found";
    }})()
    """
    res_click = eval_js(click_code)
    print(f"Click: {res_click}")
    if res_click == "not found" or res_click == "no tree":
        continue
    
    time.sleep(1.2)
    
    extract_code = """
    (() => {
      const f = document.getElementById('ifrConteudoVisualizacao');
      if (!f || !f.contentDocument) return { error: "no ifrConteudoVisualizacao" };
      const doc = f.contentDocument;
      
      const inner = doc.getElementById('ifrVisualizacao');
      if (inner && inner.contentDocument) {
        const idoc = inner.contentDocument;
        const anexoLink = Array.from(idoc.querySelectorAll('iframe, embed, object, a')).map(e => e.src || e.data || e.href).filter(Boolean);
        return {
          type: "ifrVisualizacao",
          title: idoc.title,
          text: idoc.body ? idoc.body.innerText : "",
          links: anexoLink
        };
      }
      
      const innerIframes = Array.from(doc.querySelectorAll('iframe')).map(i => {
        try { return i.contentDocument ? i.contentDocument.body.innerText : ""; }
        catch(e) { return ""; }
      });
      
      return {
        type: "direct",
        title: doc.title,
        text: doc.body ? doc.body.innerText : "",
        innerIframes: innerIframes
      };
    })()
    """
    res_info = eval_js(extract_code)
    if not res_info:
        print("No info returned!")
        continue
    
    # Check if there is an attachment link to download
    links = res_info.get("links", [])
    download_url = None
    for l in links:
        if "documento_download_anexo" in l:
            download_url = l
            break
    
    clean_name = re.sub(r'[\\/*?:"<>|]', '_', res_click)
    
    if download_url:
        print(f"Found download URL: {download_url[:100]}...")
        pdf_path = os.path.join(DOCS_DIR, f"{doc_num}_{clean_name}.pdf")
        r = sess.get(download_url)
        with open(pdf_path, "wb") as fp:
            fp.write(r.content)
        print(f"Saved PDF ({len(r.content)} bytes) to {pdf_path}")
    else:
        # Save extracted text
        text_content = res_info.get("text", "")
        if not text_content and res_info.get("innerIframes"):
            text_content = "\n\n".join(res_info.get("innerIframes"))
        
        txt_path = os.path.join(DOCS_DIR, f"{doc_num}_{clean_name}.txt")
        with open(txt_path, "w", encoding="utf-8") as fp:
            fp.write(text_content)
        print(f"Saved Text ({len(text_content)} chars) to {txt_path}")

ws.close()
print("\nDocument extraction completed!")
