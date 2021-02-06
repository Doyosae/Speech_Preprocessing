import os, argparse
import wave, natsort
import numpy as np
from tqdm import tqdm

import scipy
import scipy.signal
import scipy.io.wavfile
import librosa

class data_mixture ():
    """
    Datasets Directory Speech Separation and Enhancement
        train
            noisy
            clean
        test
            noisy
            clean

    Requirements : Target Speech, Target Noise

    def __init__    : Gets the sound source from the test_clean folder and test_noise folder in datasets_source.
    def data_split  : Pick a Speech and cut it to fit the length of the split_length.
    (The number of replications will soon be determined by the number of data iteration)
    def data_mixing : Mix split clean and noise with Loudness normalize (-25 dBFS) and match the SNR level.
        return noisy, clean
    def data_write  : Module for storing sound

    def save
        Process
        1. Read all file names of speech folder.
            Read all file names of noise folder.
        2. Call the speech file name list one by one and splits
        3. Choose one noise randomly from the noise file name list.
            random pick noise, random sample for split_length
        4. Mixing to SNR ratio == return noisy clean
        5. Save noisy, clean, noise
            Save as .npy in ./datasets/ folder (used as learning data for model)
            Create each sound folder in the ./datasets/ folder.Save as wav file
    """
    def __init__ (self, clean_source_path = "./datasets_original/clean",
                        noise_source_path = "./datasets_original/noise",
                        save_file_path    = "./datasets",
                        noisy_name        = "test_noisy",
                        clean_name        = "test_clean",
                        SNR               = np.random.randint(0, 5),
                        original_sampling = 16000,
                        target_sampling   = 16000,
                        split_length      = 16384,
                        iteration         = 1):
        '''
        arguments:
            clean_source_path: original clean path
            noise_source_path: original noise path
            save_file_path   : save file path for mixture(noisy) and target(clean)
            noisy_name       : filename of mixture(noisy)
            clean_name       : filenmae of target(clean)
            SNR              : ratio of signal and noise
            original_sampling : sampling rate of original sound
            target_sampling   : sampling rate of synthesized sound
            split_length      : cutting size of synthesized sound
            iteration         : iteration of total process
        '''
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
                print(str(folder_path) + " Finished creating folder path")


        self.clean_source_path = clean_source_path
        self.noise_source_path = noise_source_path
        self.save_file_path    = save_file_path
        self.noisy_name        = noisy_name
        self.clean_name        = clean_name

        self.SNR = SNR
        self.original_sampling = original_sampling
        self.target_sampling   = target_sampling
        self.split_length      = split_length
        self.iteration         = iteration

        self.clean_file_list   = walk_filename(self.clean_source_path)
        self.noise_file_list   = walk_filename(self.noise_source_path)

        self.noisy_file_path   = self.save_file_path + "/" + self.noisy_name + "/"
        self.clean_file_path   = self.save_file_path + "/" + self.clean_name + "/"
        folder_make(self.noisy_file_path)
        folder_make(self.clean_file_path)


        'Load noise_source_sound, clean_source_file'
        self.noise_source = []
        self.clean_source = []

        for _, data in tqdm(enumerate(self.noise_file_list)):
            sr, sound = scipy.io.wavfile.read(data)
            self.noise_source.append(sound)
        print("Completed loading of noise source memory")

        for iteration in range(self.iteration):
            self.clean_source.extend(self.clean_file_list)
        print("Completed loading voice source iteration list")


    def data_split (self, clean_speech):
        """
        Cut as much as you want from the voice file.
        (sr = 16000 and 48,000 slices 3sec)
        It's about every voice.
        Padding with 0. for the rest of the voice shorter than this
        
        Pull out a random index of the voice and cut the length from that index to the split length.
        For example, the voice is 48000 long (index is [47999]).
        If you subtract the desired split lance 16000 here, the index is [47999-16000] = [31999]
        Clean = Clean [31999 : 4799] This principle
        """
        if len(clean_speech) <= self.split_length:
            # Because clean_spech is shorter than split_length, the extra length to split_length is zero padding
            zero_padding = [0 for i in range(len(clean_speech), self.split_length)]
            # convert the split voice and the rest of the zero padding
            result       = np.concatenate([clean_speech, zero_padding])

            return result

        elif len(clean_speech) > self.split_length:
            random_point = np.random.randint(len(clean_speech) - self.split_length)
            result       = clean_speech[random_point : random_point + self.split_length]

            return result


    def data_mixing (self, clean, noise):
        '''
        argments
            clean = scipy.io.wavfile.read(One of the list of voice files)
            nosie = List of randomly selected noise files

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
            clean        = clean * scalar_clean
            noise        = noise * scalar_noise
            noise_scalar = np.sqrt((rms_clean / rms_noise / (10**(SNR/20))))
            noisy        = clean + (noise_scalar * noise)

            return noisy, clean

        # Randomly SNR
        SNR = self.SNR

        if len(noise) <= self.split_length:
            """
            If the noise length chosen randomly is short, then the self.split_length,
            Bring all the length and add zero padding.
            They don't index again because they have to add to their voice even if they have zero padding anyway.
            """
            zero_padding               = [0 for i in range(len(noise), self.split_length)]
            noise_split                = np.concatenate([noise, zero_padding])
            noisy_result, clean_result = SNR_calcaulator(SNR, clean, noise_split)

        elif len(noise) > self.split_length:
            noise_point                = np.random.randint(len(noise) - self.split_length)
            noise_split                = noise[noise_point : noise_point + self.split_length]
            noisy_result, clean_result = SNR_calcaulator(SNR, clean, noise_split)

        return noisy_result, clean_result
    

    def data_write (self, file_path, sound, index):
        scipy.io.wavfile.write(file_path + "{:08d}".format(index+1) + ".wav", rate = self.target_sampling,  data = sound)
    

    def save (self, subset_length):
        if subset_length is None:
          pass
        else:
          self.clean_source = self.clean_source[:subset_length]
          
        for index, data in tqdm(enumerate(self.clean_source)):
            _, sound     = scipy.io.wavfile.read(data)
            split_clean  = self.data_split(sound)
            noise_index  = np.random.randint(len(self.noise_source))
            noisy, clean = self.data_mixing(split_clean, self.noise_source[noise_index])
            
            noisy = noisy.astype("float32")
            clean = clean.astype("float32")
            # noise = noisy - clean

            self.data_write(self.noisy_file_path, noisy, index = index)
            self.data_write(self.clean_file_path, clean, index = index)
            # self.data_write(self.save_file_path + "/noise/", noise, index)

        print("Complete dataset production using sound source")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = 'SETTING OPTION')
    parser.add_argument("--cp", type = str, default = "./datasets_original/train_clean", help = "Input clean path")
    parser.add_argument("--np", type = str, default = "./datasets_original/train_noise", help = "Input noise path")
    parser.add_argument("--sp", type = str, default = "./datasets/short",    help = "Input save path")
    parser.add_argument("--nn", type = str, default = "train_noisy",   help = "Input noisy name")
    parser.add_argument("--cn", type = str, default = "train_clean",   help = "Input clean name")
    parser.add_argument("--snr",    type = int, default = 0,      help = "0 : 0 ~ 5, 1 : -2 ~ 3, 2 : -5 ~ 0")
    parser.add_argument("--os",     type = int, default = 16000,  help = "Input original sampling")
    parser.add_argument("--ts",     type = int, default = 16000,  help = "Input target sampling")
    parser.add_argument("--length", type = int, default = 16384,  help = "Input split length")
    parser.add_argument("--itera",  type = int, default = 1,      help = "Input iteration")
    parser.add_argument("--sub",    type = int, default = 100000, help = "Input sub slice")
    args = parser.parse_args()

    clean_source_path = args.cp
    noise_source_path = args.np
    save_file_path    = args.sp
    noisy_name        = args.nn
    clean_name        = args.cn
    SNR               = args.snr
    original_sampling = args.os
    target_sampling   = args.ts
    split_length      = args.length
    iteration         = args.itera
    subset_length     = args.sub
    
    if   SNR == 0:
         SNR = np.random.randint(0, 5)
    elif SNR == 1:
         SNR = np.random.randint(-2, 3)
    elif SNR == 2:
         SNR = np.random.randint(-5, 0)
    elif SNR == -1:
         SNR = 0

    resampling_factory = data_mixture(clean_source_path = clean_source_path,
                                      noise_source_path = noise_source_path,
                                      save_file_path    = save_file_path,
                                      noisy_name        = noisy_name,
                                      clean_name        = clean_name,
                                      SNR               = SNR,
                                      original_sampling = original_sampling,
                                      target_sampling   = target_sampling,
                                      split_length      = split_length,
                                      iteration         = iteration)

    resampling_factory.save(subset_length = subset_length)
    print("-- THe END --")
