import argparse
import sac.cli.split_wav as split_wav

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # split-wav command parser
    split_wav_parser = subparsers.add_parser('split-wav')
    split_wav_parser.add_argument('-l', '--labels', dest='labels', required=True)
    split_wav_parser.add_argument('-i', '--input-wav', dest='input_wav', required=True)
    split_wav_parser.add_argument('-o', '--output-dir', dest='output_dir', required=True)

    args = parser.parse_args()

    if args.command == "split-wav":
        split_wav.create_audio_segments(args.labels, args.input_wav, args.output_dir)