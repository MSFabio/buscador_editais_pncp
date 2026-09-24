import json, websocket, time

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

req_id = 100
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

# Click on 2145424
js_click = """
(() => {
  const treeFrame = document.getElementById('ifrArvore');
  const doc = treeFrame.contentDocument;
  const link = Array.from(doc.querySelectorAll('a')).find(a => a.innerText.includes('2145424'));
  if (link) {
    link.click();
    return "clicked: " + link.innerText;
  }
  return "not found";
})()
"""
print("Clicking 2145424:", eval_js(js_click))

# Wait 1.5 seconds for frame to load
time.sleep(1.5)

# Inspect viewer
js_inspect = """
(() => {
  const f = document.getElementById('ifrConteudoVisualizacao');
  if (!f || !f.contentDocument) return "no ifrConteudoVisualizacao";
  const doc = f.contentDocument;
  const iframes = Array.from(doc.querySelectorAll('iframe, embed, object')).map(e => ({
    tag: e.tagName,
    src: e.src || e.data,
    id: e.id
  }));
  return {
    url: doc.location.href,
    title: doc.title,
    bodyTextSnippet: doc.body.innerText.slice(0, 500),
    elements: iframes
  };
})()
"""
res = eval_js(js_inspect)
print("Inspect result:", json.dumps(res, indent=2, ensure_ascii=False))

ws.close()
