
class FilterField:
    def __init__(self, name, field_type, default=None):
        self.name = name
        self.field_type = field_type
        self.default = default

    def serialize(self) -> dict[str, tuple]:
        return {
            self.name : (self.field_type, self.default)
        }

class DataTable:
    def __init__(self, name):
        self.name = name
        self.filter_fields = [] #type: list[FilterField]

    def set_filter_fields(self, fields: dict[str, tuple]):
        for key, value in fields.items():
            if not isinstance(value, tuple):
                raise ValueError("Value must be a tuple")
            default = None
            if len(value) == 2:
                default = value[1]
            if len(value) > 2:
                raise ValueError("Value must be a tuple of length 2")
            self.filter_fields.append(FilterField(key, value[0], default))

    def add_filter_field(self, field: FilterField):
        self.filter_fields.append(field)

    def get_filter_fields(self):
        formatted = {}
        for field in self.filter_fields:
            formatted.update(field.serialize())
        return formatted

    def get_name(self):
        return self.name

    def get_all(self):
        pass

    def get_by_id(self, id):
        pass

    def get_by_filter(self, filter: dict):
        pass

    def insert(self, data):
        pass

    def update(self, id, data):
        pass

    def delete(self, id):
        pass

