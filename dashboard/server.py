import http.server, json, os, subprocess, threading, time, webbrowser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PORT = 8765
processes = {}
enabled = {
    "agenttube": True,
    "miloagent": True,
    "trend": True,
    "video_use": True,
}

def milo_python():
    p = ROOT/"engines"/"miloagent"/".venv"/"Scripts"/"python.exe"
    return str(p)

ENGINES = {
    "agenttube": {
        "cwd": ROOT/"engines"/"agenttube",
        "cmd": ["npm.cmd","start"] if os.name=="nt" else ["npm","start"],
        "ui": "http://127.0.0.1:3456",
    },
    "miloagent": {
        "cwd": ROOT/"engines"/"miloagent",
        "cmd": [milo_python(),"miloagent.py","run","--web"],
        "ui": "http://127.0.0.1:8420",
    },
}

HTML = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Creator Growth Suite</title>
<style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;margin:0}
main{max-width:1100px;margin:auto;padding:30px 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px}
.card,.box{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:18px}
.box{margin-top:20px}button,a{display:inline-block;border:0;border-radius:8px;padding:9px 12px;margin:3px;color:#fff;text-decoration:none;font-weight:600;cursor:pointer}
.on{background:#238636}.off{background:#6e7681}.open{background:#1f6feb}.stop{background:#da3633}
.status{margin-top:10px;font-weight:700}table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #30363d;text-align:left}
</style></head><body><main>
<h1>Creator Growth Suite</h1>
<p>Rumble → YouTube • Bandcamp • Teespring → Amaze</p>
<div class="grid">
<div class="card"><h2>AgentTube</h2><p>Faceless/avatar video workflow.</p>
<button class="on" onclick="toggle('agenttube',true)">Enable</button>
<button class="off" onclick="toggle('agenttube',false)">Disable</button>
<button class="on" onclick="startE('agenttube')">Start</button>
<button class="stop" onclick="stopE('agenttube')">Stop</button>
<a class="open" href="http://127.0.0.1:3456" target="_blank">Open UI</a>
<div id="agenttube" class="status"></div></div>

<div class="card"><h2>MiloAgent</h2><p>Audience discovery/outreach.</p>
<button class="on" onclick="toggle('miloagent',true)">Enable</button>
<button class="off" onclick="toggle('miloagent',false)">Disable</button>
<button class="on" onclick="startE('miloagent')">Start</button>
<button class="stop" onclick="stopE('miloagent')">Stop</button>
<a class="open" href="http://127.0.0.1:8420" target="_blank">Open UI</a>
<div id="miloagent" class="status"></div></div>

<div class="card"><h2>Trend + Script</h2><p>Trend research and on-camera script workflow.</p>
<button class="on" onclick="toggle('trend',true)">Enable</button>
<button class="off" onclick="toggle('trend',false)">Disable</button>
<div id="trend" class="status"></div></div>

<div class="card"><h2>Video Use</h2><p>Agentic video editing workflow.</p>
<button class="on" onclick="toggle('video_use',true)">Enable</button>
<button class="off" onclick="toggle('video_use',false)">Disable</button>
<div id="video_use" class="status"></div></div>
</div>

<div class="box"><h2>Daily Targets</h2><table>
<tr><td>Unique subscribers</td><td>1,000/day</td></tr>
<tr><td>Long-form views</td><td>35,000/day</td></tr>
<tr><td>Qualified Shorts views</td><td>1,500,000/day</td></tr>
<tr><td>Sales conversions</td><td>200/day</td></tr>
<tr><td>Unique visitors</td><td>1,000/day</td></tr>
</table></div>

<div class="box"><h2>Avatar</h2><p>media/avatar.jpg</p></div>

<script>
async function refresh(){
 let r=await fetch('/api/status');let d=await r.json();
 for(let k of ['agenttube','miloagent','trend','video_use']){
   let e=document.getElementById(k);
   let x=d[k];
   e.innerText=(x.enabled?'ENABLED':'DISABLED')+(x.running?' • RUNNING':'');
 }
}
async function toggle(n,v){await fetch('/api/toggle/'+n+'/'+(v?'1':'0'),{method:'POST'});refresh();}
async function startE(n){let r=await fetch('/api/start/'+n,{method:'POST'});let d=await r.json();if(!d.ok)alert(d.error||'Could not start');setTimeout(refresh,700);}
async function stopE(n){await fetch('/api/stop/'+n,{method:'POST'});setTimeout(refresh,500);}
refresh();setInterval(refresh,3000);
</script></main></body></html>"""

class H(http.server.BaseHTTPRequestHandler):
    def out(self,obj):
        b=json.dumps(obj).encode()
        self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path=="/":
            b=HTML.encode()
            self.send_response(200); self.send_header("Content-Type","text/html"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
        if self.path=="/api/status":
            out={}
            for k in enabled:
                p=processes.get(k)
                out[k]={"enabled":enabled[k],"running":bool(p and p.poll() is None)}
            self.out(out); return
        self.send_error(404)

    def do_POST(self):
        p=urlparse(self.path).path.strip("/").split("/")
        if len(p)>=3 and p[0]=="api":
            if p[1]=="toggle" and len(p)==4 and p[2] in enabled:
                enabled[p[2]]=p[3]=="1"; self.out({"ok":True}); return

            if p[1]=="start" and len(p)==3 and p[2] in ENGINES:
                n=p[2]
                if not enabled[n]: self.out({"ok":False,"error":"This workflow is disabled."}); return
                q=processes.get(n)
                if q and q.poll() is None: self.out({"ok":True}); return
                try:
                    q=subprocess.Popen(ENGINES[n]["cmd"],cwd=str(ENGINES[n]["cwd"]))
                    processes[n]=q; self.out({"ok":True})
                except Exception as e:
                    self.out({"ok":False,"error":str(e)})
                return

            if p[1]=="stop" and len(p)==3 and p[2] in ENGINES:
                n=p[2]; q=processes.get(n)
                if q and q.poll() is None:
                    try:q.terminate()
                    except:pass
                self.out({"ok":True}); return

        self.send_error(404)

    def log_message(self,*args): pass

def open_browser():
    time.sleep(1)
    webbrowser.open(f"http://127.0.0.1:{PORT}")

threading.Thread(target=open_browser,daemon=True).start()
print(f"Creator Growth Suite dashboard: http://127.0.0.1:{PORT}")
print("Leave this terminal open while using the dashboard.")
http.server.ThreadingHTTPServer(("127.0.0.1",PORT),H).serve_forever()
