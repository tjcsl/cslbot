# Stubs for jinja2.loaders (Python 3.5)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any
from types import ModuleType

def split_template_path(template): ...

class BaseLoader:
    has_source_access = ...  # type: Any
    def get_source(self, environment, template): ...
    def list_templates(self): ...
    def load(self, environment, name, globals=None): ...

class FileSystemLoader(BaseLoader):
    searchpath = ...  # type: Any
    encoding = ...  # type: Any
    followlinks = ...  # type: Any
    def __init__(self, searchpath: str, encoding='', followlinks=False) -> None: ...
    def get_source(self, environment, template): ...
    def list_templates(self): ...

class PackageLoader(BaseLoader):
    encoding = ...  # type: Any
    manager = ...  # type: Any
    filesystem_bound = ...  # type: Any
    provider = ...  # type: Any
    package_path = ...  # type: Any
    def __init__(self, package_name, package_path='', encoding=''): ...
    def get_source(self, environment, template): ...
    def list_templates(self): ...

class DictLoader(BaseLoader):
    mapping = ...  # type: Any
    def __init__(self, mapping): ...
    def get_source(self, environment, template): ...
    def list_templates(self): ...

class FunctionLoader(BaseLoader):
    load_func = ...  # type: Any
    def __init__(self, load_func): ...
    def get_source(self, environment, template): ...

class PrefixLoader(BaseLoader):
    mapping = ...  # type: Any
    delimiter = ...  # type: Any
    def __init__(self, mapping, delimiter=''): ...
    def get_loader(self, template): ...
    def get_source(self, environment, template): ...
    def load(self, environment, name, globals=None): ...
    def list_templates(self): ...

class ChoiceLoader(BaseLoader):
    loaders = ...  # type: Any
    def __init__(self, loaders): ...
    def get_source(self, environment, template): ...
    def load(self, environment, name, globals=None): ...
    def list_templates(self): ...

class _TemplateModule(ModuleType): ...

class ModuleLoader(BaseLoader):
    has_source_access = ...  # type: Any
    module = ...  # type: Any
    package_name = ...  # type: Any
    def __init__(self, path): ...
    @staticmethod
    def get_template_key(name): ...
    @staticmethod
    def get_module_filename(name): ...
    def load(self, environment, name, globals=None): ...