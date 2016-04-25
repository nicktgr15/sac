import logging
import shutil
import subprocess
import csv
import tempfile
import uuid
import sys

import os
from sac.util import Util


class WavEditor(object):
    @staticmethod
    def create_audio_segment(start_time, end_time, input_wav, output_wav):
        duration = str(float(end_time) - float(start_time))
        subprocess.check_call(["sox", input_wav, output_wav, "trim", start_time, duration])

    @staticmethod
    def create_audio_segments(labels, input_wav, output_dir, clear_output_dir, delimiter, format):
        if clear_output_dir:
            Util.remove_dir(output_dir)
        Util.make_dir(output_dir)
        for k, row in enumerate(WavEditor.get_rows(labels, delimiter)):
            if format == "f1":
                start_time = row[0]
                end_time = row[1]
            elif format == "f2":
                start_time = row[0]
                end_time = str(float(row[0]) + float(row[1]))
            else:
                logging.error("not supported file format")
                sys.exit(1)

            label = row[2]
            filename = str(uuid.uuid4())
            WavEditor.create_audio_segment(start_time, end_time, input_wav,
                                           os.path.join(output_dir, "%s_%s.wav" % (filename, label)))


    @staticmethod
    def get_rows(filename, delimiter):
        rows = []
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=delimiter)
            for row in reader:
                if len(row) > 0:
                    rows.append(row)
        return rows

    @staticmethod
    def get_files_grouped_by_class(input_dir):
        input_dir = os.path.abspath(input_dir)
        files = os.listdir(input_dir)
        files_grouped_by_class = {}

        for file in files:
            file_class = Util.get_class_from_filename(file)
            if not file_class in files_grouped_by_class:
                files_grouped_by_class[file_class] = []
            files_grouped_by_class[file_class].append(os.path.join(input_dir, file))

        return files_grouped_by_class

    @staticmethod
    def combine_audio_segments(input_dir, output_name, output_dir, clear_output_dir):
        if clear_output_dir:
            Util.remove_dir(output_dir)
        Util.make_dir(output_dir)
        files_grouped_by_class = WavEditor.get_files_grouped_by_class(input_dir)

        for class_name in files_grouped_by_class:
            input_wavs = []
            for k, file in enumerate(files_grouped_by_class[class_name]):
                input_wavs.append(file)
            cmd = ['sox'] + input_wavs + [os.path.join(output_dir, '%s_%s.wav' % (output_name, class_name))]
            subprocess.check_call(cmd)

    @staticmethod
    def split_concat(files_labels_list_file, output_name, output_dir, clear_output_dir, delimiter, format):
        files_labels_list_file = os.path.abspath(files_labels_list_file)
        files_labels_list_dir = os.path.split(files_labels_list_file)[0]

        with open(files_labels_list_file, 'rb') as f:
            files_labels_list = f.readlines()

        temp_dir = tempfile.mkdtemp()

        for file_label_pair in files_labels_list:
            label_file, audio_file = file_label_pair.decode("utf-8").strip().split(",")
            label_file_abs = os.path.join(files_labels_list_dir, label_file)
            audio_file_abs = os.path.join(files_labels_list_dir, audio_file)
            print("%s :: %s" % (label_file_abs, audio_file_abs))
            WavEditor.create_audio_segments(label_file_abs, audio_file_abs, temp_dir, clear_output_dir, delimiter,
                                            format)

        WavEditor.combine_audio_segments(temp_dir, output_name, output_dir, clear_output_dir)

        # temp_dir.cleanup()
        shutil.rmtree(temp_dir)