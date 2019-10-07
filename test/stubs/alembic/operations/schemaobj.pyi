# Stubs for alembic.operations.schemaobj (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from ..util.compat import string_types
from typing import Any, Optional


class SchemaObjects:
    migration_context: Any = ...

    def __init__(self, migration_context: Optional[Any] = ...) -> None:
        ...

    def primary_key_constraint(self, name: Any, table_name: Any, cols: Any, schema: Optional[Any] = ...):
        ...

    def foreign_key_constraint(self,
                               name: Any,
                               source: Any,
                               referent: Any,
                               local_cols: Any,
                               remote_cols: Any,
                               onupdate: Optional[Any] = ...,
                               ondelete: Optional[Any] = ...,
                               deferrable: Optional[Any] = ...,
                               source_schema: Optional[Any] = ...,
                               referent_schema: Optional[Any] = ...,
                               initially: Optional[Any] = ...,
                               match: Optional[Any] = ...,
                               **dialect_kw: Any):
        ...

    def unique_constraint(self, name: Any, source: Any, local_cols: Any, schema: Optional[Any] = ..., **kw: Any):
        ...

    def check_constraint(self, name: Any, source: Any, condition: Any, schema: Optional[Any] = ..., **kw: Any):
        ...

    def generic_constraint(self, name: Any, table_name: Any, type_: Any, schema: Optional[Any] = ..., **kw: Any):
        ...

    def metadata(self):
        ...

    def table(self, name: Any, *columns: Any, **kw: Any):
        ...

    def column(self, name: Any, type_: Any, **kw: Any):
        ...

    def index(self, name: Any, tablename: Any, columns: Any, schema: Optional[Any] = ..., **kw: Any):
        ...
