import os, re, subprocess, json, sys
BASE=os.path.expanduser("~/jena-agent")
AGENT=os.path.join(BASE,"agent.py")
YELLOW="\033[93m"; WHITE="\033[97m"; RESET="\033[0m"; BOLD="\033[1m"; GREEN="\033[92m"
def run(c): return subprocess.getoutput(c)
def say(m): print(f"{WHITE}{m}{RESET}")
def load_env():
    env_path=os.path.join(BASE,".env")
    if not os.path.exists(env_path): return
    with open(env_path) as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1)
            os.environ[k.strip()]=v.strip().strip('"').strip("'")
load_env()
def get_groq_key():
    for k in ["GROQ_API_KEY","GROQ_API","GROQ_KEY_1","GROQ_KEY_2","GROQ_KEY"]:
        if os.environ.get(k): return os.environ.get(k)
    for k,v in os.environ.items():
        if "GROQ" in k and "gsk_" in v: return v
    return None
def handle_intent(text):
    t=text.lower()
    if "time" in t and "bata" in t:
        if "time_batao" in globals():
            time_batao()
            return True
        else:
            auto_learn("time batao, current time and date batana, function name time_batao")
            return True
    return False
def auto_learn(skill_desc):
    groq_key=get_groq_key()
    if not groq_key:
        say("❌ GROQ key nahi mili")
        return
    say(f"{GREEN}🧠 Groq {MODEL} se '{skill_desc}' seekh rahi hun...{RESET}")
    try:
        import requests
        prompt=f"Write ONLY ONE python function. Use say() not print. Skill: {skill_desc}. Example: def time_batao():\n import datetime\n now=datetime.datetime.now().strftime(\"%I:%M %p, %d %B %Y\")\n say(f\"Time hai: {{now}}\")"
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type":"application/json"},
            json={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0.3}, timeout=20)
        j=r.json()
        if "choices" not in j:
            say(f"Groq error: {j}")
            return
        code=j['choices'][0]['message']['content']
        code=re.sub(r'```python|```','',code).strip()
        m=re.search(r'(def\s+\w+\(\):.*)', code, re.DOTALL)
        if m: code=m.group(1)
        say(f"{WHITE}Ye seekha:\n{GREEN}{code}{RESET}")
        import importlib.util
        spec=importlib.util.spec_from_file_location("self_editor", f"{BASE}/tools/self_editor.py")
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if mod.safe_edit("append", code):
            say("✅ Seekh liya! Restart...")
            os.execv(sys.executable, [sys.executable, AGENT])
    except Exception as e:
        say(f"❌ Error: {e}")

MODEL="groq/compound-mini"
print(f"{WHITE}{BOLD}🤖 Jena v1.2 - Model: {MODEL}{RESET}")
say(f"Key: {'✅' if get_groq_key() else '❌'}")
say("Bolo: 'jena time batao'")
while True:
    try:
        ui=input(f"{YELLOW}{BOLD}👤 AbuSaif: {RESET}{YELLOW}").strip()
        print(RESET,end="")
    except: break
    if not ui: continue
    if ui.lower() in ["exit","q"]: break
    if handle_intent(ui): continue
    if "push" in ui.lower():
        os.chdir(BASE); run("git add. 2>/dev/null"); say(run('git commit -m "Jena v1.2" 2>&1')); say(run("git push origin master 2>&1")); continue
    say("Bolo 'jena time batao'")


# [Jena self-edit 2026-09-16 09:10:23.342045]
def time_batao():
    import datetime
    now = datetime.datetime.now().strftime("%I:%M %p, %d %B %Y")
    say(f"Time hai: {now}")
