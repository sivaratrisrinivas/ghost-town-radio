"""Fetch OCR text for the book sources of a non-Bodie town from the Internet Archive. Cached. Polite 1 req/1.5s.
License rule: the IA item must be pre-1931 (US public domain by age) or carry an explicit public domain mark. The license string says which."""
import json,os,time,requests
from common import *
UA={"User-Agent":"GhostTownRadio/0.1 (research project; github.com/sivaratrisrinivas)"}
cfg=town_cfg(); os.makedirs(P("corpus"),exist_ok=True); meta=[]
for ident in cfg["ids"]:
    m=requests.get(f"https://archive.org/metadata/{ident}",headers=UA,timeout=90).json(); md=m["metadata"]; time.sleep(1.5)
    year=str(md.get("date",""))[:4]
    assert year.isdigit() and int(year)<=1930,(ident,year)
    names=[x["name"] for x in m["files"] if x["name"].endswith("_djvu.txt")]
    f=P(f"corpus/{ident}.txt")
    if not os.path.exists(f):
        r=requests.get(f"https://archive.org/download/{ident}/{names[0]}",headers=UA,timeout=300); r.raise_for_status(); open(f,"w").write(r.text); time.sleep(1.5)
    pdm="publicdomain/mark" in str(md.get("licenseurl",""))
    lic=("Public Domain Mark 1.0, declared on the Internet Archive item" if pdm else f"Public domain by age: published {year}, before 1931. The Internet Archive item has no rights statement")
    t=md["title"] if isinstance(md["title"],str) else md["title"][0]
    cr=md.get("creator","");cr=cr if isinstance(cr,str) else ", ".join(cr)
    meta.append({"id":ident,"title":t.strip(),"creator":cr,"date":f"{year}-01-01","url":f"https://archive.org/details/{ident}","license":lic,"text_file":f,"chars":len(open(f).read())})
json.dump(meta,open(P("corpus_meta.json"),"w"),indent=1); print(len(meta),sum(m["chars"] for m in meta))
