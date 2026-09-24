import json, websocket, time

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

req_id = 10

# Test reading tree links
js_get_links = """
(() => {
  const treeFrame = document.getElementById('ifrArvore');
  if (!treeFrame || !treeFrame.contentDocument) return [];
  const links = Array.from(treeFrame.contentDocument.querySelectorAll('a'));
  return links.map(a => a.innerText.trim()).filter(t => t.length > 0);
})()
"""

links = eval_js(js_get_links)
print(f"Found {len(links)} links in treeFrame:")
for l in links[:15]:
    print(" -", l)

ws.close()
