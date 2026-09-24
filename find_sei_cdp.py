import json, websocket

with open(r"C:\Users\11429149760\AppData\Local\Google\Chrome\User Data\DevToolsActivePort", "r") as f:
    port = f.readline().strip()
    browser_path = f.readline().strip()

ws_url = f"ws://127.0.0.1:{port}{browser_path}"
ws = websocket.create_connection(ws_url, suppress_origin=True)

ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
res = json.loads(ws.recv())

print(f"Connected to Chrome on port {port}!")
sei_targets = []
for t in res.get("result", {}).get("targetInfos", []):
    url = t.get("url", "")
    if "sei" in url:
        sei_targets.append(t)
        print(f"SEI Target: {t.get('targetId')} | {t.get('title')} | {url[:80]}")

ws.close()
