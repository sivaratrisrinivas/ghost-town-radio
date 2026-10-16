"""Assemble the 24-hour schedule from VERIFIED facts only. Deterministic (seeded). Writes docs/data/*.json"""
import json,random,re,sys
from common import *
meta=load_meta(); cfg=town_cfg()
facts=[]
for sp in (("dev","heldout") if LEGACY else ("all",)):
    try: facts+=json.load(open(P(f"facts_final_{sp}.json")))
    except FileNotFoundError: pass
rng=random.Random(1879)
HOURS=[("nightlife","Midnight at the saloons",0),("mining","Night shift",3),("crime","Trouble after dark",1),("weather","The cold before dawn",0),("mining","Before the whistle",3),("mining","First shift",3),("mining","Mines and mills",3),("commerce","Morning trade",2),("commerce","Prices and goods",2),("community","Church bells and schools",1),("news","Word from outside",1),("mining","Late morning, the shafts",3),("community","Noon, the town talks",1),("mining","Afternoon shift",3),("nightlife","Afternoon, no word on the saloons",0),("news","News by wire",1),("mining","Down the tunnels",3),("community","Supper hour",1),("mining","Evening shift",3),("news","The county and the capital",1),("nightlife","Saloon hour",0),("news","The business of government",1),("mining","Night work",3),("news","The last word",1)]
HOURS2=[("nightlife","Midnight, no word on the nightlife",0),("crime","Trouble and the law",1),("weather","The sky and the seasons",1),("mining","Under the ground",1),("community","Before dawn, the town",1),("travel","Roads and rails",1),("commerce","Early trade",1),("community","Schools and temples",1),("commerce","Markets and prices",1),("community","Morning, the people",2),("news","Word of the day",1),("travel","Late morning, the roads",1),("community","Noon, the town talks",1),("commerce","Afternoon trade",2),("community","Afternoon, the people",1),("news","The government and the record",1),("travel","Distances and routes",1),("community","Supper hour",2),("commerce","Evening trade",1),("community","Lamps and lodges",1),("nightlife","Evening, no word on the nightlife",0),("community","Late evening, the town",1),("commerce","Night accounts",1),("news","The last word",1)]
if not LEGACY: HOURS=HOURS2
NUM=["twelve","one","two","three","four","five","six","seven","eight","nine","ten","eleven"]
def hour_words(h):
    ap="in the morning" if h<12 else "in the evening" if h>=18 else "in the afternoon"
    return f"{NUM[h%12]} o'clock {ap}" if h not in (0,12) else ("midnight" if h==0 else "noon")
MONTHS="January February March April May June July August September October November December".split()
ORD="first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth fourteenth fifteenth sixteenth seventeenth eighteenth nineteenth twentieth twenty-first twenty-second twenty-third twenty-fourth twenty-fifth twenty-sixth twenty-seventh twenty-eighth twenty-ninth thirtieth thirty-first".split()
def spoken_date(d):
    m=re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})",d)
    if not m: return ""
    y,mo,da=map(int,m.groups()); return f"{MONTHS[mo-1]} {ORD[da-1]}, eighteen {['seventy','eighty'][y-1870] if y in (1870,1880)  else ''}".replace("eighteen eighty","eighteen eighty").strip(", ")
ONES="zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS="x x twenty thirty forty fifty sixty seventy eighty ninety".split()
def two(n): return ONES[n] if n<20 else TENS[n//10]+("-"+ONES[n%10] if n%10 else "")
def year_words(y):
    a,b=divmod(y,100)
    return two(a)+(" hundred" if b==0 else (" oh "+ONES[b] if b<10 else " "+two(b)))
def spoken_date(d):
    m=re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})",d); y,mo,da=map(int,m.groups())
    if not LEGACY: return "published in "+year_words(y)
    yr={1879:"eighteen seventy-nine",1880:"eighteen eighty"}.get(y,str(y))
    return f"{MONTHS[mo-1]} {ORD[da-1]}, {yr}"
def short_title(t):
    if not LEGACY: return re.sub(r"\s+"," ",re.sub(r"[^A-Za-z ,'-]"," ",t)).strip()
    return re.sub(r"\s*\d{4}-\d{1,2}-\d{1,2}\s*$","",t).strip()
OPEN=["Ghost Town Radio. Hollis Vane, with you at {t}.","This is Hollis Vane, {t}, on Ghost Town Radio.","{t}, and the dial is still warm. Hollis Vane here."]
INTRO={"nightlife":"Let us see what the papers said about the evenings.","crime":"Let us see what the papers said about trouble.","weather":"Let us see what the papers said about the sky.","mining":"Let us see what the papers said about the mines.","commerce":"Let us see what the papers said about trade.","community":"Let us see what the papers said about the town.","travel":"Let us see what the papers said about the roads.","news":"Let us see what the papers carried from far away."}
LEAD=["Here is what the paper printed.","Now a page from the archive.","Listen to this one.","Another clipping."]
QLEAD=["In the paper's own words.","The words themselves.","Word for word."]
OUTRO=["That is all the archive gives me on that. I will not guess.","Where the paper goes quiet, so do I.","Static for a moment. Stay on the dial."]
SIL=["Nothing in the archive on this hour's subject. So here is silence."]
sources={}
used=set();broadcast=[];used_facts={}
by_theme={}
for f in facts: by_theme.setdefault(f["theme"],[]).append(f)
for v in by_theme.values(): rng.shuffle(v)
for h,(theme,title,quota) in enumerate(HOURS):
    lines=[];pool=by_theme.get(theme,[])
    take=[];
    while pool and len(take)<quota:
        f=pool.pop()
        if f["fact_id"] in used: continue
        take.append(f);used.add(f["fact_id"])
    lines.append({"id":f"h{h}-open","type":"bridge","text":OPEN[h%3].format(t=hour_words(h))+" "+(INTRO[theme] if take else "")})
    if not take: lines.append({"id":f"h{h}-sil","type":"silence","text":""})
    for k,f in enumerate(take):
        m=meta[f["source_id"]]; sources[f["source_id"]]={"creator":m.get("creator",""),"title":m["title"],"date":m["date"],"url":m["url"],"license":m["license"],"license_short":"Public domain"}
        used_facts[f["fact_id"]]=f
        lines.append({"id":f"{f['fact_id']}-c","type":"claim","fact_id":f["fact_id"],"text":f"{LEAD[(h+k)%4]} From {short_title(m['title'])}, {spoken_date(m['date'])}. {f['claim']} {QLEAD[(h+k)%3]}"})
        lines.append({"id":f"{f['fact_id']}-q","type":"quote","fact_id":f["fact_id"],"text":norm(f["quote"]),"speak":re.sub(r"[|{}\[\]~_¢¬]"," ",re.sub(r"(\w)- (\w)",r"\1\2",norm(f["quote"])))})
    lines.append({"id":f"h{h}-out","type":"bridge","text":OUTRO[h%3]})
    broadcast.append({"hour":h,"theme":theme,"title":title,"lines":lines})
json.dump({"station":{"name":"Ghost Town Radio","dj":"Hollis Vane (fictional)","place":cfg["place"]},"hours":broadcast},open(P("broadcast_text.json"),"w"),indent=1)
json.dump({k:{"claim":v["claim"],"quote":norm(v["quote"]),"source_id":v["source_id"]} for k,v in used_facts.items()},open(DOCS("facts.json"),"w"),indent=1)
json.dump(sources,open(DOCS("sources.json"),"w"),indent=1)
print("facts used",len(used_facts),"of",len(facts),"| hours with silence:",sum(1 for H in broadcast if any(l['type']=='silence' for l in H['lines'])))
