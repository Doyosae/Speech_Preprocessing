# Introduction  
If you want to do deep learning by speech, you will need this tool.  
This tool helps to make speech preprocessing convenient.  
#
# Requirements  
numpy  
scipy  
wave  
librosa 0.7.2  
natsort  
#
# Usage  
You must to have clean speech folder and noise sound folder with path.  
Don't worry about anything else.  
  
1. mixture.py (Create Noisy speech file, Noisy = Clean + Noise with SND option)  
If you just enter the options you want, this tool takes care of everything.  
```
python mixture.py --clean_path ./original/test_clean
                  --noise_path ./original/test_noise
                  --save_path ./datasets 
                  --noisy_name test_noisy 
                  --clean_name test_clean 
                  --SNR 1 
                  --os 16000
                  --ts 16000 
                  --length 16384 
                  --iter 1
```
  
  
2. pcm2wav.py (If you have *.pmc sound file, You can convert to *.wav file from *.pcm file)
   This result is 16bit wav sound file, Therefore, additional resampling, nomalize process may be required.
```
python pmc2wav.py --load_path ./pcm_speech --save_path ./wav_speech
```
  
  
3. resample.py (sound resample module)
```
python resample.py --base_path ./original --save_path ./datasets/speech --save_name clean --os 16000 --ts 16000 --op librosa
```
