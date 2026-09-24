import json, websocket, requests, re
from bs4 import BeautifulSoup

with open(r"C:\Users\11429149760\AppData\Local\Google\Chrome\User Data\DevToolsActivePort", "r") as f:
    port = f.readline().strip()
    browser_path = f.readline().strip()

ws_url = f"ws://127.0.0.1:{port}{browser_path}"
ws = websocket.create_connection(ws_url, suppress_origin=True)
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

ws.send(json.dumps({"id": 3, "sessionId": session_id, "method": "Network.getCookies"}))
cookies = {}
while True:
    msg = json.loads(ws.recv())
    if msg.get("id") == 3:
        for c in msg.get("result", {}).get("cookies", []):
            if "def.br" in c.get("domain", ""):
                cookies[c["name"]] = c["value"]
        break
ws.close()

session = requests.Session()
session.cookies.update(cookies)
session.headers.update({"User-Agent": "Mozilla/5.0"})

url = "https://sei.rj.def.br/sei/controlador.php?acao=arvore_visualizar&acao_origem=procedimento_visualizar&id_procedimento=2848395&id_documento=3028615&infra_sistema=100000100&infra_unidade_atual=110000438&infra_hash=d2f479df41bfce723fae03cc143a006adecd5e589675d4e46fa43e6e9a50e429"
resp = session.get(url)
soup = BeautifulSoup(resp.text, "html.parser")
iframes = soup.find_all("iframe")
print("Iframes found:", len(iframes))
for ifr in iframes:
    src = ifr.get("src", "")
    print("iframe src:", src[:100])
    if src:
        if not src.startswith("http"):
            src = "https://sei.rj.def.br/sei/" + src
        sub_resp = session.get(src)
        print("   sub_resp:", sub_resp.status_code, len(sub_resp.text), "Nelson Wesp" in sub_resp.text)
        sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
        sub_iframes = sub_soup.find_all("iframe")
        print("   sub_iframes:", len(sub_iframes))
        for sifr in sub_iframes:
            ssrc = sifr.get("src", "")
            if not ssrc.startswith("http"):
                ssrc = "https://sei.rj.def.br/sei/" + ssrc
            doc_resp = session.get(ssrc)
            print("      doc_resp:", doc_resp.status_code, len(doc_resp.text), "Nelson Wesp" in doc_resp.text)
            if "Nelson Wesp" in doc_resp.text:
                print("FOUND DOCUMENT CONTENT!")
