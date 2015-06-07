import subprocess
import csv
import os
import sac.util.utils as utils
import tempfile
import uuid

def create_audio_segment(start_time, end_time, input_wav, output_wav):
    duration = str(float(end_time) - float(start_time))
    subprocess.check_call(["sox", input_wav, output_wav, "trim", start_time, duration])

def create_audio_segments(labels, input_wav, output_dir, remove=True):
    if remove:
        utils.remove_dir(output_dir)
    with open(labels, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter='\t')
        for k, row in enumerate(reader):
            start_time = row[0]
            end_time = row[1]
            label = row[2]
            filename = str(uuid.uuid4())
            create_audio_segment(start_time, end_time, input_wav, os.path.join(output_dir,  "%s_%s.wav" % (filename, label)))


def combine_audio_segments(input_dir, output_dir):
    utils.remove_dir(output_dir)
    input_dir = os.path.abspath(input_dir)
    files = os.listdir(input_dir)
    files_grouped_by_class = {}

    for file in files:
        file_class = utils.get_class_from_filename(file)
        if not file_class in files_grouped_by_class:
            files_grouped_by_class[file_class] = []
        files_grouped_by_class[file_class].append(os.path.join(input_dir, file))

    for class_name in files_grouped_by_class:
        input_wavs = []
        for k, file in enumerate(files_grouped_by_class[class_name]):
            input_wavs.append(file)
        cmd = ['sox'] + input_wavs + [os.path.join(output_dir, 'concat_%s.wav' % class_name)]
        subprocess.check_call(cmd)


def split_concat(files_labels_list_file, output_dir):
    files_labels_list_file = os.path.abspath(files_labels_list_file)
    files_labels_list_dir = os.path.split(files_labels_list_file)[0]

    with open(files_labels_list_file, 'rb') as f:
        files_labels_list = f.readlines()

    temp_dir = tempfile.TemporaryDirectory()

    for file_label_pair in files_labels_list:
        label_file, audio_file = file_label_pair.decode("utf-8").strip().split(",")
        label_file_abs = os.path.join(files_labels_list_dir, label_file)
        audio_file_abs = os.path.join(files_labels_list_dir, audio_file)
        print("%s :: %s" % (label_file_abs, audio_file_abs))
        create_audio_segments(label_file_abs, audio_file_abs, temp_dir.name, remove=False)

    combine_audio_segments(temp_dir.name, output_dir)

    temp_dir.cleanup()