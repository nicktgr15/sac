import argparse
import sys

from sac.cli.wav_editor import WavEditor


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
                                  help='CSV labels file.')
    split_wav_parser.add_argument('-i', '--input-wav', dest='input_wav', required=True,
                                  help='The input wave file. Split wave files will use the same encoding.')
    split_wav_parser.add_argument('-o', '--output-dir', dest='output_dir', required=True, help='The output directory.')
    split_wav_parser.add_argument('-d', '--delimiter', dest='delimiter', help='Labels parser delimiter', default="\t")
    split_wav_parser.add_argument('-f', '--labels-format', dest='format', choices=['f1', 'f2'], required=True,
                                  help='The labels format. f1: start,end,class f2: start,duration,class')

    # concat-wav command parser
    concat_wav_parser = subparsers.add_parser('concat-wav', help='Combines wav files generated using the '
                                                                 'split-wav command.')
    concat_wav_parser.add_argument('-i', '--input-dir', dest='input_dir', required=True,
                                   help='The directory containing the split wav files.')
    concat_wav_parser.add_argument('-n', '--output-filename', dest='output_name', required=True,
                                   help='The name prefix of the generated files.')
    concat_wav_parser.add_argument('-o', '--output-dir', dest='output_dir', required=True,
                                   help='The output directory.')

    # split-concat-wav command parser
    split_concat_wav_parser = subparsers.add_parser('split-concat-wav', help='Splits and combines multiple wav files.')
    split_concat_wav_parser.add_argument('-i', '--files-labels-list', dest='files_labels_list_file', required=True,
                                         help='A list of comma separated <labels-file>,<wav-file> pairs that will be '
                                              'used as input. Relative to this file.')
    split_concat_wav_parser.add_argument('-o', '--output-dir', dest='output_dir', required=True,
                                         help='The output directory.')
    split_concat_wav_parser.add_argument('-d', '--delimiter', dest='delimiter', help='Labels parser delimiter',
                                         default="\t")
    split_concat_wav_parser.add_argument('-n', '--output-filename', dest='output_name', required=True,
                                         help='The name prefix of the generated files.')
    split_concat_wav_parser.add_argument('-f', '--labels-format', dest='format', choices=['f1', 'f2'], required=True,
                                         help='The labels format. f1: start,end,class f2: start,duration,class')

    args = parser.parse_args()

    if args.command == "split-wav":
        WavEditor.create_audio_segments(args.labels, args.input_wav, args.output_dir, False, args.delimiter,
                                        args.format)
    elif args.command == "concat-wav":
        WavEditor.combine_audio_segments(args.input_dir, args.output_name, args.output_dir, False)
    elif args.command == "split-concat-wav":
        WavEditor.split_concat(args.files_labels_list_file, args.output_name, args.output_dir, False, args.delimiter,
                               args.format)