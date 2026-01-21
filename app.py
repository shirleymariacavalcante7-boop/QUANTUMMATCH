# -*- coding: utf-8 -*-
"""
QUANTUM MATCH V3.0 - SHARE & DESTINY EDITION
"""
import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==============================================================================
# LÓGICA DE PROCESSAMENTO (ALGORITMO DE REDUÇÃO)
# ==============================================================================
def calcular_compatibilidade(nome1, nome2):
    nomes_juntos = (nome1 + nome2).lower().replace(" ", "")
    contagem = []
    ja_contado = []
    
    for letra in nomes_juntos:
        if letra not in ja_contado:
            contagem.append(nomes_juntos.count(letra))
            ja_contado.append(letra)
    
    passos_animacao = [list(contagem)]
    
    # Algoritmo de soma das extremidades (Ponta a Ponta)
    atual = list(contagem)
    while len(atual) > 2:
        nova_lista = []
        while len(atual) > 0:
            if len(atual) == 1:
                nova_lista.append(atual.pop(0))
            else:
                soma = atual.pop(0) + atual.pop(-1)
                if soma > 9:
                    nova_lista.extend([int(d) for d in str(soma)])
                else:
                    nova_lista.append(soma)
        atual = nova_lista
        passos_animacao.append(list(atual))
        
    resultado_final = int("".join(map(str, atual)))
    if resultado_final > 100: resultado_final = 100
    
    # Oráculo de Mensagens
    if resultado_final >= 90:
        msg = "Conexão de Almas Gêmeas! ✨"
        cor = "#ff4d6d"
    elif resultado_final >= 70:
        msg = "Grande Afinidade Detectada! 🔥"
        cor = "#ff8fa3"
    elif resultado_final >= 50:
        msg = "Potencial Interessante... 👀"
        cor = "#6366f1"
    else:
        msg = "Melhor como amigos. 🤝"
        cor = "#94a3b8"

    return resultado_final, passos_animacao, msg, cor

# ==============================================================================
# INTERFACE ULTRA ANIMADA + WHATSAPP
# ==============================================================================
UI_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Quantum Matcher | 2026 Edition</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --primary: #ff4d6d; --bg: #050507; }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        body { background: var(--bg); color: white; overflow: hidden; height: 100vh; display: flex; align-items: center; justify-content: center; }
        #canvas { position: fixed; top: 0; left: 0; z-index: -1; }

        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(25px);
            padding: 50px; border-radius: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center; width: 500px;
            box-shadow: 0 40px 100px rgba(0,0,0,0.8);
            animation: fadeIn 1s ease;
        }

        h1 { font-size: 2.5rem; letter-spacing: -2px; margin-bottom: 30px; }
        h1 span { color: var(--primary); }

        input {
            width: 100%; background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 20px; border-radius: 15px;
            color: white; font-size: 1.1rem; outline: none; transition: 0.4s;
            margin-bottom: 15px;
        }

        .btn-main {
            background: linear-gradient(135deg, #ff4d6d, #ff758f);
            color: white; border: none; padding: 20px; width: 100%;
            border-radius: 15px; font-weight: 800; cursor: pointer; transition: 0.4s;
        }
        .btn-main:hover { transform: scale(1.02); filter: brightness(1.1); }

        #results { display: none; }
        .step-line { display: flex; justify-content: center; gap: 8px; margin: 10px 0; }
        .num { 
            background: rgba(255,255,255,0.1); width: 35px; height: 35px; 
            display: flex; align-items: center; justify-content: center;
            border-radius: 10px; font-weight: 800; color: var(--primary);
            animation: pop 0.3s forwards;
        }

        #final-val { font-size: 5rem; font-weight: 800; margin: 15px 0; transition: 0.5s; }
        #status-msg { font-size: 1.2rem; margin-bottom: 25px; min-height: 1.5em; }

        .share-btn {
            background: #25d366; color: white; text-decoration: none;
            padding: 15px; border-radius: 12px; display: inline-flex;
            align-items: center; gap: 10px; font-weight: 700; font-size: 0.9rem;
            margin-top: 10px; transition: 0.3s;
        }
        .share-btn:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(37,211,102,0.3); }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pop { from { transform: scale(0); } to { transform: scale(1); } }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>

    <div class="glass-card">
        <h1>QUANTUM<span>MATCH</span></h1>
        
        <div id="ui-input">
            <input type="text" id="name1" placeholder="Nome Dele(a)">
            <input type="text" id="name2" placeholder="Seu Nome">
            <button class="btn-main" onclick="process()">ANALISAR CONEXÃO</button>
        </div>

        <div id="results">
            <div id="calc-steps"></div>
            <div id="final-val">0%</div>
            <div id="status-msg"></div>
            
            <div style="display:flex; flex-direction:column; gap:10px;">
                <a id="wa-btn" href="#" target="_blank" class="share-btn" style="display:none;">
                    <i class="fab fa-whatsapp"></i> COMPARTILHAR NO WHATSAPP
                </a>
                <button class="btn-main" onclick="location.reload()" style="background:rgba(255,255,255,0.1); padding: 12px;">NOVO TESTE</button>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let pts = [];
        function init() {
            canvas.width = window.innerWidth; canvas.height = window.innerHeight;
            pts = Array.from({length: 50}, () => ({x: Math.random()*canvas.width, y: Math.random()*canvas.height, v: Math.random()*0.4+0.1}));
        }
        function anim() {
            ctx.clearRect(0,0,canvas.width, canvas.height);
            ctx.fillStyle = "rgba(255, 77, 109, 0.2)";
            pts.forEach(p => { p.y -= p.v; if(p.y < 0) p.y = canvas.height; ctx.beginPath(); ctx.arc(p.x, p.y, 2, 0, Math.PI*2); ctx.fill(); });
            requestAnimationFrame(anim);
        }
        init(); anim();

        async function process() {
            const n1 = document.getElementById('name1').value;
            const n2 = document.getElementById('name2').value;
            if(!n1 || !n2) return;

            document.getElementById('ui-input').style.display = 'none';
            document.getElementById('results').style.display = 'block';

            const res = await fetch('/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({n1, n2})
            });
            const data = await res.json();

            const stepBox = document.getElementById('calc-steps');
            for(let step of data.steps) {
                const div = document.createElement('div');
                div.className = 'step-line';
                step.forEach(n => { div.innerHTML += `<div class="num">${n}</div>`; });
                stepBox.appendChild(div);
                await new Promise(r => setTimeout(r, 450));
            }

            let count = 0;
            const interval = setInterval(() => {
                if(count >= data.score) {
                    clearInterval(interval);
                    finalize(data, n1, n2);
                } else {
                    count++;
                    document.getElementById('final-val').innerText = count + "%";
                }
            }, 25);
        }

        function finalize(data, n1, n2) {
            const m = document.getElementById('status-msg');
            m.innerText = data.msg;
            m.style.color = data.color;
            document.getElementById('final-val').style.color = data.color;
            
            // Configurar Botão WhatsApp
            const wa = document.getElementById('wa-btn');
            const text = encodeURIComponent(`🔥 Acabei de calcular nossa afinidade no Quantum Match!\\n\\n👤 ${n1} + ${n2}\\n📊 Resultado: ${data.score}%\\n📜 Mensagem: ${data.msg}\\n\\nFaça o seu teste também!`);
            wa.href = `https://api.whatsapp.com/send?text=${text}`;
            wa.style.display = 'inline-flex';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(UI_HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    d = request.json
    score, steps, msg, color = calcular_compatibilidade(d['n1'], d['n2'])
    return jsonify({'score': score, 'steps': steps, 'msg': msg, 'color': color})

if __name__ == '__main__':
    app.run(debug=True)