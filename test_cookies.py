import json, websocket, requests

with open(r"C:\Users\11429149760\AppData\Local\Google\Chrome\User Data\DevToolsActivePort", "r") as f:
    port = f.readline().strip()
    browser_path = f.readline().strip()

ws_url = f"ws://127.0.0.1:{port}{browser_path}"
ws = websocket.create_connection(ws_url, suppress_origin=True)

# Attach to target or call Network.getCookies
ws.send(json.dumps({"id": 1, "method": "Storage.getCookies"}))
res = json.loads(ws.recv())

cookies = {}
for c in res.get("result", {}).get("cookies", []):
    if "def.br" in c.get("domain", ""):
        cookies[c["name"]] = c["value"]
        print(f"Cookie: {c['name']} = {c['value'][:15]}... domain={c['domain']}")

ws.close()

if cookies:
    session = requests.Session()
    session.cookies.update(cookies)
    test_url = "https://sei.rj.def.br/sei/controlador.php?acao=procedimento_consultar_historico&id_procedimento=2848395"
    resp = session.get(test_url)
    print(f"Request test: status={resp.status_code}, len={len(resp.text)}")
    print(resp.text[:300])
