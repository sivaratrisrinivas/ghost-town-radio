"""Fetch OCR text + metadata for public-domain Bodie newspaper issues. Cached. 1 req/1.5s."""
import json,os,time,requests,re
UA={"User-Agent":"GhostTownRadio/0.1 (research project; github.com/sivaratrisrinivas)"}
hits=json.load(open("data/search_hits.json"))
os.makedirs("data/corpus",exist_ok=True)
meta=[]
for ident,h in sorted(hits.items()):
    t=h.get("title","")
    if not re.search(r"Bodie (Chronicle|Morning News|Standard)|Daily Bodie Standard|Tales of Aurora",t): continue
    rights=h.get("rights","")
    if isinstance(rights,list): rights=" ".join(rights)
    if not rights.lower().startswith("public domain"): print("skip rights",ident,rights[:40]); continue
    f=f"data/corpus/{ident}.txt"
    if not os.path.exists(f):
        m=requests.get(f"https://archive.org/metadata/{ident}",headers=UA,timeout=60).json()
        names=[x["name"] for x in m["files"] if x["name"].endswith("_djvu.txt")]
        if not names: print("no text",ident); continue
        time.sleep(1.5)
        r=requests.get(f"https://archive.org/download/{ident}/{names[0]}",headers=UA,timeout=120)
        r.raise_for_status(); open(f,"w").write(r.text); time.sleep(1.5)
    md=json.load(open("data/search_hits.json"))[ident]
    meta.append({"id":ident,"title":t,"date":h.get("date","")[:10],"url":f"https://archive.org/details/{ident}","license":"Public domain (rights statement: "+rights.strip()+")","text_file":f,"chars":len(open(f).read())})
json.dump(meta,open("data/corpus_meta.json","w"),indent=1)
print(len(meta),sum(m["chars"] for m in meta))
