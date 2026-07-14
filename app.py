import os, sqlite3, datetime, json, requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

OPENROUTER_API_KEY = "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"
DB_NAME = 'lunar.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversas (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, pergunta TEXT, resposta TEXT, data TEXT)''')
    conn.commit()
    conn.close()
init_db()

def chamar_ia(pergunta):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for modelo in ["deepseek/deepseek-v4-pro", "qwen/qwen-3.7-max", "zhipuai/glm-5.2"]:
        try:
            r = requests.post(url, json={"model":modelo, "messages":[{"role":"user","content":pergunta}], "max_tokens":500}, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except:
            continue
    return "Não consegui responder."

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template_string("""<html><head><title>Lunar IA</title><style>body{background:#0a0a1a;color:#e0e0ff;font-family:Arial;display:flex;justify-content:center;padding:20px;}.container{max-width:800px;width:100%;background:rgba(20,20,50,0.8);border-radius:20px;padding:20px;}.chat{background:rgba(0,0,20,0.5);border-radius:15px;padding:15px;min-height:300px;max-height:400px;overflow-y:auto;}.msg{margin:8px 0;padding:10px;background:rgba(40,50,100,0.3);border-left:3px solid #7c3aed;border-radius:8px;}.user{border-left-color:#22d3ee;background:rgba(30,80,120,0.2);}.input{display:flex;gap:10px;margin-top:10px;}.input input{flex:1;padding:12px;border-radius:20px;border:1px solid #7c3aed;background:rgba(0,0,30,0.5);color:white;}.input button{padding:12px 30px;border-radius:20px;border:none;background:#7c3aed;color:white;cursor:pointer;}h1{text-align:center;background:linear-gradient(135deg,#a78bfa,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}</style></head><body><div class="container"><h1>🌕 Lunar IA ∞</h1><div class="chat" id="chat"><div class="msg">🌕 Digite /ajuda</div></div><div class="input"><input id="input" placeholder="Digite aqui..." onkeydown="if(event.key==='Enter')enviar()"><button onclick="enviar()">Enviar</button></div></div><script>function enviar(){const input=document.getElementById('input');const msg=input.value.trim();if(!msg)return;const chat=document.getElementById('chat');const userDiv=document.createElement('div');userDiv.className='msg user';userDiv.textContent='👤 '+msg;chat.appendChild(userDiv);input.value='';const load=document.createElement('div');load.className='msg';load.textContent='🌕 Pensando...';load.id='load';chat.appendChild(load);fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pergunta:msg,usuario:'default'})}).then(r=>r.json()).then(data=>{document.getElementById('load')?.remove();const resp=document.createElement('div');resp.className='msg';resp.innerHTML='🌕 '+data.resposta;chat.appendChild(resp);}).catch(()=>{document.getElementById('load')?.remove();const err=document.createElement('div');err.className='msg';err.textContent='❌ Erro';chat.appendChild(err);});}</script></body></html>""")

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    pergunta = data.get('pergunta', '')
    if not pergunta:
        return jsonify({'resposta': 'Digite algo'})
    if pergunta.startswith('/'):
        if pergunta == '/ajuda':
            resp = "/ajuda, /estado, /agro preco"
        else:
            resp = chamar_ia(pergunta)
    else:
        resp = chamar_ia(pergunta)
    return jsonify({'resposta': resp})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
