import os
import argparse
import natsort
import wave
import numpy as np

import scipy
import scipy.signal
import scipy.io.wavfile
import librosa

from tqdm import tqdm


"""
Speech Separation 문제를 풀기 위한 데이터
    train
        noisy
        clean
    test
        noisy
        clean

7. 이를 다시 STFT, Mel spectogram, MFCC 등을 통해서 전처리 해야함
    이후에 서술 ... ...
"""


class data_mixture ():
    """
    준비물 : 원하는 target sampling된 clean과 noise

    def __init__    : datasets_source의 test_clean 폴더와 test_noise 폴더에서 음원을 불러온다.
    def data_split  : Speech 음성을 하나 뽑아 split_length 길이에 맞게 자른다.
    (반복 횟수는 곧 데이터의 갯수 iteration이 결정)
    def data_mixing : split clean과 noise를 Loudness normalize를 (-25 dBFS) 하고 SNR 레벨에 맞게 섞는다.
        return noisy, clean
    def data_write  : sound를 저장하는 모듈

    def save

        처리 과정
        1. speech folder의 모든 파일명을 읽어온다.
           noise folder의 모든 파일명을 읽어온다.
        2. speech file name list를 순서대로 하나씩 불러서 split
        3. split speech를 noise file name list에서 noise를 랜덤으로 하나 고르기
            random pick noise, random smaple for split_length
        4. SNR ratio에 맞게 섞기 == return noisy clean
        5. noisy, clean, noise를 저장
        ./datasets/ 폴더에 .npy 형태로 저장 (모델의 학습 데이터로 사용)
        ./datasets/ 폴더에 각 sound 폴더를 만들어서 .wav 파일로 저장
    """
    def __init__ (self, clean_source_path = "./datasets_original/clean",
                        noise_source_path = "./datasets_original/noise",
                        save_file_path = "./datasets",
                        noisy_name = "test_noisy",
                        clean_name = "test_clean",
                        SNR = np.random.randint(0, 5),
                        original_sampling = 16000,
                        target_sampling = 16000,
                        split_length = 16384,
                        iteration = 1):

        def walk_filename (file_path):

            file_list = []

            for root, dirs, files in tqdm(os.walk(file_path)):
                for fname in files:
                    if fname == "desktop.ini" or fname == ".DS_Store":
                        continue 
                    full_fname = os.path.join(root, fname)
                    file_list.append(full_fname)

            file_list = natsort.natsorted(file_list, reverse = False)
            
            return file_list

        def folder_make(folder_path):

            if not(os.path.isdir(folder_path)):
                os.makedirs(folder_path)
                print(str(folder_path) + " 폴더 경로 생성 완료")


        self.clean_source_path = clean_source_path
        self.noise_source_path = noise_source_path
        self.save_file_path = save_file_path
        self.noisy_name = noisy_name
        self.clean_name = clean_name

        self.SNR = SNR
        self.original_sampling = original_sampling
        self.target_sampling = target_sampling
        self.split_length = split_length
        self.iteration = iteration

        self.clean_file_list = walk_filename(self.clean_source_path)
        self.noise_file_list = walk_filename(self.noise_source_path)

        self.clean_file_path = self.save_file_path + "/" + self.clean_name
        self.noisy_file_path = self.save_file_path + "/" + self.noisy_name
        folder_make(self.clean_file_path)
        folder_make(self.noisy_file_path)


        'Load noise_source_sound, clean_source_file'
        self.noise_source = []
        self.clean_source = []

        for _, data in tqdm(enumerate(self.noise_file_list)):
            _, sound = scipy.io.wavfile.read(data)
            self.noise_source.append(sound)
        print("노이즈 소스 메모리 로드 완료")

        for iteration in range(self.iteration):
            self.clean_source.extend(self.clean_file_list)
        print("Interation할 음성 소스 리스트 로드 완료")


    def data_split (self, clean_speech):
        """
        Cut as much as you want from the voice file.
        (sr = 16000 and 48,000 slices 3sec)
        It's about every voice.
        Padding with 0. for the rest of the voice shorter than this
        
        음성의 랜덤 인덱스을 뽑고 그 인덱스에서 split length까지의 길이를 자른다.
        예를 들어 음성의 길이가 48000인데 (인덱스는 [47999])
        여기서 원하는 스플릿 렝스 16000을 빼면 인덱스는 [47999-16000] = [31999]
        clean = clean [31999 : 47999] 이런 원리
        """
        if len(clean_speech) <= self.split_length:

            # clean_speech가 split_length보다 짧으므로 split_length까지 여분의 길이는 zero padding
            zero_padding = [0 for i in range(len(clean_speech), self.split_length)]

            # split 음성과 나머지 zero padding을 concatenate
            result = np.concatenate([clean_speech, zero_padding])

            return result


        elif len(clean_speech) > self.split_length:

            random_point = np.random.randint(len(clean_speech) - self.split_length)
            result = clean_speech[random_point : random_point + self.split_length]

            return result


    def data_mixing (self, clean, noise):
        '''
        argments
            clean = scipy.io.wavfile.read(음성 파일 리스트 중 하나)
            nosie = 랜덤으로 고른 노이즈 파일 리스트

        Ex)
        noise_source = []
        for _, data in enumerate(noise_file_list):
            sound = scipy.io.wavfile.read(data)
            noise_source.append(sound)
        

        for index, data in enumerate(clean_file_list):
            clean_source = scipy.io.wavfie.read(data)
            noise_index  = np.random.randint(len(noise_source))

            split_clean = self.data_split(clean_source)
            noisy, clean, noise = self.data_mixing(split_clean, noise[noise_index])

            scipy.io.wavfile.write(noisy path)
            scipy.io.wavfile.write(noisy path)
            scipy.io.wavfile.write(noisy path)
        '''

        def SNR_calcaulator (SNR, clean, noise):
            """
            Calculate the scale of noise to create the desired SNR
            Make noisy voice using this alpha value.
            """
            rms_clean = np.sqrt((np.dot(clean, clean) / len(clean)))
            rms_noise = np.sqrt((np.dot(noise, noise) / len(noise)))
            
            # Normalize sound
            scalar_clean = 10 ** (-25 / 20) / rms_clean
            scalar_noise = 10 ** (-25 / 20) / rms_noise
            
            clean = clean * scalar_clean
            noise = noise * scalar_noise

            noise_scalar = np.sqrt((rms_clean / rms_noise / (10**(SNR/20))))
            noisy = clean + (noise_scalar * noise)

            return noisy, clean

        # 랜덤 SNR
        SNR = self.SNR

        if len(noise) <= self.split_length:

            """
            랜덤으로 고른 노이즈 길이가 slef.split_length 짧으면,
            그 길이는 모두 가져오고 추가로 제로패딩을 한다.
            어차피 제로패딩을 해서라도 음성에 더해야 하기 때문에 새로 다시 인덱싱을 하지 않는다. 
            """
            zero_padding  = [0 for i in range(len(noise), self.split_length)]
            noise_split = np.concatenate([noise, zero_padding])

            noisy_result, clean_result = SNR_calcaulator(SNR, clean, noise_split)


        elif len(noise) > self.split_length:

            noise_point = np.random.randint(len(noise) - self.split_length)
            noise_split = noise[noise_point : noise_point + self.split_length]

            noisy_result, clean_result = SNR_calcaulator(SNR, clean, noise_split)

        return noisy_result, clean_result
    

    def data_write (self, file_path, sound, sound_name, index):
    
        scipy.io.wavfile.write(file_path + "/" + str(sound_name) + "{:06d}".format(index+1) + ".wav", 
                               rate = self.target_sampling,  data = sound)
    

    def save (self):
            
        for index, data in tqdm(enumerate(self.clean_source)):

            _, sound = scipy.io.wavfile.read(data)
            split_clean = self.data_split(sound)

            noise_index  = np.random.randint(len(self.noise_source))
            noisy, clean = self.data_mixing(split_clean, self.noise_source[noise_index])

            self.data_write(self.noisy_file_path, noisy, sound_name = self.noisy_name, index = index)
            self.data_write(self.clean_file_path, clean, sound_name = self.clean_name, index = index)

        print("음원 소스를 이용해서 데이터셋 생산 완료")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = 'SETTING OPTION')
    parser.add_argument("--clean_path", type = str, default = "./datasets_source/test_clean", help = "Input clean path")
    parser.add_argument("--noise_path", type = str, default = "./datasets_source/test_noise", help = "Input noise path")
    parser.add_argument("--save_path",  type = str, default = "./datasets",       help = "Input save path")
    parser.add_argument("--noisy_name", type = str, default = "test_noisy",       help = "Input noisy name")
    parser.add_argument("--clean_name", type = str, default = "test_clean",       help = "Input clean name")
    parser.add_argument("--SNR",    type = int, default = 0,     help = "0 : 0 ~ 5, 1 : -2 ~ 3, 2 : -5 ~ 0")
    parser.add_argument("--os",     type = int, default = 16000, help = "Input original sampling")
    parser.add_argument("--ts",     type = int, default = 16000, help = "Input target sampling")
    parser.add_argument("--length", type = int, default = 16384, help = "Input split length")
    parser.add_argument("--iter",   type = int, default = 1,     help = "Input iteration")
    args = parser.parse_args()

    clean_source_path = args.clean_path
    noise_source_path = args.noise_path
    save_file_path = args.save_path
    noisy_name = args.noisy_name
    clean_name = args.clean_name
    SNR = args.SNR
    original_sampling = args.os
    target_sampling = args.ts
    split_length = args.length
    iteration = args.iter

    if SNR == 0:
        SNR = np.random.randint(0, 5)
    elif SNR == 1:
        SNR = np.random.randint(-2, 3)
    elif SNR == 2:
        SNR = np.random.randint(-5, 0)

    resampling_factory = data_mixture(clean_source_path = clean_source_path,
                                      noise_source_path = noise_source_path,
                                      save_file_path = save_file_path,
                                      noisy_name = noisy_name,
                                      clean_name = clean_name,
                                      SNR = SNR,
                                      original_sampling = original_sampling,
                                      target_sampling = target_sampling,
                                      split_length = split_length,
                                      iteration = iteration)

    resampling_factory.save()

    print("-- THe END --")