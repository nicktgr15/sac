from sac.util import Util
import collections
import contextlib
import wave
import webrtcvad
from sac.model.audacity_label import AudacityLabel


class Vad(object):

    def _read_wave(self, path):
        """Reads a .wav file.
        Takes the path, and returns (PCM audio data, sample rate).
        """
        with contextlib.closing(wave.open(path, 'rb')) as wf:
            num_channels = wf.getnchannels()
            assert num_channels == 1
            sample_width = wf.getsampwidth()
            assert sample_width == 2
            sample_rate = wf.getframerate()
            assert sample_rate in (8000, 16000, 32000)
            pcm_data = wf.readframes(wf.getnframes())
            return pcm_data, sample_rate

    class Frame(object):
        """Represents a "frame" of audio data."""
        def __init__(self, bytes, timestamp, duration):
            self.bytes = bytes
            self.timestamp = timestamp
            self.duration = duration

    def _frame_generator(self, frame_duration_ms, audio, sample_rate):
        """Generates audio frames from PCM audio data.
        Takes the desired frame duration in milliseconds, the PCM data, and
        the sample rate.
        Yields Frames of the requested duration.
        """
        n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
        offset = 0
        timestamp = 0.0
        duration = (float(n) / sample_rate) / 2.0
        while offset + n < len(audio):
            yield self.Frame(audio[offset:offset + n], timestamp, duration)
            timestamp += duration
            offset += n

    def _vad_collector(self, sample_rate, frame_duration_ms,
                       padding_duration_ms, vad, frames):
        """Filters out non-voiced audio frames.
        Given a webrtcvad.Vad and a source of audio frames, yields only
        the voiced audio.
        Uses a padded, sliding window algorithm over the audio frames.
        When more than 90% of the frames in the window are voiced (as
        reported by the VAD), the collector triggers and begins yielding
        audio frames. Then the collector waits until 90% of the frames in
        the window are unvoiced to detrigger.
        The window is padded at the front and back to provide a small
        amount of silence or the beginnings/endings of speech around the
        voiced frames.
        Arguments:
        sample_rate - The audio sample rate, in Hz.
        frame_duration_ms - The frame duration in milliseconds.
        padding_duration_ms - The amount to pad the window, in milliseconds.
        vad - An instance of webrtcvad.Vad.
        frames - a source of audio frames (sequence or generator).
        Returns: A generator that yields PCM audio data.
        """
        num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        # We use a deque for our sliding window/ring buffer.
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
        # NOTTRIGGERED state.
        triggered = False

        voiced_frames = []
        for frame in frames:
            is_speech = vad.is_speech(frame.bytes, sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                # If we're NOTTRIGGERED and more than 90% of the frames in
                # the ring buffer are voiced frames, then enter the
                # TRIGGERED state.
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    # We want to yield all the audio we see from now until
                    # we are NOTTRIGGERED, but we have to start with the
                    # audio that's already in the ring buffer.
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                # We're in the TRIGGERED state, so collect the audio data
                # and add it to the ring buffer.
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                # If more than 90% of the frames in the ring buffer are
                # unvoiced, then enter NOTTRIGGERED and yield whatever
                # audio we've collected.
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    triggered = False
                    voiced_frames = voiced_frames[0:len(voiced_frames)-len(ring_buffer)]
                    yield voiced_frames
                    ring_buffer.clear()
                    voiced_frames = []
        if voiced_frames:
            yield voiced_frames

    def generate_missing_labels(self, lbls, start_time, end_time):

        # NOTE: wouldn't work with overlapping labels
        lbls = sorted(lbls, key=lambda x: x.start_seconds)

        missing_lbls = []

        current_time = start_time

        if lbls[0].start_seconds == start_time:
            current_time = lbls[0].end_seconds
            lbls = lbls[1:]

        for k, lbl in enumerate(lbls):
            missing_lbls.append(AudacityLabel(current_time, lbl.start_seconds, "non_speech"))
            current_time = lbl.end_seconds

        if current_time != end_time:
            missing_lbls.append(AudacityLabel(current_time, end_time, "non_speech"))

        return missing_lbls

    def detect_voice_segments(self, wav_file):
        audio, sample_rate = self._read_wave(wav_file)
        vad = webrtcvad.Vad(1)
        frames = list(self._frame_generator(30, audio, sample_rate))
        start_time = 0.0
        end_time = len(audio)/2 * 1.0/sample_rate
        voiced_frames_generator = self._vad_collector(sample_rate, 30, 150, vad, frames)
        lbls = []
        for voiced_frames in voiced_frames_generator:
            lbls.append(AudacityLabel(voiced_frames[0].timestamp, voiced_frames[-1].timestamp, "speech"))
        non_speech_lbls = self.generate_missing_labels(lbls, start_time, end_time)
        return sorted(lbls+non_speech_lbls, key=lambda x: x.start_seconds)
