"""Locally synthesized period ambience: desert wind + radio hiss + vinyl-like crackle. No samples, license-free. Seamless 30s loop."""
import numpy as np,soundfile as sf,subprocess
sr=24000;n=sr*30;rng=np.random.default_rng(1879)
def fnoise(slope,lo,hi):
    X=np.fft.rfft(rng.standard_normal(n));f=np.fft.rfftfreq(n,1/sr);f[0]=1
    X*=f**(-slope/2)*((f>=lo)&(f<=hi));x=np.fft.irfft(X,n);return x/np.abs(x).max()
wind=fnoise(2,40,900)
lfo=0.55+0.45*np.sin(2*np.pi*np.arange(n)/sr/30*3+1.0)*np.sin(2*np.pi*np.arange(n)/sr/30*5)
wind*=lfo
hiss=fnoise(0,2500,7000)*0.05
crack=np.zeros(n)
for i in rng.choice(n,int(n/sr*9),replace=False):
    L=int(rng.integers(8,60));crack[i:i+L]+=(rng.standard_normal(min(L,n-i))*np.exp(-np.arange(min(L,n-i))/ (L/4)))*rng.uniform(.2,1)
crack=np.roll(crack,0)*0.25
x=wind*0.5+hiss+crack; x=x/np.abs(x).max()*0.6
sf.write("/tmp/amb.wav",x.astype(np.float32),sr)
subprocess.run(["ffmpeg","-v","error","-y","-i","/tmp/amb.wav","-ac","1","-b:a","40k","site/audio/ambience.mp3"],check=True)
