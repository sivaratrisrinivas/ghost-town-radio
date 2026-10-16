"""Code evals on extracted facts. Usage: 06_verify.py dev|heldout. Writes data/facts_verified_<split>.json and evals/verify_<split>.json"""
import json,re,sys
from common import *
meta=load_meta(); texts={i:norm(doc_text(m)) for i,m in meta.items()}
def checks(f):
    r={}
    r["has_source_id"]=f.get("source_id") in meta
    q=norm(f.get("quote",""))
    r["has_quote"]=bool(q)
    r["quote_verbatim"]=bool(q) and r["has_source_id"] and q in texts[f["source_id"]]
    w=len(q.split()); r["quote_len_ok"]=8<=w<=45
    claim=f.get("claim","")
    nums=re.findall(r"\d[\d,.]*",claim)
    r["claim_numbers_in_quote"]=all(n.strip(".,") in q for n in nums)
    r["claim_ok_len"]=3<=len(claim.split())<=45
    return r
if __name__=="__main__":
    sp=sys.argv[1]; raw=json.load(open(f"data/facts_raw_{sp}.json")); ok=[];fails=[];n=len(raw)
    tot={}
    for f in raw:
        r=checks(f)
        for k,v in r.items(): tot[k]=tot.get(k,0)+v
        if all(r.values()): ok.append(f)
        else: fails.append({"fact_id":f["fact_id"],"failed":[k for k,v in r.items() if not v],"quote":f.get("quote","")[:160]})
    res={"split":sp,"raw_facts":n,"passing_all":len(ok),"pct_verbatim":round(100*tot["quote_verbatim"]/n,1) if n else None,
         "pct_pass_all":round(100*len(ok)/n,1) if n else None,"per_check_pct":{k:round(100*v/n,1) for k,v in tot.items()},"fail_examples":fails[:25]}
    json.dump(ok,open(f"data/facts_verified_{sp}.json","w"),indent=1); json.dump(res,open(f"evals/verify_{sp}.json","w"),indent=1)
    print({k:v for k,v in res.items() if k!="fail_examples"})
