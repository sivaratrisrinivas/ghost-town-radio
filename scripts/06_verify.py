"""Code evals on extracted facts. Usage: 06_verify.py dev|heldout. Writes data/facts_verified_<split>.json and evals/verify_<split>.json"""
import json,re,sys,collections
from rapidfuzz import fuzz
from common import *
meta=load_meta(); texts={i:norm(doc_text(m)) for i,m in meta.items()}
cnt=collections.Counter(w for t in texts.values() for w in re.findall(r"[a-z]{3,}",t.lower()))
VOCAB={w for w,c in cnt.items() if c>=8}|set("a an as at be by do go he if in is it me my no of on or so to up us we am i".split())
def readable(q):
    t=re.findall(r"[A-Za-z']+",q)
    return bool(t) and "|" not in q and sum(w.lower() in VOCAB for w in t)/len(t)>=0.85
def snap(f):
    """If the LLM silently 'fixed' OCR, replace its quote with the closest real span from the source. Verbatim by construction."""
    q=norm(f["quote"]); T=texts[f["source_id"]]
    a=fuzz.partial_ratio_alignment(q,T)
    if a is None or a.score<90: return None
    s,e=a.dest_start,a.dest_end
    while s>0 and T[s-1]!=" ": s-=1
    while e<len(T) and T[e]!=" ": e+=1
    return T[s:e]
NUMW=set("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand first second third fourth fifth tenth twice double half".split())
def grounded(claim,quote):
    """Error-discovery finding: claims added names/numbers not in the quote. Every non-initial capitalized word and every number word in the claim must appear (fuzzily, for OCR) in the quote."""
    qt=[w.lower() for w in re.findall(r"[A-Za-z']+",quote)]
    ct=re.findall(r"[A-Za-z']+",claim)
    for i,w in enumerate(ct):
        if (i>0 and w[0].isupper()) or w.lower() in NUMW:
            if not any(fuzz.ratio(w.lower(),t)>=80 for t in qt): return False
    return True
def checks(f):
    r={}
    r["schema_ok"]=all(isinstance(f.get(k),str) for k in ("claim","quote","theme")) and f.get("theme") in ("mining","nightlife","crime","weather","commerce","community","travel","news")
    if not r["schema_ok"]:
        f=dict(f,claim=str(f.get("claim","")),quote=str(f.get("quote","")))
    r["has_source_id"]=f.get("source_id") in meta
    q=norm(f.get("quote",""))
    r["has_quote"]=bool(q)
    r["quote_readable"]=readable(q)
    r["quote_verbatim"]=bool(q) and r["has_source_id"] and q in texts[f["source_id"]]
    w=len(q.split()); r["quote_len_ok"]=8<=w<=45
    claim=f.get("claim","")
    nums=re.findall(r"\d[\d,.]*",claim)
    r["claim_numbers_in_quote"]=all(n.strip(".,") in q for n in nums)
    r["claim_grounded"]=grounded(claim,q)
    r["claim_ok_len"]=3<=len(claim.split())<=45
    return r
if __name__=="__main__":
    sp=sys.argv[1]; raw=json.load(open(f"data/facts_raw_{sp}.json")); ok=[];fails=[];n=len(raw)
    tot={}
    raw_ok_verbatim=0;snapped=0
    for f in raw:
        r=checks(f)
        for k,v in r.items(): tot[k]=tot.get(k,0)+v
        raw_ok_verbatim+=r["quote_verbatim"]
        if not r["quote_verbatim"] and r["has_source_id"] and r["schema_ok"]:
            nq=snap(f)
            if nq: f=dict(f,quote=nq,snapped=True); r=checks(f); snapped+=r["quote_verbatim"]
        if all(r.values()): ok.append(f)
        else: fails.append({"fact_id":f["fact_id"],"failed":[k for k,v in r.items() if not v],"quote":f.get("quote","")[:160]})
    res={"split":sp,"raw_facts":n,"passing_all":len(ok),"pct_raw_llm_quote_verbatim":round(100*raw_ok_verbatim/n,1),"snapped_to_source":snapped,
         "pct_pass_all":round(100*len(ok)/n,1) if n else None,"per_check_pct":{k:round(100*v/n,1) for k,v in tot.items()},"fail_examples":fails[:25]}
    json.dump(ok,open(f"data/facts_verified_{sp}.json","w"),indent=1); json.dump(res,open(f"evals/verify_{sp}.json","w"),indent=1)
    print({k:v for k,v in res.items() if k!="fail_examples"})
