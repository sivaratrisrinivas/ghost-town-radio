"""Code evals on the FINAL broadcast (what listeners hear). Also self-tests the checker on planted failures."""
import json,re,sys
from common import *
meta=load_meta(); texts={i:norm(doc_text(m)) for i,m in meta.items()}
ALLOW={"Ghost","Town","Radio","Hollis","Vane","This","Let","Here","Now","Listen","Another","In","The","Word","That","Where","Static","Stay","Nothing","So","I","And","Bodie"}
def check(B,F,S):
    res=[];claims=0;ok_verb=0;ok_src=0;ok_pair=0;bridge_bad=[]
    for H in B["hours"]:
        for l in H["lines"]:
            if l["type"] in ("claim","quote"):
                f=F.get(l.get("fact_id")); 
                if not f: res.append((l["id"],"no fact")); continue
                src=S.get(f["source_id"]); good_src=bool(src and src["url"].startswith("https://archive.org/details/") and src["license"] and src["date"])
                verb=norm(f["quote"]) in texts.get(f["source_id"],"")
                if l["type"]=="claim":
                    claims+=1; ok_verb+=verb; ok_src+=good_src
                    ok_pair+= f["claim"] in l["text"] and bool(f["quote"])
                    if not verb: res.append((l["id"],"quote not verbatim"))
                else:
                    if norm(l["text"])!=norm(f["quote"]): res.append((l["id"],"spoken quote differs from stored quote"))
            elif l["type"]=="bridge":
                if re.search(r"\d",l["text"]): bridge_bad.append((l["id"],"digit in bridge"))
                caps=[w for w in re.findall(r"\b[A-Z][a-z']+",l["text"]) if w not in ALLOW]
                if caps: bridge_bad.append((l["id"],"unlisted proper noun "+",".join(caps)))
    return {"claims":claims,"pct_quote_verbatim":round(100*ok_verb/max(1,claims),1),"pct_source_ok":round(100*ok_src/max(1,claims),1),
            "pct_claim_text_intact_and_quoted":round(100*ok_pair/max(1,claims),1),"violations":res+bridge_bad}
if __name__=="__main__":
    B=json.load(open("site/data/broadcast.json"));F=json.load(open("site/data/facts.json"));S=json.load(open("site/data/sources.json"))
    r=check(B,F,S); 
    # self-test: planted failures must be caught
    import copy
    F2=copy.deepcopy(F);k=next(iter(F2));F2[k]["quote"]+=" xyzzy invented words"
    B2=copy.deepcopy(B);B2["hours"][0]["lines"][0]["text"]="Bodie had 4000 people."
    t=check(B2,F2,S); r["selftest_caught_fake_quote"]=any("not verbatim" in v[1] for v in t["violations"]); r["selftest_caught_digit_bridge"]=any("digit" in v[1] for v in t["violations"])
    json.dump(r,open("evals/broadcast_eval.json","w"),indent=1); print(json.dumps(r,indent=1)[:1500])
    sys.exit(1 if r["violations"] or not r["selftest_caught_fake_quote"] else 0)
