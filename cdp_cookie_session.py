import json, websocket, requests

with open(r"C:\Users\11429149760\AppData\Local\Google\Chrome\User Data\DevToolsActivePort", "r") as f:
    port = f.readline().strip()
    browser_path = f.readline().strip()

ws_url = f"ws://127.0.0.1:{port}{browser_path}"
ws = websocket.create_connection(ws_url, suppress_origin=True)

# 1. Get targets
ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
res = json.loads(ws.recv())
target_id = [t["targetId"] for t in res["result"]["targetInfos"] if "002323" in t.get("title","")][0]

# 2. Attach
ws.send(json.dumps({"id": 2, "method": "Target.attachToTarget", "params": {"targetId": target_id, "flatten": True}}))

session_id = None
while True:
    msg = json.loads(ws.recv())
    if msg.get("method") == "Target.attachedToTarget":
        session_id = msg["params"]["sessionId"]
        break

print("Attached with session ID:", session_id)

# 3. Get cookies
ws.send(json.dumps({"id": 3, "sessionId": session_id, "method": "Network.getCookies"}))

cookies = {}
while True:
    msg = json.loads(ws.recv())
    if msg.get("id") == 3:
        for c in msg.get("result", {}).get("cookies", []):
            if "def.br" in c.get("domain", ""):
                cookies[c["name"]] = c["value"]
                print(f"Cookie: {c['name']} = {c['value'][:15]}...")
        break

ws.close()

if cookies:
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    # Test fetch Despacho 2223276
    url = "https://sei.rj.def.br/sei/controlador.php?acao=arvore_visualizar&acao_origem=procedimento_visualizar&id_procedimento=2848395&id_documento=3028615&infra_sistema=100000100&infra_unidade_atual=110000438&infra_hash=d2f479df41bfce723fae03cc143a006adecd5e589675d4e46fa43e6e9a50e429"
    resp = session.get(url)
    print("Fetch test:", resp.status_code, len(resp.text), "Nelson Wesp" in resp.text)
