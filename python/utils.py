import re

def matching_import(pattern, module, globals):
    for key, value in module.__dict__.items():
        if re.findall(pattern, key):
            globals[key] = value
