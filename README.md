# Introduction  
If you want to do deep learning by speech, you will need this tool.  
This tool helps to make speech preprocessing convenient.  
- from *.pcm file to *.wav file  
- Resampling all *.wav file  
- Creating noisy speech using clean speech and noise. (You can set the SNR level you want!)  
#
# Requirements  
numpy  
scipy  
wave  
librosa 0.7.2 (with numba 0.48.0)  
natsort  
#
# Usage  
You must to have clean speech folder and noise sound folder with path.  
Don't worry about anything else.  
  
  
1. pcm2wav.py (If you have *.pmc sound file, You can convert to *.wav file from *.pcm file)  
   This result is 16bit wav sound file, Therefore, additional resampling, nomalize process may be required.  
```
python pmc2wav.py --load_path ./pcm_speech --save_path ./wav_speech
```
  
  
2. resample.py (sound resample module)
```
python resample.py --bp ./original 
                   --sp ./datasets/speech 
                   --sn clean 
                   --os 16000 
                   --ts 16000 
                   --op librosa
```
  
  
3. mixture.py (Create Noisy speech file, Noisy = Clean + Noise with SND option)  
   If you just enter the options you want, this tool takes care of everything.  
```
python mixture.py --cp ./datasets_original/test_clean/
                  --np ./datasets_original/test_noise/
                  --sp ./datasets/mainsets
                  --nn test_noisy 
                  --cn test_clean 
                  --SNR 1 
                  --os 16000
                  --ts 16000 
                  --length 16384 
                  --iter 1
                  --sub 100000000
```
