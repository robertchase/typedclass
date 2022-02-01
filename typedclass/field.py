def _String(instance, value):
    return str(value)


class Field:
    def __init__(self,
                 field_type=_String,
                 default=None,
                 is_required=False,
                 is_readonly=False,
                 after_init=None,
                 after_set=None,
                 ):

        self.type = field_type
        self.default = default
        self.is_required = is_required
        self.is_readonly = is_readonly
        self._after_init = after_init
        self._after_set = after_set
        self.name = None

    def parse(self, instance, value):
        return self.type(instance, value)

    def after_init(self, instance):
        if self._after_init:
            self._after_init(instance)

    def after_set(self, instance):
        if self._after_set:
            self._after_set(instance)
