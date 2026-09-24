import json, websocket

ws_url = "ws://127.0.0.1:9222/devtools/browser/5b6640f0-461f-480f-acca-63840f7c7aac"
ws = websocket.create_connection(ws_url)

msg = {"id": 1, "method": "Target.getTargets"}
ws.send(json.dumps(msg))

res = ws.recv()
data = json.loads(res)
for t in data.get("result", {}).get("targetInfos", []):
    if t.get("type") == "page":
        print(t.get("targetId"), t.get("title"), t.get("url"))

ws.close()
