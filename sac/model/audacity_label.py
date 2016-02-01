

class AudacityLabel(object):

    def __init__(self, start_seconds, end_seconds, label):
        self.label = label
        self.end_seconds = float(end_seconds)
        self.start_seconds = float(start_seconds)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)