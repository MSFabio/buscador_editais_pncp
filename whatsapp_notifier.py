import os
import json
import requests
import urllib.parse
import datetime

CONFIG_PATH = r'C:\Users\11429149760\.gemini\antigravity\scratch\config_whatsapp.json'

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "whatsapp_enabled": True,
        "phone_number": "",
        "provider": "callmebot",
        "callmebot_apikey": ""
    }

def format_whatsapp_message(ba_items, today_str):
    ba_pregao = [i for i in ba_items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
    
    msg_lines = []
    msg_lines.append(f"🚨 *ALERTA PNCP - EDITAIS ABERTOS NA BAHIA* 🚨")
    msg_lines.append(f"📅 *Data:* {today_str}")
    msg_lines.append(f"📊 *Total de Editais em BA:* {len(ba_items)}")
    msg_lines.append(f"⚡ *Pregões Eletrônicos:* {len(ba_pregao)}\n")

    if ba_pregao:
        msg_lines.append("📌 *DESTAQUES EM PREGÃO ELETRÔNICO:*")
        for idx, item in enumerate(ba_pregao[:5], 1):
            orgao = item.get('orgao') or 'Órgão não informado'
            muni = item.get('municipio') or 'BA'
            title = item.get('title') or 'Edital'
            dt_enc = item.get('data_encerramento_proposta') or 'N/A'
            if 'T' in dt_enc:
                dt_enc = dt_enc.split('T')[0]
                dt_enc = datetime.datetime.strptime(dt_enc, "%Y-%m-%d").strftime("%d/%m/%Y")
            
            link = item.get('link_pncp') or ''
            msg_lines.append(f"\n*{idx}. {title}*")
            msg_lines.append(f"🏛️ *Órgão:* {orgao} ({muni})")
            msg_lines.append(f"⏰ *Sessão Pública:* {dt_enc}")
            if link:
                msg_lines.append(f"🔗 {link}")

    msg_lines.append("\n📁 *Relatório em PDF gerado e salvo no sistema.*")
    return "\n".join(msg_lines)

def send_whatsapp_notification(ba_items):
    config = load_config()
    if not config.get('whatsapp_enabled'):
        print("[WhatsApp] Notificações desativadas na configuração.")
        return

    phone = config.get('phone_number')
    if not phone or phone == "5571999999999":
        print("[WhatsApp] ⚠️ ATENÇÃO: Configure seu número de telefone em config_whatsapp.json")
        return

    today_str = datetime.date.today().strftime('%d/%m/%Y')
    message_text = format_whatsapp_message(ba_items, today_str)

    provider = config.get('provider', 'webhook').lower()

    if provider == 'callmebot':
        # Free CallMeBot WhatsApp API
        apikey = config.get('callmebot_apikey', '')
        encoded_text = urllib.parse.quote(message_text)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_text}&apikey={apikey}"
        try:
            r = requests.get(url, timeout=15)
            print(f"[WhatsApp CallMeBot] Status: {r.status_code}")
        except Exception as e:
            print(f"[WhatsApp CallMeBot] Erro ao enviar: {e}")

    elif provider == 'webhook' or provider == 'zapi' or provider == 'evolution':
        # HTTP Webhook API (Z-API, Evolution API, UltraMsg, etc.)
        api_url = config.get('api_url')
        if not api_url:
            print("[WhatsApp] API URL não informada.")
            return
        
        payload = {
            "phone": phone,
            "number": phone,
            "message": message_text,
            "text": message_text
        }
        headers = {
            "Content-Type": "application/json",
            "Client-Token": config.get('api_token', '')
        }
        try:
            r = requests.post(api_url, json=payload, headers=headers, timeout=15)
            print(f"[WhatsApp API] Status: {r.status_code}, Response: {r.text[:200]}")
        except Exception as e:
            print(f"[WhatsApp API] Erro ao enviar: {e}")

    elif provider == 'pywhatkit':
        try:
            import pywhatkit
            now = datetime.datetime.now()
            pywhatkit.sendwhatmsg_instantly(f"+{phone}", message_text, wait_time=15, tab_close=True)
            print("[WhatsApp pywhatkit] Mensagem enviada com sucesso.")
        except Exception as e:
            print(f"[WhatsApp pywhatkit] Erro: {e}")

if __name__ == '__main__':
    # Test notification with mock data
    print("Testing WhatsApp formatting...")
    sample_msg = format_whatsapp_message([], "12/08/2026")
    print(sample_msg)
