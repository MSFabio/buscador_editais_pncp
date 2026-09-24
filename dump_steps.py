import sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\11429149760\.gemini\antigravity\brain\39837c6c-21ca-4f11-8996-c4b3a6b82e98\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        item = json.loads(line)
        idx = item.get('step_index')
        t = item.get('type')
        if 'tool_calls' in item:
            for tc in item['tool_calls']:
                print(f"STEP {idx} TOOL: {tc.get('name')} | args: {json.dumps(tc.get('args', {}), ensure_ascii=False)[:300]}")
        elif t == 'GENERIC':
            c = item.get('content', '')
            if len(c) > 0 and 'Script ran on page' in c:
                print(f"STEP {idx} OUTPUT: {c[:250].replace(chr(10), ' ')}")
