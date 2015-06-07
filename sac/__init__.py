import argparse
import sac.cli.wav_editor as wav_editor
import sys


class DefaultHelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    parser = DefaultHelpParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # split-wav command parser
    split_wav_parser = subparsers.add_parser('split-wav', help='Splits a wave files in segments using '
                                                               'boundaries and class names provided in a labels file')
    split_wav_parser.add_argument('-l', '--labels', dest='labels', required=True,
                                  help='Audacity compatible labels file.')
    split_wav_parser.add_argument('-i', '--input-wav', dest='input_wav', required=True,
                                  help='The input wave file. Split wave files will use the same encoding.')
    split_wav_parser.add_argument('-o', '--output-dir', dest='output_dir', required=True, help='The output directory.')

    # concat-wav command parser
    concat_wav_parser = subparsers.add_parser('concat-wav', help='Combines wav files generated using the '
                                                                 'split-wav command.')
    concat_wav_parser.add_argument('-i', '--input-dir', dest='input_dir', required=True,
                                   help='The directory containing the split wav files.')
    concat_wav_parser.add_argument('-o', '--output-dir', dest='output_dir', required=True,
                                   help='The output directory.')

    #split-concat-wav command parser
    split_concat_wav_parser = subparsers.add_parser('split-concat-wav', help='Splits and combines multiple wav files.')
    split_concat_wav_parser.add_argument('-i', '--files-labels-list', dest='files_labels_list_file', required=True,
                                         help='A list of comma separated <labels-file>,<wav-file> pairs that will be '
                                              'used as input. Absolute paths required')
    split_concat_wav_parser.add_argument('-o', '--output-dir', dest='output_dir', required=True,
                                         help='The output directory.')

    args = parser.parse_args()

    if args.command == "split-wav":
        wav_editor.create_audio_segments(args.labels, args.input_wav, args.output_dir)
    elif args.command == "concat-wav":
        wav_editor.combine_audio_segments(args.input_dir, args.output_dir)
    elif args.command == "split-concat-wav":
        wav_editor.split_concat(args.files_labels_list_file, args.output_dir)