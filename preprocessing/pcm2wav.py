import os, argparse
import wave, natsort
import numpy as np
from tqdm import tqdm

import scipy
import scipy.signal
import scipy.io.wavfile
import librosa

class pcm2wav ():
    """
    *.pcm 파일을 *.wav 파일로 변환하는 모듈들
    1. 이 모듈을 이용해서 *.pcm파일을 *.wav 파일로 변환하면 float32가 아닌 int16 형으로 바뀜
    2. 그래서 *.wav 파일을 리로드하면 int16으로 바뀌고 librosa.load(파일 경로, sr = 16000) 옵션을 다시 권장
    3. librosa.load 메서드는 *.wav 파일을 불러와서 동시에 sr = 지정한 값으로 자동 Resampling and Normalize
    """
    def __init__ (self, load_path = "./korean_corpus", save_path = "./datasets/clean"):
        self.load_path     = load_path
        self.save_path     = save_path
        self.make_folder()
        self.pcm_directory = self.read_directory()


    def make_folder (self):
        if not(os.path.isdir(self.save_path)):
            os.makedirs(self.save_path)
            print(str(self.save_path) + " 폴더 경로 생성 완료")


    def read_directory (self):
        pcm_folder_name = []
        pcm_file_list   = []

        for file in os.listdir(self.load_path):
            pcm_folder_name.append(load_path + "/" + str(file))
        print(load_path + " 이하의 폴더를 모두 불러오기 완료")

        for name in pcm_folder_name:
            for file in os.listdir(name):
                if file.endswith(".pcm"):
                    pcm_file_list.append(name + "/"+ file)
        print(load_path + " 이하 폴더들의 모든 *.pcm 파일 불러오기 완료")
        
        return pcm_file_list


    # The parameters are prerequisite information. More specifically,
    # channels, bit_depth, sampling_rate must be known to use this function.
    def start (self, channels = 1, bit_depth = 16, sampling_rate = 16000):

        for index, pcm_file_path in tqdm(enumerate (self.pcm_directory)):
            # Check if the options are valid.
            if bit_depth % 8 != 0:
                raise ValueError("bit_depth "+str(bit_depth)+" must be a multiple of 8.")

            pcm_file_name = os.path.splitext(os.path.basename(pcm_file_path))[0]
            wav_file_path = self.save_path + "/" + str(pcm_file_name) + ".wav"
                
            # Read the .pcm file as a binary file and store the data to pcm_data
            with open(pcm_file_path, 'rb') as opened_pcm_file:
                pcm_data  = opened_pcm_file.read()
                
                obj2write = wave.open(wav_file_path, 'wb')
                obj2write.setnchannels(channels )
                obj2write.setsampwidth(bit_depth // 8)
                obj2write.setframerate(sampling_rate)
                obj2write.writeframes(pcm_data)
                obj2write.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'SETTING PATH')
    parser.add_argument("--load_path", type = str, default = "./korean_corpus",  help = "Input load_path (for *.pcm file")
    parser.add_argument("--save_path", type = str, default = "./datasets/clean", help = "Input save_path (for *.wav file")
    args = parser.parse_args()

    load_path       = args.load_path
    save_path       = args.save_path
    pcm2wav_factory = pcm2wav(load_path=load_path, save_path=save_path)
    pcm2wav_factory.start()
    print("-- THe END --")
