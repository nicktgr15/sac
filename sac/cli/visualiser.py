import re
import tempfile
import wave
import struct
from matplotlib import pyplot as plt
import subprocess
import numpy as np


def read_wav_file(input_wav):
    wave_file = wave.open(input_wav, 'r')
    length = wave_file.getnframes()
    print(wave_file.getparams())

    channels = wave_file.getnchannels()
    sample_width = wave_file.getsampwidth()
    bytes_per_frame = channels * sample_width

    c0 = []
    wave_file.rewind()

    for i in range(0, length):
        wave_data = wave_file.readframes(1)
        # print(len(waveData))
        # because we have 2 channels the waveData length is 4. so we get the first 2 bytes only (for one channel)
        data = struct.unpack("<h", wave_data[0:2])
        c0.append(data[0])

    print(len(wave_data))

    return c0

def downsample(input_wav):
    downsampled_wav = tempfile.NamedTemporaryFile(suffix=".wav")
    subprocess.check_call(['sox', input_wav, '-r', '1000', downsampled_wav.name])
    return downsampled_wav

def get_sample_rate(input_wav):
    wave_file = wave.open(input_wav, 'r')
    return wave_file.getframerate()

def parse_yaafe_header(csv_file):
    header = {}
    with open(csv_file, 'r') as csv_file:
        lines = csv_file.readlines(5)
    for line in lines:
        if 'samplerate' in line:
            header['samplerate'] = int(re.search('.*samplerate=(\d+).*', line).group(1))
        if 'yaafedefinition' in line:
            yaafedefinition = re.search('.*yaafedefinition=(\d+).*', line).group(1).split('>')





def load_yaafe_csv(csv_file):
    features = []
    step_size = None
    aggregated_step_size = None
    with open(csv_file, 'r') as csv_file:
        for line in csv_file:
            extracted_step_size = False
            if line[0] == '%':
                if 'StepNbFrames' in line and extracted_step_size is False:
                    step_size = re.search('.*StepNbFrames=(\d+).*', line).group(1)
                    aggregated_step_size = re.search('.*stepSize=(\d+).*', line).group(1)
                    extracted_step_size = True
                elif 'stepSize' in line and extracted_step_size is False:
                    step_size = re.search('.*stepSize=(\d+).*', line).group(1)
                    extracted_step_size = True
            else:
                feature_vector_elements = line.split(',')
                feature_vector_elements = [float(i) for i in feature_vector_elements]
                features.append(feature_vector_elements)

    if aggregated_step_size is None:
        timestamps = [(i*float(step_size))/float(sample_rate) for i in range(0, len(features))]
    else:
        timestamps = [(i*float(step_size)*float(aggregated_step_size))/float(sample_rate) for i in range(0, len(features))]

    return timestamps, np.array(features)


def visualise(input_wav, features_csv_file):

    original_sample_rate = get_sample_rate(input_wav)
    timestamps, features = load_yaafe_csv(features_csv_file, original_sample_rate)

    downsampled_wav = downsample(input_wav)
    samples = read_wav_file(downsampled_wav)
    x = [s/1000 for s in range(0, len(samples))]
    print(len(samples))

    fig, ax1 = plt.subplots()
    ax1.plot(x, samples, 'c')

    ax2 = ax1.twinx()
    for i in range(0, features.shape[1]):
        # if i == 1:
        #     ax2.plot(timestamps, features[:, i]/features[:, i-1], label='column %s' % i)
        # else:
        # if i == 9:
            ax2.plot(timestamps, features[:, i], label='column %s' % i)

    plt.grid()
    plt.legend()
    plt.show()
