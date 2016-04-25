import csv
import shutil
import struct
import subprocess
import tempfile
import wave

import os
import re
import numpy as np
import itertools
from model.audacity_label import AudacityLabel


class Util(object):

    @staticmethod
    def split_data_based_on_annotation(X, Y, classes):
        data = {}
        for c in classes:
            data[c] = []

        for k, x in enumerate(X):
            sample_class = classes[Y[k]]
            data[sample_class].append(x.tolist())

        for c in classes:
            data[c] = np.array(data[c])

        return data


    @staticmethod
    def get_annotated_data_x_y(timestamps, data, lbls):

        timestamps = np.array(timestamps)

        X = None
        Y = []
        classes = []

        for i in range(0, len(timestamps)):

            for lbl in lbls:
                if lbl.start_seconds <= timestamps[i] <= lbl.end_seconds:
                    if X is None:
                        X = data[i, :]
                    else:
                        X = np.vstack((X, data[i, :]))
                    Y.append(lbl.label)

                    if lbl.label not in classes:
                        classes.append(lbl.label)

        return X, Y, classes

    @staticmethod
    def get_annotated_data(timestamps, data, lbls):
        timestamps = np.array(timestamps)

        annotated_data = {}

        for lbl in lbls:
            start = lbl.start_seconds
            end = lbl.end_seconds
            l_class = lbl.label

            indices = np.where(np.logical_and(timestamps >= start, timestamps <= end))[0]

            if not l_class in annotated_data:
                annotated_data[l_class] = data[indices, :]
            else:
                annotated_data[l_class] = np.vstack((annotated_data[l_class], data[indices, :]))

        return annotated_data

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
        """
        This is to generate continuous segments out of classified small windows
        :param classifications:
        :param timestamps:
        :return:
        """
        window_length = timestamps[1] - timestamps[0]
        combo_list = [(classifications[k], timestamps[k]) for k in range(0, len(classifications))]
        labels = []
        for k, g in itertools.groupby(combo_list, lambda x: x[0]):
            items = list(g)
            start_time = items[0][1]
            end_time = items[-1][1] + window_length
            label_class = items[0][0]
            labels.append(AudacityLabel(start_time, end_time, label_class))
        return labels

    @staticmethod
    def combine_adjacent_labels_of_the_same_class(input_labels):
        labels = []
        for k, g in itertools.groupby(input_labels, lambda x: x.label):
            items = list(g)
            start_time = items[0].start_seconds
            end_time = items[-1].end_seconds
            label_class = items[0].label
            labels.append(AudacityLabel(start_time, end_time, label_class))
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
        downsampled_wav = Util.downsample(input_wav)
        timestamps, samples = Util.read_wav_file(downsampled_wav.name)
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
            timestamps, feature_vectors = Util.load_yaafe_csv("%s.%s.csv" % (audio_file, feature))
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
            timestamps, x = Util.read_merged_features(file, features)
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

    @staticmethod
    def read_audacity_labels(labels_file):
        audacity_labels = []
        with open(labels_file, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            for row in csv_reader:
                audacity_labels.append(AudacityLabel(row[0], row[1], row[2]))
        return audacity_labels

    @staticmethod
    def write_audacity_labels(audacity_labels, filename):
        """
        :param audacity_labels: list containing audacity label objects
        :return:
        """
        with open(filename, "wb") as f:
            for label in audacity_labels:
                f.write("%s\t%s\t%s\n" % (label.start_seconds, label.end_seconds, label.label))

    @staticmethod
    def read_feature_names_from_file(feature_plan):
        with open(feature_plan, "rb") as f:
            lines = f.readlines()

        features = []
        for line in lines:
            if line[0] != "#":
                features.append(line.split(":")[0])

        return features

