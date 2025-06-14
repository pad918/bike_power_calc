

class OpenRange:
    
    def __init__(self, min, max):
        self._min = min
        self._max = max

    # Overide dunder method to test if number is in this range
    def __contains__(self, item):
        return item <= self._max and item >= self._min 