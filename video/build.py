import json,os,subprocess,asyncio,time,hashlib,sys
import numpy as np,soundfile as sf
os.chdir("/workspace/outreach/gtr2"); os.makedirs(".",exist_ok=True); G="/workspace/ghost-town-radio/docs/"
sys.path.insert(0,"/workspace/vo")
LINES=[
("why","Most AI history tools sound sure of themselves, and you cannot tell what is real. So I built a radio station that is not allowed to guess."),
("what","This is Ghost Town Radio. It began with Bodie, California. Now it also tunes Bangalore, Coorg, Hyderabad and Mumbai, from public domain newspapers, gazetteers and books."),
("towns","Pick a town with these buttons. Each town has its own sources, its own schedule, and its own silent hours."),
("knob","Turn the dial to pick an hour. It works by touch, mouse, or keyboard."),
("play","Press play. The D J is fictional. But look at the card. Every line shows the exact quote, and a link to the page."),
("dj",None),
("verb","The quote is word for word, typos and all. A code check rejects any quote that is not in the source."),
("quiet","Some hours are silent. When the archive has nothing, the D J says nothing."),
("nums","Across the five towns, one hundred twenty claims are on air, and every quote passes the code check. I read the new ones by hand, and threw out eighteen of one hundred fourteen that did not hold up."),
("end","It is open source, and the link is below. Ghost Town Radio."),
]
# narrator TTS (af_heart, local Kokoro)
from kokoro_onnx import Kokoro
k=Kokoro("/workspace/vo/kokoro-v1.0.onnx","/workspace/vo/voices-v1.0.bin")
sr=48000; clips={}
for key,t in LINES:
    if not t: continue
    f=f"{key}.wav"
    if not os.path.exists(f):
        s,r=k.create(t,voice="af_heart",speed=0.95,lang="en-us"); sf.write("raw_"+f,s,r)
        subprocess.run(["ffmpeg","-v","error","-y","-i","raw_"+f,"-af","silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse","-ar",str(sr),"-ac","1",f],check=True)
    a,_=sf.read(f,dtype="float32"); clips[key]=a
B=json.load(open(G+"data/mumbai/broadcast.json")); L=B["hours"][17]["lines"]
dj=[l for l in L if l["id"].startswith("in.ernet.dli.2015.35213-p20-f0")]
djaud=[]
for l in dj:
    subprocess.run(["ffmpeg","-v","error","-y","-i",G+l["audio"],"-ar",str(sr),"-ac","1","dj_"+l["type"]+".wav"],check=True)
    djaud.append(sf.read("dj_"+l["type"]+".wav",dtype="float32")[0])
# timeline
GAP=0.55;t=0.6;tl={};caps=[]
for key,txt in LINES:
    if key=="dj":
        tl["dj"]=t; d=len(djaud[0])/sr+0.45+len(djaud[1])/sr; tl["dj_q"]=t+len(djaud[0])/sr+0.45; t+=d+0.8; continue
    tl[key]=t; d=len(clips[key])/sr; caps.append((t,t+d,txt)); t+=d+GAP
total=t+0.8; print("total",total,tl)
buf=np.zeros(int(total*sr)+sr,np.float32)
for key,a in clips.items(): i=int(tl[key]*sr); buf[i:i+len(a)]+=a
for st,a in ((tl["dj"],djaud[0]),(tl["dj_q"],djaud[1])): i=int(st*sr); buf[i:i+len(a)]+=a*0.9
sf.write("mix_raw.wav",buf,sr)
subprocess.run(["ffmpeg","-v","error","-y","-i","mix_raw.wav","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-ar","48000","mix.wav"],check=True)
# captions (SRT). DJ lines get DJ captions from the real card text.
F=json.load(open(G+"data/mumbai/facts.json")); fid=dj[0]["fact_id"]
def srt(x): h=int(x//3600);m=int(x%3600//60);s=x%60; return f"{h:02}:{m:02}:{s:06.3f}".replace(".",",")
caps.append((tl["dj"],tl["dj"]+len(djaud[0])/sr,"DJ Hollis Vane (fictional): "+F[fid]["claim"]))
caps.append((tl["dj_q"],tl["dj_q"]+len(djaud[1])/sr+0.6,"Quote: \u201c"+F[fid]["quote"]+"\u201d"))
caps.sort()
open("caps.srt","w").write("".join(f"{i+1}\n{srt(a)} --> {srt(b)}\n{tx}\n\n" for i,(a,b,tx) in enumerate(caps)))
json.dump({"tl":tl,"total":total},open("tl.json","w"))
