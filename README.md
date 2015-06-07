# SAC (Semantic Audio Companion)

Sac is a python command line tool based on [Sox](http://sox.sourceforge.net/) which splits wave files using time boundaries
defined in a labels file and afterwards concatenates them according to their class identifiers.

## Installation

- Install [Python](https://www.python.org/downloads/)
- Install [Sox](http://sox.sourceforge.net/)
- Install Sac `pip install sac`

To verify that you have a working sac installation do:

```sac -h```

and you should see the following output


```
usage: sac [-h] {split-wav,concat-wav,split-concat-wav} ...

positional arguments:
  {split-wav,concat-wav,split-concat-wav}
    split-wav           Splits a wave files in segments using boundaries and
                        class names provided in a labels file
    concat-wav          Combines wav files generated using the split-wav
                        command.
    split-concat-wav    Splits and combines multiple wav files.

optional arguments:
  -h, --help            show this help message and exit
```

## Example

Lets suppose that we have the following `labels-wavs.txt` file and we want to generate the concatenated wav files under the `output` dir.
The contents of the `labels-wavs.txt` should be relative to itself.

```
audio_1.labels.txt,audio_1.wav
audio_2.labels.txt,audio_2.wav
```

We run:

```
sac split-concat-wav -i path/to/labels-wavs.txt -o output
```

If our label files look like the following:

```
25.407824	27.037760	v
28.571817	29.530603	v
33.653382	35.762711	v
49.665105	53.596127	m
55.417820	56.664242	v
116.013084	118.601806	v
```

Then we expect the `output` directory to contain the following files:

```
concat_m.wav    
concat_v.wav
```

