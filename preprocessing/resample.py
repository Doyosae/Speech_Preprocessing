import os, argparse
import wave, natsort
import numpy as np
from tqdm import tqdm

import scipy
import scipy.signal
import scipy.io.wavfile
import librosa
"""
원음의 샘플링 레이트를 파악한다.
샘플링 레이트를 설정한다. (VoIP 기준 16,000 sampling rate)
scipy.io.wavfile는 *.wav 파일을 그대로 불러온다. 이 메서드로 sampling rate와 신호를 그대로 읽을 수 있다.
    이 메서드는 normalize - convert2float32 - resampling 모듈로 별도로 전처리를 해야한다.
librosa.load를 이용한다. librosa.load("파일 경로", sr = target_sampling)
    이 메서드는 normalize와 resampling까지 동시에 처리한다.

따라서 권장하는 리샘플링 방법
    "./folder/*.wav" 폴더를 준비 (샘플렝 레이트가 무엇이든 상관 없음)
    librosa.load 메서드로 리샘플링까지 시행
    librosa.output.write_wav 메서드로 새로운 폴더에 저장
    음성 폴더 하나씩 할 것

기본적인 resampling 준비 (class data_dloader)
    "./original/*.wav" (dtype = int16 or int32)
    librosa.load로 normalize, resampling
    "./datasets/*.wav" 형식으로 저장
"""
class resampler ():
    '''
    class dataload
        def load_librosa
        def load_scipy
        def data_normalize
        def data_convert2float32
        def data_split
        def data_resampler

        original_sampling : 원 *.wav 파일의 샘플링 레이트
        target_sampling   : 원하는 샘플링 레이트
        base_file_path : 소리 소스가 저장되어 있는 폴더
        load_file_name : 소리 소스가 있는 폴더에서 어떤 소리의 폴더를 가지고 올 것인지 선택

        save_file_path : 저장하고자 하는 소리의 폴더
        save_file_name : 저장하는 폴더의 해당 데이터 폴더
        save_naming : 그 폴더의 이름

        1. librosa 옵션
            self.load_librosa로부터 -1 ~ 1 사이의 정규화한 resampling 데이터 return
            
        2. scipy 옵션
            self.load_sicpy
            self.data_normalize
            self.data_resampling
            self.data_conver2float32

        3. 가급적이면 데이터의 sampling rate를 미리 알아서 librosa 옵션을 사용할 것
    '''
    def __init__ (self, base_file_path = "./original",
                        save_file_path = "./datasets",
                        save_file_name = "test_clean",
                        original_sampling = 16000,
                        target_sampling = 16000):
        

        def walk_filename (file_path):

            file_list = []

            for root, dirs, files in tqdm(os.walk(file_path)):
                for fname in files:

                    if fname == "desktop.ini" or fname == ".DS_Store": continue 

                    full_fname = os.path.join(root, fname)
                    file_list.append(full_fname)

            file_list = natsort.natsorted(file_list, reverse = False)
            
            return file_list

        self.original_sampling = original_sampling
        self.target_sampling   = target_sampling

        self.file_path = base_file_path
        self.file_list = walk_filename(self.file_path)

        # "./datasets/test_clean"
        self.save_file_path = save_file_path + "/" + save_file_name

        # Check save_file_path -> create folder
        print("Check folder path ::: ", self.save_file_path)
        if not(os.path.isdir(self.save_file_path)): 
            os.makedirs(self.save_file_path)
        

        
    def load_librosa (self):
        """
        librosa_load (wav file to numpy array with normalize, resampling)
        1. load file (Default sampling 22050)
        2. Audio normalization -1 ~ 1
        3. resampling to "self.target_sampling"
        4. 여기서는 원 .wav 파일의 sampling rate가 필요 없음
        """
        for index, data in tqdm(enumerate (self.file_list)):

            sound, sampling_rate = librosa.load(data, sr = self.target_sampling)
            librosa.output.write_wav(self.save_file_path + "/" + "{:07d}".format(index+1) + ".wav", sound, self.target_sampling)
        

    def load_scipy (self, path):
        """
        scipy.io.wavfile.read
        wav file to numpy array
        1. load file (example, data type is in16)
        2. No audio normalization
        3. no resampling
        4. Extract sampling rate and quantization data
        5. You need to normalize data
        """
        sr, sound = scipy.io.wavfile.read(path)
        
        return sound
    

    def data_normalize (self, data):
        """
        If dtype int16, normalize -1 ~ 1
        """
        data = data + (2**15)
        data = data / ((2**16) - 1)
        data = 2 * data
        data = data - 1

        return data
    
    
    def data_resampler (self, data):
        """
        original sampling rate to target sampling rate
        """
        data = librosa.resample(data, orig_sr = original_sampling, target_sr = self.target_sampling)
        
        return data


    def data_convert2float32 (self, data):
        """
        datatype convert to float32
        """
        data = data.astype(np.float32)

        return data


    def save_scipy (self, data):
        scipy.io.wavfile.write(self.save_file_path, sr = self.target_sampling, data = data)


    def data_save (self, option = "librosa"):

        print("Option is ", option)

        if option == "librosa": 
            self.load_librosa()

        elif option == "scipy":

            for index, path in tqdm(enumerate (self.file_list)):

                sound = self.load_scipy(path)
                sound = self.data_normalize(sound)
                sound = self.data_resampler(sound)
                sound = self.data_convert2float32(sound)
                self.save_scipy(sound)

        else: raise "option을 librosa나 scipy 둘 중 하나로 입력하세요."



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = 'SETTING OPTION')
    parser.add_argument("--bp",    type = str, default = "./original",      help = "Input original file path")
    parser.add_argument("--sp",    type = str, default = "./datasets/clean", help = "Input resampling file path")
    parser.add_argument("--sn",    type = str, default = "test_clean",       help = "Input resampling file name")
    parser.add_argument("--os", type = int, default = 16000, help = "Input original sound sampling rate")
    parser.add_argument("--ts", type = int, default = 16000, help = "Input targeting sound sampling rate")
    parser.add_argument("--op", type = str, default = "librosa", help = "Input library factory librosa or scipy")
    args = parser.parse_args()

    base_file_path    = args.bp
    save_file_path    = args.sp
    save_file_name    = args.sn
    original_sampling = args.os
    target_sampling   = args.ts
    option            = args.op
    print(option)

    resampling_factory = resampler(base_file_path = base_file_path,
                                   save_file_path = save_file_path,  
                                   save_file_name = save_file_name,
                                   original_sampling = original_sampling,
                                   target_sampling = target_sampling)
    
    resampling_factory.data_save(option = option)
    print("-- THe END --")