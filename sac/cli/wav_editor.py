import logging
import shutil
import subprocess
import csv
import tempfile
import uuid
import sys

import os
from sac.util import Util

def all_same(items):
    return all(x[2] == items[0][2] for x in items)


def find_min_start(items):
    min = float('Inf')
    for i in items:
        if i[0] <= min:
            min = i[0]
    return min


def find_max_end(items):
    max = -float('Inf')
    for i in items:
        if i[1] >= max:
            max = i[1]
    return max


def chunks(l, n):
    c = []
    for i in range(0, len(l), n):
        c.append(l[i:i+n] + ["m"])
    return c


def not_in_overlapping(item, overlapping_items):
    for i in overlapping_items:
        for j in i:
            if item == j:
                return False
    return True

class WavEditor(object):
    @staticmethod
    def create_audio_segment(start_time, end_time, input_wav, output_wav):
        duration = str(float(end_time) - float(start_time))
        subprocess.check_call(["sox", input_wav, output_wav, "trim", start_time, duration])

    @staticmethod
    def get_non_overlapping_items(rows_in_f2):

        transformed_rows = []
        for row in rows_in_f2:
            transformed_rows.append([float(row[0]), float(row[0])+float(row[1]), row[2]])

        overlapping = []
        non_overlapping = []

        for i in range(len(transformed_rows)):
            row = transformed_rows[i]
            overlapping_rows = []
            for j in range(i+1, len(transformed_rows)):
                j_row = transformed_rows[j]
                if j_row[0] < row[1]:
                    if len(overlapping_rows) == 0:
                        overlapping_rows.extend([row, j_row])
                    else:
                        overlapping_rows.append(j_row)
            if len(overlapping_rows) == 0 and not_in_overlapping(row, overlapping):
                non_overlapping.append(row)
            elif len(overlapping_rows) != 0 and not_in_overlapping(row, overlapping):
                overlapping.append(overlapping_rows)

        print overlapping
        print non_overlapping

        new_overlapping = []

        # find same class
        for o in overlapping:
            if all_same(o):
                non_overlapping.append([
                    find_min_start(o),
                    find_max_end(o),
                    o[0][2]
                ])
            else:
                new_overlapping.append(o)

        overlapping = new_overlapping

        # find m s s s .. pattern
        for o in overlapping:
            # print o
            if o[0][2] == "m" and all_same(o[1:]):
                cut_points = [o[0][0]]
                m_section = o[0]
                has_end = True
                for overlapping_s_section in o[1:]:
                    if float(overlapping_s_section[0]) > float(m_section[0]) and float(overlapping_s_section[1]) < float(m_section[1]):
                        cut_points.append(overlapping_s_section[0])
                        cut_points.append(overlapping_s_section[1])
                    else:
                        cut_points.append(overlapping_s_section[0])
                        has_end = False
                if has_end:
                    cut_points.append(m_section[1])
            # print cut_points
            non_overlapping.extend(chunks(cut_points, 2))

        for i in range(len(non_overlapping)):
            non_overlapping[i][0] = str(non_overlapping[i][0])
            non_overlapping[i][1] = str(non_overlapping[i][1])
            non_overlapping[i][2] = str(non_overlapping[i][2])


        return non_overlapping

    @staticmethod
    def create_audio_segments(labels, input_wav, output_dir, clear_output_dir, delimiter, format, remove_overlapping=False):
        if clear_output_dir:
            Util.remove_dir(output_dir)
        Util.make_dir(output_dir)

        rows = WavEditor.get_rows(labels, delimiter)
        if format == "f2" and remove_overlapping:
            rows = WavEditor.get_non_overlapping_items(rows)

        for k, row in enumerate(rows):
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