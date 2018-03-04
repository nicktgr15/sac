from unittest import TestCase
from sac.methods.vad import Vad
import os
from sac.model.audacity_label import AudacityLabel


class TestVad(TestCase):

    WAV_FILE = os.path.join(os.path.dirname(__file__), '..', 'fixtures/mono_16bit_16k.wav')
    print(WAV_FILE)

    def test_detect_voice_segments(self):
        vad = Vad()
        lbls = vad.detect_voice_segments(self.WAV_FILE)
        self.assertEqual(3, len(lbls))
        self.assertListEqual([
            AudacityLabel(0.0, 0.51, "non_speech"),
            AudacityLabel(0.51, 1.14, "speech"),
            AudacityLabel(1.14, 1.48481, "non_speech")
        ], lbls)

    def test_generate_missing_labels(self,):
        vad = Vad()
        missing_lbls = vad.generate_missing_labels([AudacityLabel(1.0, 2.0, 'speech')], 0.0, 3.0)
        self.assertListEqual(
            [AudacityLabel(0.0, 1.0, "non_speech"), AudacityLabel(2.0, 3.0, "non_speech")],
            missing_lbls
        )
