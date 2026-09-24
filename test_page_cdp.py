import json, websocket

with open(r"C:\Users\11429149760\AppData\Local\Google\Chrome\User Data\DevToolsActivePort", "r") as f:
    port = f.readline().strip()
    browser_path = f.readline().strip()

ws_url = f"ws://127.0.0.1:{port}{browser_path}"
ws = websocket.create_connection(ws_url, suppress_origin=True)
ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
res = json.loads(ws.recv())
ws.close()

target = None
for t in res.get("result", {}).get("targetInfos", []):
    if "002323" in t.get("title", ""):
        target = t
        break

print("Target found:", target.get("targetId"), target.get("title"))
page_ws_url = f"ws://127.0.0.1:{port}/devtools/page/{target.get('targetId')}"
print("Connecting to page:", page_ws_url)
pws = websocket.create_connection(page_ws_url, suppress_origin=True)

# Evaluate javascript: document.title
pws.send(json.dumps({
    "id": 1,
    "method": "Runtime.evaluate",
    "params": {"expression": "document.title"}
}))
res = json.loads(pws.recv())
print("Result:", res)
pws.close()
