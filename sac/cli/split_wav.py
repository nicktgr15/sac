import subprocess
import csv
import os
import sac.util.utils as utils

def create_audio_segment(start_time, end_time, input_wav, output_wav):
    duration = str(float(end_time) - float(start_time))
    subprocess.check_call(['/usr/local/bin/ffmpeg', '-v' , 'error', '-i', input_wav, '-ss', start_time, '-t', duration,
                           '-y', output_wav])

def create_audio_segments(labels, input_wav, output_dir):
    utils.remove_dir(output_dir)
    with open(labels, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter='\t')
        for k, row in enumerate(reader):
            start_time = row[0]
            end_time = row[1]
            label = row[2]
            create_audio_segment(start_time, end_time, input_wav, os.path.join(output_dir,
                                                                               "segment_%s_%s.wav" % (k, label)))