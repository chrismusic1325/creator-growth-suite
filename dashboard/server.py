import http.server
import json
import os
import socket
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PORT = 8765
RUNTIME = ROOT / "runtime"
RUNTIME.mkdir(exist_ok=True)

enabled = {
    "agenttube": True,
    "miloagent": True,
    "trend": True,
    "video_use": True,
}

def port_up(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=.4):
            return True
    except Exception:
        return False

def start_detached(cmd, cwd, logfile):
    log = open(RUNTIME / logfile, "a", encoding="utf-8", errors="ignore")
    kwargs = {
        "cwd": str(cwd),
        "stdout": log,
        "stderr": subprocess.STDOUT,
        "env": os.environ.copy(),
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP |
            subprocess.DETACHED_PROCESS
        )
    return subprocess.Popen(cmd, **kwargs)

def milopy():
    return str(ROOT / "engines" / "miloagent" / ".venv" / "Scripts" / "python.exe")

def start_agenttube():
    if port_up(3456):
        return True, "AgentTube already running."
    cmd = ["npm.cmd", "start"] if os.name == "nt" else ["npm", "start"]
    start_detached(cmd, ROOT/"engines"/"agenttube", "agenttube.log")
    time.sleep(4)
    return True, "AgentTube launch requested."

def start_milo():
    py = Path(milopy())
    if not py.exists():
        return False, "Milo Python environment is missing."

    # Milo is useful as a background orchestrator even if its optional
    # web dashboard is not bound to 8420.
    cmd = [str(py), "miloagent.py", "run"]
    start_detached(cmd, ROOT/"engines"/"miloagent", "miloagent.log")
    time.sleep(3)
    return True, "MiloAgent background orchestrator started."

def start_trend():
    agent = ROOT/"engines"/"agenttube"
    cmd = ["cmd.exe","/c",
           "start","Trend + Script",
           "cmd.exe","/k",
           f'cd /d "{agent}" && npm run agent:strategy && npm run agent:script && npm run agent:seo']
    subprocess.Popen(cmd)
    return True, "Trend + Script opened as a manual creator tool."

def start_video():
    video = ROOT/"engines"/"video-use"

    if not video.exists():
        return False, "Video Use engine not found."

    # Prefer existing local Python environment.
    py = video/".venv"/"Scripts"/"python.exe"

    # Open a terminal in the tool instead of pretending we know
    # an upstream UI command that may not exist.
    if py.exists():
        cmd = ["cmd.exe","/c",
               "start","Video Use",
               "cmd.exe","/k",
               f'cd /d "{video}" && "{py}" --version && echo Video Use ready in this terminal.']
    else:
        cmd = ["cmd.exe","/c",
               "start","Video Use",
               "cmd.exe","/k",
               f'cd /d "{video}" && echo Video Use ready in this terminal.']

    subprocess.Popen(cmd)
    return True, "Video Use opened as a manual creator tool."

def stop_port(port):
    ps = (
        "$x=Get-NetTCPConnection -LocalPort "
        + str(port)
        + " -State Listen -ErrorAction SilentlyContinue;"
          "foreach($c in $x){Stop-Process -Id $c.OwningProcess -Force "
          "-ErrorAction SilentlyContinue}"
    )
    subprocess.run(
        ["powershell.exe","-NoProfile","-Command",ps],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

HTML = r"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Creator Growth Suite</title>
<style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;margin:0}
main{max-width:1100px;margin:auto;padding:30px 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px}
.card,.box{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:18px}
.box{margin-top:20px}
button,a{display:inline-block;border:0;border-radius:8px;padding:9px 12px;margin:3px;color:#fff;text-decoration:none;font-weight:600;cursor:pointer}
.on{background:#238636}
.off{background:#6e7681}
.open{background:#1f6feb}
.stop{background:#da3633}
.status{margin-top:10px;font-weight:700}
.small{font-size:13px;color:#9da7b3}
</style>
</head>
<body>
<main>

<h1>Creator Growth Suite</h1>
<p>Rumble → YouTube • Bandcamp • Teespring → Amaze</p>

<div class="grid">

<div class="card">
<h2>AgentTube</h2>
<p>Automated YouTube + Rumble creation and optimization.</p>
<button class="on" onclick="startE('agenttube')">Start</button>
<button class="stop" onclick="stopE('agenttube')">Stop</button>
<a class="open" href="http://127.0.0.1:3456" target="_blank">Open UI</a>
<div id="agenttube" class="status"></div>
</div>

<div class="card">
<h2>MiloAgent</h2>
<p>Traffic, audience and conversion orchestrator for your configured destinations.</p>
<button class="on" onclick="startE('miloagent')">Start</button>
<button class="stop" onclick="stopE('miloagent')">Stop</button>
<div id="miloagent" class="status"></div>
<div class="small">Runs in background mode. Port 8420 is optional.</div>
</div>

<div class="card">
<h2>Trend + Script</h2>
<p>Manual trend research and on-camera script tool.</p>
<button class="on" onclick="startE('trend')">Open Tool</button>
<div id="trend" class="status"></div>
</div>

<div class="card">
<h2>Video Use</h2>
<p>Manual creator/editing tool.</p>
<button class="on" onclick="startE('video_use')">Open Tool</button>
<div id="video_use" class="status"></div>
</div>

</div>

<div class="box">
<h2>Automation Source of Truth</h2>
<p><b>AgentTube:</b> YouTube + Rumble</p>
<p><b>MiloAgent:</b> YouTube + Rumble + Bandcamp + Amaze/Teespring</p>
<p><b>Trend + Script:</b> manual only</p>
<p><b>Video Use:</b> manual only</p>
</div>

<div class="box">
<h2>Live state</h2>
<div id="state"></div>
</div>

<script>
async function refresh(){
    let r=await fetch('/api/status');
    let d=await r.json();

    document.getElementById('agenttube').innerText =
        d.agenttube.running ? 'RUNNING' : 'STOPPED';

    document.getElementById('miloagent').innerText =
        d.miloagent.running ? 'RUNNING' : 'STOPPED';

    document.getElementById('trend').innerText='MANUAL';
    document.getElementById('video_use').innerText='MANUAL';

    document.getElementById('state').innerHTML =
        'Dashboard: RUNNING<br>'+
        'AgentTube: '+(d.agenttube.running?'RUNNING':'STOPPED')+'<br>'+
        'MiloAgent: '+(d.miloagent.running?'RUNNING':'STOPPED');
}

async function startE(n){
    let r=await fetch('/api/start/'+n,{method:'POST'});
    let d=await r.json();
    if(!d.ok) alert(d.error||'Could not start');
    setTimeout(refresh,1200);
}

async function stopE(n){
    await fetch('/api/stop/'+n,{method:'POST'});
    setTimeout(refresh,1000);
}

refresh();
setInterval(refresh,3000);
</script>

</main>
</body>
</html>
"""

class H(http.server.BaseHTTPRequestHandler):

    def out(self,obj):
        b=json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):

        if self.path=="/":
            b=HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type","text/html")
            self.send_header("Content-Length",str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        if self.path=="/api/status":
            # AgentTube status comes from the real port.
            agent = port_up(3456)

            # Milo is considered running if a Milo process from this repo exists.
            ps = subprocess.run(
                ["powershell.exe","-NoProfile","-Command",
                 r"""$x=Get-CimInstance Win32_Process |
                 Where-Object {$_.CommandLine -like '*creator-growth-suite*engines*miloagent*miloagent.py*run*'};
                 if($x){'YES'}"""],
                capture_output=True,text=True
            )
            milo = "YES" in ps.stdout

            self.out({
                "agenttube":{"running":agent},
                "miloagent":{"running":milo},
                "trend":{"running":False},
                "video_use":{"running":False}
            })
            return

        self.send_error(404)

    def do_POST(self):

        p=urlparse(self.path).path.strip("/").split("/")

        if len(p)==3 and p[0]=="api" and p[1]=="start":

            n=p[2]

            if n=="agenttube":
                ok,msg=start_agenttube()

            elif n=="miloagent":
                ok,msg=start_milo()

            elif n=="trend":
                ok,msg=start_trend()

            elif n=="video_use":
                ok,msg=start_video()

            else:
                ok,msg=False,"Unknown tool."

            self.out({"ok":ok,"message":msg})
            return

        if len(p)==3 and p[0]=="api" and p[1]=="stop":

            n=p[2]

            if n=="agenttube":
                stop_port(3456)

            elif n=="miloagent":
                subprocess.run(
                    ["powershell.exe","-NoProfile","-Command",
                     r"""Get-CimInstance Win32_Process |
                     Where-Object {$_.CommandLine -like '*creator-growth-suite*engines*miloagent*miloagent.py*run*'} |
                     ForEach-Object {Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue}"""],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            self.out({"ok":True})
            return

        self.send_error(404)

    def log_message(self,*args):
        pass

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8765")

threading.Thread(target=open_browser,daemon=True).start()

print("Creator Growth Suite dashboard: http://127.0.0.1:8765")
print("Current repo is the only source of truth.")
http.server.ThreadingHTTPServer(("127.0.0.1",8765),H).serve_forever()
