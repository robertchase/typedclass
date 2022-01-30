class Set:
    def __init__(self, *args, name=None):
        self.valid = args
        if name:
            self.__name__ = name

    def __call__(self, instance, value):
        if value not in self.valid:
            raise ValueError(f"must be one of {self.valid}")
        return value
