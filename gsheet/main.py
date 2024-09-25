import oead
import os
import yaml

def list_datasheet(version):

    file_list = []
    for subdir, dirs, files in os.walk(version):
        for file in files:
            if file.endswith('.gsheet'):
                file_list.append(os.path.join(subdir, file))

    print(file_list)
    return file_list

def oead_to_py(obj):

    if type(obj) in [oead.BufferBool, oead.BufferInt, oead.BufferF32, oead.BufferString, oead.gsheet.StructArray, oead.gsheet.FieldArray]:
        result = []
        for obj_ in list(obj):
            result.append(oead_to_py(obj_))
        return result
    
    elif type(obj) is oead.gsheet.Field:
        result = {}
        result['name'] = obj.name
        result['type_name'] = obj.type_name
        result['type'] = obj.type.value
        result['flags'] = obj.flags
        result['fields'] = oead_to_py(obj.fields)
        return result
    
    elif type(obj) is oead.gsheet.Struct:
        result = {}
        for key, value in obj.items():
            result[key] = oead_to_py(value)
        return result
    
    elif type(obj) is oead.Bytes:
        return bytes(obj)
    
    return obj

def read_sheet(file_data):

    data = {}

    datasheet = oead.gsheet.parse(file_data)
    
    data['fields'] = oead_to_py(datasheet.root_fields)
    data['contents'] = oead_to_py(datasheet.values)
    
    return data

def parse_all(version):

    file_list = list_datasheet(version)
    
    for file in file_list:
        with open(file, 'rb') as data_file:
            datasheet = oead.Bytes(data_file.read())
        with open(f'gsheet/datasheets/{version}/{file.split("\\")[-2]}/{file.split("\\")[-1].replace('.gsheet', '.yaml')}', 'w') as yaml_file:
            yaml_file.write(yaml.dump(read_sheet(datasheet), Dumper = yaml.Dumper, indent = 2))

parse_all('100')
parse_all('101')