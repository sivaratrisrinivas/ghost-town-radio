"""Chunk OCR text into passages; score OCR quality; keep best few per doc."""
import json,re,collections
from common import *
meta=load_meta()
docs={i:doc_text(m) for i,m in meta.items()}
cnt=collections.Counter(w for t in docs.values() for w in re.findall(r"[a-z]{3,}",t.lower()))
vocab={w for w,c in cnt.items() if c>=8}|set("a an as at be by do go he if in is it me my no of on or so to up us we am i".split())
KEY=re.compile(r"\b(Bodie|mine|mill|miners?|saloon|stage|Standard|ore|bullion|fire|shot|killed|hotel|school|church|lodge|snow|wind|assay|company|stock|town)\b",re.I)
def quality(p):
    toks=re.findall(r"[A-Za-z']+",p)
    if len(toks)<40: return 0
    good=sum(1 for t in toks if t.lower() in vocab)
    return good/len(toks)
out=[]
for i,t in docs.items():
    paras=[norm(p) for p in re.split(r"\n\s*\n",t)]
    paras=[p for p in paras if len(p)>40]
    wins=[];cur=""
    for p in paras:
        if len(cur)+len(p)>1500 and cur: wins.append(cur);cur=p
        else: cur=(cur+" "+p).strip()
    if cur: wins.append(cur)
    sc=[]
    for w in wins:
        if len(w)<400: continue
        q=quality(w)
        if q<0.78: continue
        sc.append((q+0.02*min(10,len(KEY.findall(w))),w,q))
    sc.sort(reverse=True)
    for k,(s,w,q) in enumerate(sc[:3]):
        out.append({"pid":f"{i}-p{k}","doc":i,"split":split_of(i),"quality":round(q,3),"text":w})
json.dump(out,open("data/passages.json","w"),indent=1)
print(len(out),"passages from",len({o['doc'] for o in out}),"docs;",collections.Counter(o['split'] for o in out))
