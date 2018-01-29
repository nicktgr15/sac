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
from sac.model.audacity_label import AudacityLabel
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
import pandas as pd


class Util(object):

    @staticmethod
    def get_shifted_data(predictions, timestamps, shifted_labels):
        shifted_timestamps = []
        shifted_predictions = []

        shifted_labels = sorted(shifted_labels, key=lambda k: k['new_label'].start_seconds)

        for i in range(0, len(predictions)):

            for lbl in shifted_labels:
                if lbl['new_label'].start_seconds <= timestamps[i] <= lbl['new_label'].end_seconds:
                    # shifted_predictions.append(lbl['new_label'].label)
                    shifted_timestamps.append(timestamps[i] + lbl['shift'])

        # print(predictions)
        # print(shifted_timestamps)

        return predictions, shifted_timestamps

    @staticmethod
    def get_annotation_time_shift(labels):
        new_labels = []

        for k, lbl in enumerate(labels):
            if k == 0:
                new_label = AudacityLabel(0, lbl.end_seconds-lbl.start_seconds, lbl.label)
            else:
                new_label = AudacityLabel(
                    start_seconds=lbl.start_seconds-(lbl.start_seconds-new_labels[-1]["new_label"].end_seconds),
                    end_seconds=lbl.end_seconds-(lbl.start_seconds-new_labels[-1]["new_label"].end_seconds),
                    label=lbl.label
                )
            shift = lbl.start_seconds - new_label.start_seconds
            new_labels.append({
                "old_label": lbl,
                "new_label": new_label,
                "shift": shift
            })

        return new_labels

    @staticmethod
    def get_annotated_labels_from_predictions_and_sm_segments(frame_level_predictions, sm_segments, timestamps):

        labeled_segments = []
        timestamps = np.array(timestamps)

        for segment in sm_segments:

            indices = np.where(np.logical_and(timestamps >= segment.start_seconds, timestamps <= segment.end_seconds))[0]
            segment_predictions = frame_level_predictions[indices]
            class_percentages = Util.calculate_classes_percentages(segment_predictions)
            classes = []
            percentages = []
            for key in class_percentages.keys():
                classes.append(key)
                percentages.append(class_percentages[key])
            df = pd.DataFrame({
                "class": classes,
                "percentage": percentages
            })
            df = df.sort_values(by="percentage", ascending=False)
            detected_class_based_on_percentage = df.iloc[0]['class']

            segment.label = detected_class_based_on_percentage
            labeled_segments.append(segment)

        return labeled_segments

    @staticmethod
    def non_maximum_suppression(peaks, values):

        lbls = []
        for k, v in enumerate(values):
            if k in peaks:
                lbls.append(("p", k, v))
            else:
                lbls.append(("n", k, v))

        new_peaks = []

        for k, g in itertools.groupby(lbls, lambda x: x[0]):
            items = list(g)
            # no peaks
            if items[0][0] == "p":
                if len(items) == 1:
                    new_peaks.append(items[0][1])
                else:
                    group_peak_values = [item[2] for item in items]
                    argmax = np.argmax(group_peak_values)
                    new_peaks.append(items[argmax][1])

        return new_peaks, values

    @staticmethod
    def combine_peaks(a_peaks, a_peak_values, b_peaks, b_peak_values):

        new_peaks = []

        for b_peak in b_peaks:
            # check if a peak already exists in the same position.
            # if the new peak has higher value -> update existing value
            if b_peak in a_peaks:
                if b_peak_values[b_peak] > a_peak_values[b_peak]:
                    a_peak_values[b_peak] = b_peak_values[b_peak]
            else:
                new_peaks.append(b_peak)
                a_peak_values[b_peak] = b_peak_values[b_peak]

        a_peaks = a_peaks + new_peaks
        a_peaks = np.sort(a_peaks)
        return a_peaks.tolist(), a_peak_values

    @staticmethod
    def kmeans_image_quantisation(sm, clusters=5, random_samples=10000):
        sm_reshaped = sm.reshape((-1, 1))

        random_samples_from_image = shuffle(sm_reshaped, random_state=0)[0:20]

        kmeans = KMeans(n_clusters=clusters)
        kmeans.fit(random_samples_from_image)

        y = kmeans.predict(sm_reshaped)

        for i in range(len(y)):
            sm_reshaped[i] = kmeans.cluster_centers_[y[i]]

        image = sm_reshaped.reshape(sm.shape)
        return image

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
        """
        DOESN'T work with OVERLAPPING labels

        :param timestamps:
        :param data:
        :param lbls:
        :return:
        """

        timestamps = np.array(timestamps)

        timestamp_step = timestamps[3]-timestamps[2]
        current_new_timestamp = 0.0
        new_timestamps = []

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
                    new_timestamps.append(current_new_timestamp)
                    current_new_timestamp += timestamp_step

                    if lbl.label not in classes:
                        classes.append(lbl.label)

        return X, Y, classes, new_timestamps

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
        with open(labels_file, 'r') as csv_file:
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
        with open(filename, "w") as f:
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
