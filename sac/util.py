import shutil
import struct
import subprocess
import tempfile
import wave

import os
import re
import numpy as np


class Util(object):
    @staticmethod
    def remove_dir(directory):
        if os.path.exists(directory):
            shutil.rmtree(directory)

    @staticmethod
    def make_dir(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def get_class_from_filename(filename):
        return filename.split("_")[-1].split(".")[0]

    @staticmethod
    def calculate_classes_percentages(classifications):
        percentages = {}

        for classification in classifications:
            if not classification in percentages:
                percentages[classification] = 0
            percentages[classification] += 1

        for k in percentages:
            percentages[k] = percentages[k] / float(len(classifications))

        return percentages

    @staticmethod
    def generate_labels_from_classifications(classifications, timestamps):
        window_length = timestamps[1] - timestamps[0]
        chunks = []
        previous = classifications[0]
        previous_position = 0
        for k, classification in enumerate(classifications):
            if classification != previous:
                chunks.append({
                    "classifications": classifications[previous_position:k],
                    "time-range": timestamps[previous_position:k]
                })
                previous_position = k
                previous = classification
            if k == len(classifications) - 1:
                chunks.append({
                    "classifications": classifications[previous_position:k + 1],
                    "time-range": timestamps[previous_position:k + 1]
                })
        labels = []
        for chunk in chunks:
            start_time = chunk["time-range"][0]
            end_time = chunk["time-range"][-1] + window_length
            label_class = chunk["classifications"][0]
            labels.append([start_time, end_time, label_class])
        return labels

    @staticmethod
    def downsample(input_wav):
        downsampled_wav = tempfile.NamedTemporaryFile(suffix=".wav")
        subprocess.check_call(['/usr/local/bin/sox', input_wav, '-r', '1000', downsampled_wav.name])
        return downsampled_wav

    @staticmethod
    def get_sample_rate(input_wav):
        wave_file = wave.open(input_wav, 'r')
        return wave_file.getframerate()

    @staticmethod
    def read_wav_file(input_wav):
        wave_file = wave.open(input_wav, 'r')
        length = wave_file.getnframes()
        print(wave_file.getparams())

        channels = wave_file.getnchannels()
        sample_width = wave_file.getsampwidth()
        bytes_per_frame = channels * sample_width
        sample_rate = wave_file.getframerate()

        samples = []
        wave_file.rewind()

        for i in range(0, length):
            wave_data = wave_file.readframes(1)
            # print(len(waveData))
            # because we have 2 channels the waveData length is 4. so we get the first 2 bytes only (for one channel)
            data = struct.unpack("<h", wave_data[0:2])
            samples.append(data[0])

        timestamps = [c * 1.0 / sample_rate for c in range(0, len(samples))]

        print(len(wave_data))

        return timestamps, samples

    @staticmethod
    def read_downsampled_wav(input_wav):
        downsampled_wav = downsample(input_wav)
        timestamps, samples = read_wav_file(downsampled_wav.name)
        downsampled_wav.close()
        return timestamps, samples

    @staticmethod
    def parse_yaafe_header(csv_file):
        header = {}
        header_lines = []
        with open(csv_file, 'r') as csv_file:
            for i in range(0, 6):
                l = csv_file.readline()
                if l[0] == "%":
                    header_lines.append(l.strip())

        for line in header_lines:
            if 'samplerate' in line:
                header['samplerate'] = int(re.search('.*samplerate=(\d+).*', line).group(1))
            if 'yaafedefinition' in line:
                yaafedefinition = re.search('.*yaafedefinition=(.*)', line).group(1)

                yaafedefinition_groups = re.search('.*yaafedefinition=(.*)', line).group(1).split('>')
                base_conf = yaafedefinition_groups[0].strip()
                base_step_size = int(re.search('.*stepSize=(\d+).*', line).group(1))

                yaafedefinition_groups_without_derivate = []
                for group in yaafedefinition_groups:
                    if not "Derivate" in group:
                        yaafedefinition_groups_without_derivate.append(group)

                if len(yaafedefinition_groups_without_derivate) > 1:
                    for i in range(1, len(yaafedefinition_groups_without_derivate)):
                        step_nb_frames = int(re.search('.*StepNbFrames=(\d+).*', line).group(1))
                        base_step_size *= step_nb_frames
                header['effective_step_size'] = base_step_size

        return header

    @staticmethod
    def load_yaafe_csv(csv_file):
        header = Util.parse_yaafe_header(csv_file)
        features = []
        with open(csv_file, 'r') as csv_file:
            for line in csv_file:
                if line[0] != '%':
                    feature_vector_elements = line.split(',')
                    feature_vector_elements = [float(i) for i in feature_vector_elements]
                    features.append(feature_vector_elements)

        timestamps = [i * header['effective_step_size'] / float(header['samplerate']) for i in range(0, len(features))]

        return timestamps, np.array(features)

    @staticmethod
    def read_merged_features(audio_file, features):
        feature_list = []
        for feature in features:
            timestamps, feature_vectors = load_yaafe_csv("%s.%s.csv" % (audio_file, feature))
            feature_list.append(feature_vectors)

        return timestamps, np.hstack((i for i in feature_list))

    @staticmethod
    def read_full_dataset(files, features, selected_features=[]):
        """

        :param files: a list of the audio files
        :param features: a list of the names of the audio features
        :param selected_features: a list of column positions
        :return:
        """

        data = []
        classes = []

        for file in files:
            class_id = file.split("_")[-1].split(".")[0]
            if not class_id in classes:
                classes.append(class_id)
            timestamps, x = read_merged_features(file, features)
            y = [classes.index(class_id) for i in x]
            data.append({
                "x": x,
                "y": y
            })

        X = np.vstack((d["x"] for d in data))
        Y = np.hstack((d["y"] for d in data))

        if len(selected_features) == 0:
            return X, Y, classes
        else:
            return X[:, selected_features], Y, classes