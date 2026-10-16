"""Render every line with Kokoro (local). Cached by text hash. Writes site/data/broadcast.json with audio paths + durations."""
import json,os,hashlib,subprocess,sys,soundfile as sf,numpy as np
sys.path.insert(0,"/workspace/vo"); os.chdir("/workspace/ghost-town-radio")
from kokoro_onnx import Kokoro
VOICE="am_onyx";SPEED=0.9
k=Kokoro("/workspace/vo/kokoro-v1.0.onnx","/workspace/vo/voices-v1.0.bin")
B=json.load(open("data/broadcast_text.json")); os.makedirs("site/audio/lines",exist_ok=True)
sr=24000;n=0
for H in B["hours"]:
    for l in H["lines"]:
        if l["type"]=="silence": l["audio"]=None;l["dur"]=3.5;continue
        h=hashlib.md5((VOICE+str(SPEED)+l["text"]).encode()).hexdigest()[:10]
        f=f"site/audio/lines/{h}.mp3"
        if not os.path.exists(f):
            s,r=k.create(l["text"],voice=VOICE,speed=SPEED,lang="en-us")
            sf.write("/tmp/l.wav",s,r)
            subprocess.run(["ffmpeg","-v","error","-y","-i","/tmp/l.wav","-af","silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,loudnorm=I=-16:TP=-1.5","-ar","24000","-ac","1","-b:a","32k",f],check=True)
            n+=1
        l["audio"]="audio/lines/"+h+".mp3"
        l["dur"]=round(float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f])),2)
    print("hour",H["hour"],"done",n,flush=True)
json.dump(B,open("site/data/broadcast.json","w"),indent=1)
print("total minutes",sum(l["dur"] for H in B["hours"] for l in H["lines"])/60)
