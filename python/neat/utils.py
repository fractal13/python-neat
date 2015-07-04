import re

def matching_import(pattern, module, globals):
    for key, value in module.__dict__.items():
        if re.findall(pattern, key):
            globals[key] = value

def main():
    print "Need utils exercise code here."
    return
    
if __name__ == "__main__":
    main()

