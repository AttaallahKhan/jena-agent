import datetime
import os, re, subprocess, json, sys
from dotenv import load_dotenv
from groq import Groq
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_KEY_1"))

def ask_groq(prompt):
    try:
        memory = load_memory()
        memory_context = json.dumps(memory, ensure_ascii=False, indent=2)
        history_context = json.dumps(get_memory_history(), ensure_ascii=False, indent=2)
        capabilities = load_capabilities()
        capabilities_context = json.dumps(capabilities, ensure_ascii=False, indent=2)

        system_prompt = f"""You are Jena, a female AI assistant.

IMPORTANT USER PREFERENCES:
- User name: AbuSaif.
- Speak only in English or Roman Urdu. Default to Roman Urdu (Latin script) unless the user clearly asks for English.
- Do NOT use traditional Urdu script.
- Do NOT use Hindi, Hinglish, or Devanagari.
- You are female and must use feminine grammar when referring to yourself.
- Treat the following stored memory as persistent user context.
- Do not invent, alter, or omit stored facts when the user asks what you know about them.

STORED MEMORY:
{memory_context}

MEMORY HISTORY:
{history_context}

CAPABILITY REGISTER:
{capabilities_context}

Capability rules:
- When asked what you can do, inspect the Capability Register first.
- Only claim capabilities listed in the register.
- Respect each capability's status: WORKING, PARTIALLY_WORKING, or NOT_IMPLEMENTED.
- Never invent capabilities based on general AI knowledge.
- If a capability is NOT_IMPLEMENTED, clearly say it is not implemented.
- If a capability is PARTIALLY_WORKING, explain the actual limitation briefly.
- The Capability Register describes Jena's actual implemented capabilities, not the general abilities of the underlying Groq model.

Memory history contains previous versions of facts. Use it when the user asks about previous, changed, or forgotten information. Do not treat old values as current values unless the user specifically asks about history.

When the user asks what you know about them, clearly list the relevant stored memories.
When answering normally, naturally follow all applicable saved preferences.
"""

        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Groq error: {e}"

BASE=os.path.expanduser("~/jena-agent")
MEMORY_FILE = os.path.join(BASE, "memory", "knowledge.json")
AGENT=os.path.join(BASE,"agent.py")
YELLOW="\033[93m"; WHITE="\033[97m"; CYAN="\033[96m"; RESET="\033[0m"; BOLD="\033[1m"; GREEN="\033[92m"
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
def startup_ui():
    print(f"{CYAN}{BOLD}")
    print("        ✦  J E N A  A I  ✦")
    print("            A G E N T")
    print(f"{WHITE}        AbuSaif's Assistant{RESET}")
    print(f"{WHITE}      Small Prompts • Real Progress{RESET}")
    print()
    say(f"Model: {MODEL}")
    say(f"Key: {'✅' if get_groq_key() else '❌'}")
    say("Welcome, AbuSaif. Jena is ready. 🤖")
    say("How can I help you today?")
    print()

CAPABILITIES_FILE = os.path.join(BASE, "memory", "capabilities.json")

def load_capabilities():
    try:
        with open(CAPABILITIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {"capabilities": {}}
    except Exception:
        return {"capabilities": {}}

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def load_history():
    history_file = os.path.join(BASE, "memory", "history.json")
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {"history": []}
    except Exception:
        return {"history": []}

def get_memory_history(key=None):
    history = load_history().get("history", [])
    if key is None:
        return history
    return [item for item in history if item.get("key") == key]

def save_memory(key, value):
    memory = load_memory()
    old_value = memory.get(key)

    if old_value is not None and old_value != value:
        history_file = os.path.join(BASE, "memory", "history.json")
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {"history": []}

        history.setdefault("history", []).append({
            "version": len(history["history"]) + 1,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "key": key,
            "old_value": old_value,
            "new_value": value
        })

        tmp_history = history_file + ".tmp"
        with open(tmp_history, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        os.replace(tmp_history, history_file)

    memory[key] = value

    tmp = MEMORY_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
    os.replace(tmp, MEMORY_FILE)

def remember(key, value):
    save_memory(key, value)
    say(f"{GREEN}🧠 Yaad rakh liya: {key}{RESET}")

def handle_memory(text):
    t = text.lower().strip()

    memory_triggers = [
        "remember", "yaad rakh", "yaad rakho", "yaad rakhna",
        "don't forget", "do not forget", "save this", "save that",
        "keep this in memory", "memory mein"
    ]

    if not any(trigger in t for trigger in memory_triggers):
        return False

    intent_prompt = f"""Determine whether the user wants Jena to permanently remember information.

Return ONLY a valid JSON object:
{{"save_memory": true}} or {{"save_memory": false}}

Set save_memory=true when the user is asking to remember, save, retain, or not forget a permanent personal fact or preference, even if expressed naturally in any language.

Set save_memory=false for normal conversation, questions, temporary information, or casual statements.

User message:
{text}
"""

    try:
        intent_response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": intent_prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )

        intent = json.loads(intent_response.choices[0].message.content)

        if not intent.get("save_memory", False):
            return False

    except Exception:
        return False

    prompt = f"""Extract only the permanent user preferences or facts from this request.

Return ONLY a valid JSON object.
Use short snake_case keys.
Values must be strings or booleans.
Do not add markdown, explanation, or any text outside JSON.

User request:
{text}
"""

    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )

        data = json.loads(r.choices[0].message.content)

        if not isinstance(data, dict):
            return False

        for key, value in data.items():
            remember(key, value)

        say("🤖 Jena: Ji, yaad rakhungi.")
        return True

    except Exception as e:
        say(f"❌ Memory error: {e}")
        return True
def time_batao():
    import datetime
    now = datetime.datetime.now().strftime("%I:%M %p, %d %B %Y")
    say(f"Time hai: {now}")

def main():
    startup_ui()
    while True:
        try:
            ui=input(f"{YELLOW}{BOLD}👤 AbuSaif: {RESET}{YELLOW}").strip()
            print(RESET,end="")
        except: break
        if not ui: continue
        if ui.lower() in ["exit","q"]: break
        if handle_intent(ui): continue
        if handle_memory(ui): continue
        if "push" in ui.lower():
            os.chdir(BASE); run("git add. 2>/dev/null"); say(run('git commit -m "Jena v1.2" 2>&1')); say(run("git push origin master 2>&1")); continue
        say("🤖 Jena: " + ask_groq(ui))


# M2 — Permanent Memory
MEMORY_FILE = os.path.join(BASE, "memory", "knowledge.json")

if __name__ == "__main__":
    main()
