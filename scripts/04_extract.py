"""LLM fact extraction (Groq free tier, gpt-oss-120b). Every call cached on disk. Usage: 04_extract.py dev|heldout|all"""
import json,os,sys,time,hashlib,requests
from common import *
PROMPT_VERSION="v2"
MODEL=os.environ.get("GTR_MODEL","openai/gpt-oss-120b")
SYS="""You extract checkable facts from OCR of an 1879-1880 newspaper from Bodie, California.
Rules:
1. Output JSON only: {"facts":[{"claim":str,"quote":str,"theme":str}]}. At most 3 facts. Return {"facts":[]} if the passage has no clear, readable fact.
2. "quote" must be copied CHARACTER FOR CHARACTER from the passage: one contiguous span, 8 to 45 words, readable (no garbled OCR). Do not fix spelling or punctuation. Do not join separate spans.
3. "claim" is ONE plain sentence in modern English that says only what the quote says. Use no outside knowledge. Do not add names, numbers, places or causes that are not in the quote. If the quote is ambiguous, skip it.
4. "theme" is one of: mining, nightlife, crime, weather, commerce, community, travel, news.
5. Prefer concrete facts about Bodie life: people, prices, events, places, numbers."""
if not LEGACY:
    _c=town_cfg()
    SYS=SYS.replace("OCR of an 1879-1880 newspaper from Bodie, California","OCR of an old book about "+_c["sys"]).replace("about Bodie life","about life in "+_c["name"])
    PROMPT_VERSION="v2-"+TOWN
cache_dir="data/llm_cache"; os.makedirs(cache_dir,exist_ok=True)
GEM="gemini-3.5-flash-lite"
def gemini(passage):
    k=open("/workspace/.secrets/gemini_key").read().strip()  # read into memory only, never printed
    for attempt in range(6):
        r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{GEM}:generateContent",headers={"x-goog-api-key":k},
            json={"systemInstruction":{"parts":[{"text":SYS}]},"contents":[{"parts":[{"text":"PASSAGE:\n"+passage}]}],
                  "generationConfig":{"temperature":0,"responseMimeType":"application/json"}},timeout=(10,90))
        if r.status_code in (429,500,503): time.sleep(15); continue
        r.raise_for_status()
        try: return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
        except Exception: return {"facts":[],"parse_error":True}
    raise SystemExit("gemini free quota exhausted (stopping, never adding billing)")
_groq_dead=os.environ.get("LLM")=="gemini"
def call(passage):
    global _groq_dead
    key=hashlib.sha256((PROMPT_VERSION+MODEL+SYS+passage).encode()).hexdigest()
    f=f"{cache_dir}/{key}.json"
    if os.path.exists(f): return json.load(open(f))
    k0=hashlib.sha256((PROMPT_VERSION+'openai/gpt-oss-120b'+SYS+passage).encode()).hexdigest()
    if os.path.exists(f'{cache_dir}/{k0}.json'): return json.load(open(f'{cache_dir}/{k0}.json'))
    gkey=hashlib.sha256((PROMPT_VERSION+GEM+SYS+passage).encode()).hexdigest(); gf=f"{cache_dir}/{gkey}.json"
    if os.path.exists(gf): return json.load(open(gf))
    if _groq_dead:
        d=gemini(passage); d["model"]=GEM; json.dump(d,open(gf,"w")); return d
    for attempt in range(8):
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":"Bearer "+os.environ["GROQ_API_KEY"]},
            json={"model":MODEL,"temperature":0,"response_format":{"type":"json_object"},"reasoning_effort":"low",
                  "messages":[{"role":"system","content":SYS},{"role":"user","content":"PASSAGE:\n"+passage}]},timeout=(10,60))
        if r.status_code==429 and "tokens per day" in r.text and os.environ.get("GTR_MODEL"): raise SystemExit("model daily quota exhausted: "+MODEL)
        if r.status_code==429:
            if "tokens per day" in r.text and not os.environ.get("GTR_MODEL"): _groq_dead=True; d=gemini(passage); d["model"]=GEM; json.dump(d,open(gf,"w")); return d
            time.sleep(float(r.headers.get("retry-after",10))+1); continue
        if r.status_code>=500: time.sleep(5); continue
        r.raise_for_status()
        txt=r.json()["choices"][0]["message"]["content"]
        try: d=json.loads(txt)
        except Exception: d={"facts":[],"parse_error":True}
        json.dump(d,open(f,"w")); return d
    raise SystemExit("rate limit exhausted (stopping, never adding billing)")
if __name__=="__main__":
    which=sys.argv[1]
    PS=[p for p in json.load(open(P("passages.json"))) if which=="all" or p["split"]==which]
    meta=load_meta(); out=[]
    for n,p in enumerate(PS):
        d=call(p["text"]); 
        for k,f in enumerate(d.get("facts",[])):
            out.append({"fact_id":f"{p['pid']}-f{k}","source_id":p["doc"],"split":p["split"],"claim":f.get("claim",""),"quote":f.get("quote",""),"theme":f.get("theme",""),"passage_id":p["pid"]})
        if n%20==0: print(n,len(PS),len(out),flush=True)
    json.dump(out,open(P(f"facts_raw_{which}.json"),"w"),indent=1); print("raw facts",len(out))
