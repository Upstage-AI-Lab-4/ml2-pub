import os
import re

def handler(base_path, base_filename):
    pattern = re.compile(rf"{re.escape(base_filename)}(?:_(\d+))?\.csv$")
    
    max_suffix = -1
    latest_file = None

    for filename in os.listdir(base_path):
        match = pattern.match(filename)
        if match:
            suffix = int(match.group(1)) if match.group(1) else 0
            if suffix > max_suffix:
                max_suffix = suffix
                latest_file = filename

    return os.path.join(base_path, latest_file) if latest_file else None
