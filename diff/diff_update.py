from hashlib import sha256
import os
import json

def get_hash(file_data):

    return sha256(file_data).hexdigest()

def get_base_data(rootdir):

    if os.path.isfile(rootdir + '.json'):

        with open("diff/" + rootdir + '.json', 'r') as json_file:
            full_data = json.loads(json_file.read())

    else:

        full_data = {}

        for subdir, dirs, files in os.walk(rootdir):
            for file in files:
                file_name = os.path.join(subdir, file).replace(f'{rootdir}\\', "").replace('\\', '/')
                with open(os.path.join(subdir, file), 'rb') as file:
                    file_data = file.read()
                file_hash = get_hash(file_data)

                full_data[file_name] = file_hash.upper()

        with open("diff/" + rootdir + '.json', 'w') as json_file:
            json_file.write(json.dumps(full_data, indent = 2))

    return full_data

def diff_versions(base, new):

    base_data = get_base_data(base)
    new_data = get_base_data(new)

    all_keys = sorted(set(base_data.keys()) | set(new_data.keys()))

    full_data = []

    for key in all_keys:
        if not key in new_data:
            full_data.append({"Status": "Removed", "Path": key, "Old Hash": base_data[key]})
        elif not key in base_data:
            full_data.append({"Status": "Added", "Path": key, "Hash": new_data[key]})
        elif base_data[key] != new_data[key]:
            full_data.append({"Status": "Changed", "Path": key, "Hash": new_data[key], "Old Hash": base_data[key]})

    with open("diff/" + 'diff.json', 'w') as json_file:
        json_file.write(json.dumps(full_data, indent = 2))

diff_versions('100', '101')