
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

class DataSource:
    def __init__(self, tables: list):
        self.tables = tables

    def add_table(self, table):
        if table not in self.tables:
            self.tables.append(table)

    def remove_table(self, table):
        if table in self.tables:
            self.tables.remove(table)

    def get_table(self, name) -> DataTable | None:
        for table in self.tables:
            if table.get_name() == name:
                return table

        return None

    def get_all(self, table_name):
        table = self.get_table(table_name)
        if table:
            return table.get_all()
        else:
            return None

    def get_by_id(self, table_name, id):
        table = self.get_table(table_name)
        if table:
            return table.get_by_id(id)
        else:
            return None

    def get_by_filter(self, table_name, filter):
        table = self.get_table(table_name)
        if table:
            return table.get_by_filter(filter)
        else:
            return None

    def insert(self, table_name, data):
        table = self.get_table(table_name)
        if table:
            return table.insert(data)
        else:
            return None

    def update(self, table_name, id, data):
        table = self.get_table(table_name)
        if table:
            return table.update(id, data)
        else:
            return None

    def delete(self, table_name, id):
        table = self.get_table(table_name)
        if table:
            return table.delete(id)
        else:
            return None
