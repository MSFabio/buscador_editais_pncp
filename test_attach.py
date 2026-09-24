import json, websocket

with open(r"C:\Users\11429149760\AppData\Local\Google\Chrome\User Data\DevToolsActivePort", "r") as f:
    port = f.readline().strip()
    browser_path = f.readline().strip()

ws_url = f"ws://127.0.0.1:{port}{browser_path}"
ws = websocket.create_connection(ws_url, suppress_origin=True)

# 1. Get targets
ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
res = json.loads(ws.recv())
target_id = None
for t in res.get("result", {}).get("targetInfos", []):
    if "002323" in t.get("title", ""):
        target_id = t["targetId"]
        break

print("Target ID:", target_id)

# 2. Attach
ws.send(json.dumps({
    "id": 2,
    "method": "Target.attachToTarget",
    "params": {"targetId": target_id, "flatten": True}
}))
res = json.loads(ws.recv())
session_id = res.get("result", {}).get("sessionId")
print("Session ID:", session_id)

# 3. Evaluate in session
ws.send(json.dumps({
    "id": 3,
    "sessionId": session_id,
    "method": "Runtime.evaluate",
    "params": {"expression": "document.title"}
}))

while True:
    msg = json.loads(ws.recv())
    if msg.get("id") == 3:
        print("Runtime.evaluate result:", msg.get("result", {}).get("result", {}).get("value"))
        break

ws.close()
