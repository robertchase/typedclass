from typedclass.types import String


class Field:
    NO_DEFAULT = type("EMPTY", (), dict())

    def __init__(self,
                 field_type=String(),
                 default=NO_DEFAULT,
                 is_required=False,
                 is_readonly=False,
                 after_init=None,
                 before_set=None,
                 after_set=None,
                 ):

        self.type = field_type
        self.is_nested = False
        self.default = default
        self.is_required = is_required
        self.is_readonly = is_readonly
        self._after_init = after_init
        self._before_set = before_set
        self._after_set = after_set
        self.name = None

    def parse(self, instance, value):
        return self.type(instance, value)

    def after_init(self, instance):
        if self._after_init and instance:
            self._after_init(instance)

    def before_set(self, instance, value):
        if self._before_set and instance:
            value = self._before_set(instance, value)
        return value

    def after_set(self, instance):
        if self._after_set and instance:
            self._after_set(instance)
