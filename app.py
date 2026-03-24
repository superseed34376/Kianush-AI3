from flask import Flask, render_template_string, request, Response, stream_with_context
from groq import Groq
import json

app = Flask(__name__)

GROQ_API_KEY = "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"
DEFAULT_MODEL  = "llama-3.3-70b-versatile"
SYSTEM_PROMPT  = (
    "You are Kianush AI, a brilliant AI assistant. "
    "Format responses in Markdown: use **bold**, `inline code`, ```code blocks```, "
    "# headings, and bullet lists where appropriate. Be precise and helpful."
)

client = Groq(api_key=GROQ_API_KEY)

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kianush AI</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark-dimmed.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#e8e8e8;font-family:'Inter',sans-serif;height:100vh;display:flex;overflow:hidden}

/* SIDEBAR */
.sidebar{width:268px;flex-shrink:0;background:#111;border-right:1px solid #1f1f1f;display:flex;flex-direction:column;overflow:hidden}
.sidebar-header{display:flex;align-items:center;gap:10px;padding:20px 16px 16px;flex-shrink:0}
.sidebar-logo{width:32px;height:32px;background:#1e1e1e;border:1px solid #2a2a2a;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.85rem;color:#e8e8e8;flex-shrink:0}
.sidebar-brand{display:flex;flex-direction:column}
.sidebar-brand-name{font-size:.88rem;font-weight:600;color:#e8e8e8;line-height:1.2}
.sidebar-brand-tier{font-size:.6rem;font-weight:500;color:#555;letter-spacing:.1em;text-transform:uppercase}
.sidebar-new-chat{margin:0 12px 12px;flex-shrink:0}
.new-chat-btn{display:flex;align-items:center;gap:8px;width:100%;padding:10px 14px;border-radius:10px;border:1px solid #2a2a2a;background:#1a1a1a;color:#ccc;font-family:'Inter',sans-serif;font-size:.84rem;font-weight:500;cursor:pointer;transition:all .15s}
.new-chat-btn:hover{background:#222;border-color:#333;color:#fff}
.new-chat-btn svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.sidebar-scroll{flex:1;overflow-y:auto;padding:0 12px 12px}
.sidebar-scroll::-webkit-scrollbar{width:3px}
.sidebar-scroll::-webkit-scrollbar-thumb{background:#222;border-radius:99px}
.chat-section-label{font-size:.65rem;font-weight:600;letter-spacing:.1em;color:#444;text-transform:uppercase;padding:12px 4px 6px}
.chat-item{display:flex;align-items:center;gap:8px;width:100%;padding:8px 10px;border-radius:8px;border:1px solid transparent;background:transparent;color:#888;font-family:'Inter',sans-serif;font-size:.8rem;cursor:pointer;transition:all .12s;text-align:left}
.chat-item:hover{background:#1a1a1a;color:#ccc}
.chat-item.active{background:#1e1e1e;border-color:#2a2a2a;color:#e8e8e8}
.chat-item svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0;opacity:.6}
.chat-item-title{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chat-item-del{flex-shrink:0;background:none;border:none;color:#444;cursor:pointer;padding:1px 3px;border-radius:3px;display:none;font-size:.75rem;transition:color .12s;line-height:1}
.chat-item:hover .chat-item-del,.chat-item.active .chat-item-del{display:block}
.chat-item-del:hover{color:#ef4444}
.sidebar-bottom{padding:10px 12px 16px;border-top:1px solid #1f1f1f;flex-shrink:0;display:flex;flex-direction:column;gap:2px}
.sb-btn{display:flex;align-items:center;gap:8px;width:100%;padding:8px 10px;border-radius:8px;border:none;background:transparent;color:#555;font-family:'Inter',sans-serif;font-size:.8rem;cursor:pointer;transition:all .12s;text-align:left}
.sb-btn:hover{background:#1a1a1a;color:#aaa}
.sb-btn svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}

/* MAIN */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden;background:#0a0a0a}

/* TOPBAR */
.topbar{display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:56px;flex-shrink:0;border-bottom:1px solid #1a1a1a}
.topbar-title{font-size:1rem;font-weight:600;color:#e8e8e8}
.topbar-center{display:flex;align-items:center;gap:10px}
.model-dropdown{display:flex;align-items:center;gap:6px;padding:6px 12px;border-radius:8px;border:1px solid #2a2a2a;background:#141414;position:relative}
.model-dropdown select{background:transparent;border:none;outline:none;color:#ccc;font-family:'Inter',sans-serif;font-size:.8rem;cursor:pointer;appearance:none;padding-right:18px}
.model-dropdown select option{background:#1a1a1a}
.model-dropdown-arrow{position:absolute;right:10px;pointer-events:none;color:#555;font-size:.65rem}
.topbar-right{display:flex;align-items:center;gap:10px}
.status-pill{display:flex;align-items:center;gap:6px;padding:5px 12px;border-radius:8px;background:#141414;border:1px solid #2a2a2a;font-size:.72rem;font-weight:600;color:#e8e8e8;letter-spacing:.02em}
.status-dot{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px #22c55e}
.topbar-icon-btn{width:32px;height:32px;border-radius:7px;border:1px solid #2a2a2a;background:#141414;color:#888;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .12s}
.topbar-icon-btn:hover{background:#1e1e1e;color:#ccc}
.topbar-icon-btn svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

/* CHAT */
.chat-area{flex:1;display:flex;flex-direction:column;overflow:hidden}
.messages{flex:1;overflow-y:auto;padding:32px 0;display:flex;flex-direction:column;scroll-behavior:smooth}
.messages::-webkit-scrollbar{width:4px}
.messages::-webkit-scrollbar-thumb{background:#222;border-radius:99px}

/* WELCOME */
.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;flex:1;text-align:center;padding:60px 40px 20px}
.welcome-title{font-size:clamp(2.2rem,5vw,3.8rem);font-weight:700;color:#e8e8e8;letter-spacing:-.03em;line-height:1.1;max-width:720px;margin-bottom:20px}
.welcome-sub{font-size:1rem;color:#666;max-width:480px;line-height:1.7;margin-bottom:40px}
.welcome-chips{display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap}
.chip{display:flex;align-items:center;gap:7px;padding:9px 18px;background:#141414;border:1px solid #222;border-radius:99px;color:#888;font-size:.82rem;cursor:pointer;transition:all .15s;white-space:nowrap;font-family:'Inter',sans-serif}
.chip:hover{background:#1e1e1e;border-color:#333;color:#ccc}
.chip svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

/* BUBBLES */
.msg-wrap{display:flex;flex-direction:column;gap:4px;padding:0 max(24px,calc(50% - 400px));margin-bottom:20px;animation:fadeUp .2s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.msg-header{display:flex;align-items:center;gap:8px;padding:0 2px;font-size:.68rem;font-family:'JetBrains Mono',monospace;letter-spacing:.06em;color:#444}
.msg-header .name{font-weight:600}
.msg-wrap.user .name{color:#888}
.msg-wrap.ai .name{color:#666}
.bubble{border-radius:12px;padding:12px 16px;font-size:.92rem;line-height:1.75;border:1px solid transparent}
.msg-wrap.user .bubble{background:#161616;border-color:#222;color:#d4d4d4}
.msg-wrap.ai .bubble{background:transparent;padding-left:2px;color:#c8c8c8}
.bubble h1,.bubble h2,.bubble h3{color:#e8e8e8;margin:.6em 0 .3em;font-weight:600}
.bubble h1{font-size:1.25rem}.bubble h2{font-size:1.1rem}.bubble h3{font-size:.98rem}
.bubble strong{color:#e0e0e0}
.bubble a{color:#888}
.bubble code:not(pre code){background:#161616;color:#f97316;font-family:'JetBrains Mono',monospace;font-size:.82em;padding:2px 5px;border-radius:4px;border:1px solid #222}
.bubble pre{background:#111;border:1px solid #222;border-radius:8px;margin:8px 0;overflow:hidden}
.bubble pre .code-header{display:flex;justify-content:space-between;align-items:center;padding:5px 12px;background:#1a1a1a;border-bottom:1px solid #222;font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#555;letter-spacing:.08em}
.bubble pre code{display:block;padding:12px 14px;font-family:'JetBrains Mono',monospace;font-size:.8rem;line-height:1.6;overflow-x:auto;color:#aaa;background:transparent;border:none}
.copy-code-btn{background:none;border:1px solid #2a2a2a;color:#555;font-family:'JetBrains Mono',monospace;font-size:.62rem;padding:2px 7px;border-radius:4px;cursor:pointer;transition:all .12s}
.copy-code-btn:hover{border-color:#444;color:#888}
.bubble ul,.bubble ol{padding-left:1.3em;margin:.35em 0}
.bubble li{margin:.2em 0}
.bubble p{margin:.35em 0}
.bubble p:first-child{margin-top:0}.bubble p:last-child{margin-bottom:0}
.msg-footer{display:flex;justify-content:flex-end;padding:0 2px}
.copy-btn{background:none;border:1px solid #1f1f1f;color:#444;font-family:'JetBrains Mono',monospace;font-size:.62rem;padding:3px 9px;border-radius:99px;cursor:pointer;transition:all .12s}
.copy-btn:hover{border-color:#333;color:#777}
.copy-btn.copied{border-color:#22c55e;color:#22c55e}

/* TYPING */
.typing-wrap{display:none;margin-bottom:14px}
.typing-wrap.visible{display:flex;flex-direction:column;gap:4px;padding:0 max(24px,calc(50% - 400px))}
.typing-bubble{background:transparent;padding:6px 2px;display:flex;align-items:center;gap:5px}
.typing-dot{width:5px;height:5px;border-radius:50%;background:#444;animation:bounce .9s ease-in-out infinite}
.typing-dot:nth-child(2){animation-delay:.15s}.typing-dot:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:.4}40%{transform:translateY(-4px);opacity:1}}
.stream-cursor::after{content:'▋';color:#444;animation:blink-c .7s step-end infinite}
@keyframes blink-c{0%,100%{opacity:1}50%{opacity:0}}

/* INPUT */
.input-area{background:#0a0a0a;padding:0 max(24px,calc(50% - 400px)) 12px;flex-shrink:0}
.input-card{background:#131313;border:1px solid #222;border-radius:16px;transition:border-color .15s}
.input-card:focus-within{border-color:#333}
#user-input{width:100%;background:transparent;border:none;outline:none;color:#e8e8e8;font-family:'Inter',sans-serif;font-size:.92rem;padding:16px 18px 8px;resize:none;min-height:60px;max-height:200px;line-height:1.6}
#user-input::placeholder{color:#444}
.input-bottom{display:flex;align-items:center;justify-content:space-between;padding:8px 12px}
.input-left{display:flex;align-items:center;gap:4px}
.icon-btn{display:flex;align-items:center;gap:4px;background:none;border:none;color:#555;padding:6px 8px;border-radius:7px;cursor:pointer;font-size:.75rem;transition:all .12s}
.icon-btn:hover{background:#1e1e1e;color:#aaa}
.icon-btn svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.input-right{display:flex;align-items:center;gap:8px}
.project-btn{display:flex;align-items:center;gap:5px;padding:5px 12px;border-radius:8px;border:1px solid #2a2a2a;background:none;color:#666;font-size:.78rem;cursor:pointer;transition:all .12s;font-family:'Inter',sans-serif}
.project-btn:hover{border-color:#333;color:#aaa;background:#1a1a1a}
.project-btn svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.send-btn{display:flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:99px;border:none;background:#e8e8e8;color:#0a0a0a;cursor:pointer;transition:all .15s}
.send-btn:hover{background:#fff}
.send-btn:disabled{opacity:.25;cursor:not-allowed}
.send-btn svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.input-footer{text-align:center;font-size:.65rem;color:#333;padding:8px 0 4px;letter-spacing:.02em;font-family:'Inter',sans-serif}
</style>
</head>
<body>

<!-- SIDEBAR -->
<div class="sidebar">
  <div class="sidebar-header">
    <div class="sidebar-logo">✦</div>
    <div class="sidebar-brand">
      <div class="sidebar-brand-name">Kianush AI</div>
      <div class="sidebar-brand-tier">Premium Tier</div>
    </div>
  </div>

  <div class="sidebar-new-chat">
    <button class="new-chat-btn" onclick="newChat()">
      <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
      New Chat
    </button>
  </div>

  <div class="sidebar-scroll">
    <div id="chat-list-today-label" class="chat-section-label" style="display:none">Today</div>
    <div id="chat-list-today"></div>
    <div id="chat-list-older-label" class="chat-section-label" style="display:none">Previous 7 Days</div>
    <div id="chat-list-older"></div>
  </div>

  <div class="sidebar-bottom">
    <button class="sb-btn" onclick="copyLast()">
      <svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
      Copy last reply
    </button>
    <button class="sb-btn" onclick="saveHistory()">
      <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Save history
    </button>
  </div>
</div>

<!-- MAIN -->
<div class="main">
  <div class="topbar">
    <div class="topbar-title">Kianush Intelligence</div>
    <div class="topbar-center">
      <div class="model-dropdown">
        <select id="model-select">
          <option value="llama-3.3-70b-versatile">Llama 3.3 70B</option>
          <option value="llama-3.1-8b-instant">Llama 3.1 8B</option>
          <option value="llama3-70b-8192">Llama3 70B</option>
          <option value="llama3-8b-8192">Llama3 8B</option>
          <option value="mixtral-8x7b-32768">Mixtral 8x7B</option>
          <option value="gemma2-9b-it">Gemma2 9B</option>
        </select>
        <span class="model-dropdown-arrow">▾</span>
      </div>
    </div>
    <div class="topbar-right">
      <div class="status-pill">
        <div class="status-dot"></div>
        ONLINE
      </div>
      <button class="topbar-icon-btn" title="Share">
        <svg viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
      </button>
      <button class="topbar-icon-btn" title="More">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="19" r="1" fill="currentColor"/></svg>
      </button>
    </div>
  </div>

  <div class="chat-area">
    <div class="messages" id="messages">
      <div class="welcome" id="welcome">
        <div class="welcome-title">What can I help you with?</div>
        <div class="welcome-sub">Ask anything. Ultra-fast inference with Markdown rendering and memory.</div>
        <div class="welcome-chips">
          <button class="chip" onclick="fillPrompt('Explain a concept to me')">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Explain something
          </button>
          <button class="chip" onclick="fillPrompt('Write code for ')">
            <svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            Write code
          </button>
          <button class="chip" onclick="fillPrompt('Summarize the following: ')">
            <svg viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
            Summarize
          </button>
          <button class="chip" onclick="fillPrompt('Help me brainstorm ideas for ')">
            <svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            Brainstorm
          </button>
          <button class="chip" onclick="fillPrompt('Debug this code: ')">
            <svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            Debug code
          </button>
        </div>
      </div>
      <div class="typing-wrap" id="typing">
        <div class="msg-header"><span class="name">KIANUSH AI</span></div>
        <div class="typing-bubble">
          <div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>
        </div>
      </div>
    </div>

    <div class="input-area">
      <div class="input-card">
        <textarea id="user-input" placeholder="Ask Kianush AI anything..." rows="1"></textarea>
        <div class="input-bottom">
          <div class="input-left">
            <button class="icon-btn" title="Attach">
              <svg viewBox="0 0 24 24"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
            </button>
          </div>
          <div class="input-right">
            <button class="project-btn">
              <svg viewBox="0 0 24 24"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
              Project
            </button>
            <button class="send-btn" id="send-btn" onclick="sendMessage()">
              <svg viewBox="0 0 24 24"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
            </button>
          </div>
        </div>
      </div>
      <div class="input-footer">KIANUSH AI CAN MAKE MISTAKES. VERIFY IMPORTANT INFO.</div>
    </div>
  </div>
</div>

<script>
let history=[], streaming=false, lastAiText='', msgCount=0, turnCount=0;
let sessions=[], activeId=null;

function genId(){return 'c'+Date.now()+'_'+Math.random().toString(36).slice(2,6)}
function titleFromText(t){return t.length>38?t.slice(0,38).trim()+'…':t.trim()}

function renderChatList(){
  const tl=document.getElementById('chat-list-today');
  const ol=document.getElementById('chat-list-older');
  const tlb=document.getElementById('chat-list-today-label');
  const olb=document.getElementById('chat-list-older-label');
  if(!tl)return;
  const now=Date.now();
  const today=sessions.filter(s=>now-s.ts<86400000).reverse();
  const older=sessions.filter(s=>now-s.ts>=86400000&&now-s.ts<7*86400000).reverse();
  tlb.style.display=today.length?'':'none';
  olb.style.display=older.length?'':'none';
  function render(el,arr){
    el.innerHTML=arr.map(s=>`
      <button class="chat-item ${s.id===activeId?'active':''}" onclick="switchChat('${s.id}')">
        <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        <span class="chat-item-title">${s.title}</span>
        <span class="chat-item-del" onclick="deleteChat(event,'${s.id}')">✕</span>
      </button>`).join('');
  }
  render(tl,today); render(ol,older);
}

function saveCurrentSession(){
  if(!activeId)return;
  const idx=sessions.findIndex(s=>s.id===activeId);
  if(idx===-1)return;
  sessions[idx].history=[...history];
  sessions[idx].msgCount=msgCount;
  sessions[idx].turnCount=turnCount;
  sessions[idx].lastAiText=lastAiText;
}

function switchChat(id){
  if(streaming)return;
  saveCurrentSession();
  const s=sessions.find(s=>s.id===id);
  if(!s)return;
  activeId=id; history=[...s.history];
  msgCount=s.msgCount||0; turnCount=s.turnCount||0; lastAiText=s.lastAiText||'';
  renderChatList(); restoreMessages(s);
}

function welcomeHTML(){return `<div class="welcome" id="welcome">
  <div class="welcome-title">What can I help you with?</div>
  <div class="welcome-sub">Ask anything. Ultra-fast inference with Markdown rendering and memory.</div>
  <div class="welcome-chips">
    <button class="chip" onclick="fillPrompt('Explain a concept to me')"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>Explain something</button>
    <button class="chip" onclick="fillPrompt('Write code for ')"><svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>Write code</button>
    <button class="chip" onclick="fillPrompt('Summarize the following: ')"><svg viewBox="0 0 24 24"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/></svg>Summarize</button>
    <button class="chip" onclick="fillPrompt('Help me brainstorm ideas for ')"><svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>Brainstorm</button>
    <button class="chip" onclick="fillPrompt('Debug this code: ')"><svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>Debug code</button>
  </div>
</div>`}

function typingHTML(){return `<div class="typing-wrap" id="typing">
  <div class="msg-header"><span class="name">KIANUSH AI</span></div>
  <div class="typing-bubble"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>
</div>`}

function restoreMessages(s){
  const msgs=document.getElementById('messages');
  if(!s.history.length){msgs.innerHTML=welcomeHTML()+typingHTML();return;}
  msgs.innerHTML=typingHTML();
  for(const h of s.history){
    const role=h.role==='user'?'user':'ai';
    const name=role==='user'?'YOU':'KIANUSH AI';
    const footer=role==='ai'?`<div class="msg-footer"><button class="copy-btn" onclick="copyThis(this)">copy</button></div>`:'';
    const wrap=document.createElement('div');
    wrap.className=`msg-wrap ${role}`;
    wrap.innerHTML=`<div class="msg-header"><span class="name">${name}</span></div><div class="bubble">${marked.parse(h.content)}</div>${footer}`;
    const typing=document.getElementById('typing');
    typing.parentNode.insertBefore(wrap,typing);
  }
  hljs.highlightAll(); scrollBottom();
}

function deleteChat(e,id){
  e.stopPropagation(); sessions=sessions.filter(s=>s.id!==id);
  if(activeId===id){sessions.length>0?switchChat(sessions[sessions.length-1].id):newChat();}
  else renderChatList();
}

function newChat(){
  if(streaming)return;
  saveCurrentSession();
  const id=genId();
  sessions.push({id,title:'New chat',history:[],msgCount:0,turnCount:0,lastAiText:'',ts:Date.now()});
  activeId=id; history=[]; msgCount=0; turnCount=0; lastAiText='';
  renderChatList(); restoreMessages({history:[]});
  document.getElementById('user-input').focus();
}

marked.setOptions({breaks:true,gfm:true});
const renderer=new marked.Renderer();
renderer.code=function(code,lang){
  const l=lang?lang.toUpperCase():'CODE';
  const e=code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  return `<pre><div class="code-header"><span>${l}</span><button class="copy-code-btn" onclick="copyCode(this)">copy</button></div><code class="${lang?'language-'+lang:''}">${e}</code></pre>`;
};
marked.use({renderer});

function now(){return new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}
function scrollBottom(){const m=document.getElementById('messages');m.scrollTop=m.scrollHeight}
function updateSendBtn(){
  const v=document.getElementById('user-input').value.trim();
  document.getElementById('send-btn').style.opacity=(v&&!streaming)?'1':'0.25';
}

function addBubble(role,html,id,userText){
  document.getElementById('welcome')?.remove();
  if(role==='user'){
    if(!activeId||!sessions.find(s=>s.id===activeId)){
      const sid=genId();
      sessions.push({id:sid,title:titleFromText(userText||'New chat'),history:[],msgCount:0,turnCount:0,lastAiText:'',ts:Date.now()});
      activeId=sid; renderChatList();
    } else if(history.length===1){
      const idx=sessions.findIndex(s=>s.id===activeId);
      if(idx!==-1){sessions[idx].title=titleFromText(userText||'New chat');renderChatList();}
    }
  }
  const wrap=document.createElement('div');
  wrap.className=`msg-wrap ${role}`;
  if(id)wrap.id=id;
  const name=role==='user'?'YOU':'KIANUSH AI';
  const footer=role==='ai'?`<div class="msg-footer"><button class="copy-btn" onclick="copyThis(this)">copy</button></div>`:'';
  wrap.innerHTML=`<div class="msg-header"><span class="name">${name}</span><span class="ts">${now()}</span></div><div class="bubble">${html}</div>${footer}`;
  const typing=document.getElementById('typing');
  typing.parentNode.insertBefore(wrap,typing);
  scrollBottom(); return wrap;
}

async function sendMessage(){
  if(streaming)return;
  const inp=document.getElementById('user-input');
  const text=inp.value.trim();
  if(!text)return;
  inp.value=''; inp.style.height='auto'; updateSendBtn();
  addBubble('user',marked.parse(text),null,text);
  history.push({role:'user',content:text});
  msgCount++; turnCount++;
  streaming=true;
  document.getElementById('send-btn').disabled=true;
  document.getElementById('typing').classList.add('visible');
  scrollBottom();
  const aiId='ai-'+Date.now();
  const aiBubble=addBubble('ai','<span class="stream-cursor"></span>',aiId);
  const bubbleDiv=aiBubble.querySelector('.bubble');
  document.getElementById('typing').classList.remove('visible');
  let raw='';
  try{
    const model=document.getElementById('model-select').value;
    const resp=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({history,model})});
    const reader=resp.body.getReader();
    const decoder=new TextDecoder();
    while(true){
      const{done,value}=await reader.read();
      if(done)break;
      for(const line of decoder.decode(value,{stream:true}).split('\\n')){
        if(!line.startsWith('data: '))continue;
        const data=line.slice(6);
        if(data==='[DONE]')break;
        try{const p=JSON.parse(data);if(p.token){raw+=p.token;bubbleDiv.innerHTML=marked.parse(raw)+'<span class="stream-cursor"></span>';scrollBottom();}}catch{}
      }
    }
    bubbleDiv.innerHTML=marked.parse(raw);
    hljs.highlightAll();
    lastAiText=raw;
    history.push({role:'assistant',content:raw});
    msgCount++;
    saveCurrentSession();
  }catch(err){bubbleDiv.innerHTML=`<span style="color:#ef4444">Error: ${err.message}</span>`;}
  streaming=false;
  document.getElementById('send-btn').disabled=false;
  updateSendBtn(); scrollBottom();
}

function fillPrompt(text){
  const inp=document.getElementById('user-input');
  inp.value=text; inp.focus();
  inp.style.height='auto';
  inp.style.height=Math.min(inp.scrollHeight,200)+'px';
  updateSendBtn();
}
function copyThis(btn){
  navigator.clipboard.writeText(btn.closest('.msg-wrap').querySelector('.bubble').innerText);
  btn.textContent='✓ copied'; btn.classList.add('copied');
  setTimeout(()=>{btn.textContent='copy';btn.classList.remove('copied');},2000);
}
function copyCode(btn){
  navigator.clipboard.writeText(btn.closest('pre').querySelector('code').innerText);
  btn.textContent='✓'; setTimeout(()=>btn.textContent='copy',1500);
}
function copyLast(){if(lastAiText)navigator.clipboard.writeText(lastAiText);}
function saveHistory(){
  if(!history.length)return;
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([JSON.stringify(history,null,2)],{type:'application/json'}));
  a.download=`kianush_chat_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.json`;
  a.click();
}

newChat();
const ta=document.getElementById('user-input');
ta.addEventListener('input',()=>{ta.style.height='auto';ta.style.height=Math.min(ta.scrollHeight,200)+'px';updateSendBtn();});
ta.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();}});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json()
    history = data.get("history", [])
    model   = data.get("model", DEFAULT_MODEL)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    def generate():
        stream = client.chat.completions.create(
            model=model, messages=messages,
            max_tokens=4096, temperature=0.7, stream=True,
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"\n✦ KIANUSH AI  →  http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port)
