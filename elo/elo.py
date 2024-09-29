import glob
import struct
import math
import pprint
from numpy import float32
import binascii
import zlib
import re
import os
import json

def roundUp(x):
    return (x+0x10)//0x10*0x10

def assertZero(xs):
    for x in xs:
        assert x == 0

sectionSpecs = [
    {'name':'actors','itemsize':0x7C,'endalignment':True,'fields':'<fffhhfffffffffhhhhhhhhhhhhhhhhihbbIhhhhhhhhhhhhbbh'},
    {'name':'empty1','itemsize':-1,'endalignment':True},
    {'name':'unk2','itemsize':4,'endalignment':True,'fields':'<I'},
    {'name':'unk3','itemsize':2,'endalignment':True,'fields':'<h'},
    {'name':'unk4','itemsize':0x18,'endalignment':True},
    {'name':'unk5','itemsize':0xC,'endalignment':True},
    {'name':'unk6','itemsize':2,'endalignment':True},
    {'name':'unk7','itemsize':0x30,'endalignment':True},
    {'name':'unk8','itemsize':0x30,'endalignment':True},
    {'name':'unk9','itemsize':4,'endalignment':True},
    {'name':'unk10','itemsize':8,'endalignment':True,'fields':'<hhi'},
    {'name':'unk11','itemsize':4,'endalignment':True},
    {'name':'unk12','itemsize':0x30,'endalignment':True},
    {'name':'unk13','itemsize':0xC,'endalignment':True},
    {'name':'unk14','itemsize':0x30,'endalignment':True},
    {'name':'unk15','itemsize':0x20,'endalignment':True},
    {'name':'unk16','itemsize':8,'endalignment':True},
    {'name':'unk17','itemsize':2,'endalignment':True},
    {'name':'unk18','itemsize':8,'endalignment':True},
    {'name':'unk19','itemsize':0x20,'endalignment':True},
    {'name':'unk20','itemsize':8,'endalignment':True},
    {'name':'unk21','itemsize':4,'endalignment':True},
    {'name':'unk22','itemsize':8,'endalignment':True},
    {'name':'empty23','itemsize':-1,'endalignment':True},
    {'name':'unk24','itemsize':0x10,'endalignment':True},
    {'name':'unk25','itemsize':0x10,'endalignment':False},
    {'name':'actorParams','itemsize':8,'endalignment':False,'fields':'<i4s'},
    {'name':'unk27','itemsize':4,'endalignment':False},
    {'name':'empty28','itemsize':-1,'endalignment':False},
    {'name':'unk29','itemsize':2,'endalignment':False},
    {'name':'stringOffsets','itemsize':4,'endalignment':True,'fields':'<i'},
    {'name':'strings','itemsize':None,'endalignment':True},
]

def get_hashes(version):

    hashes = {}

    for line in open(f'apd/{version}/ActorProfile.txt'):
        hashes[binascii.crc32(line[:-1].encode('ascii'))] = line[:-1]

    with open(f'elo/hashes/{version}.json', 'w') as json_file:
        json_file.write(json.dumps(hashes, indent = 2))

    return hashes

def parse_elo(file_data, version):

    hashes = get_hashes(version)

    assert file_data[:8] == b'elo \x01\x00\x01\x01'
    assert struct.unpack('<I', file_data[8:0xC]) == (len(file_data),)
    headers = []
    for i in range(32):
        count, start = struct.unpack('<II', file_data[0xC+8*i:0xC+8*(i+1)])
        headers.append({'count':count,'start':start})
    assert file_data[0x10C:0x120] == b'LVLE\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    assert headers[0]['count'] == headers[3]['count']
    assert headers[2]['count'] == headers[10]['count']
    assert headers[30]['count'] == headers[31]['count']
    assert headers[17]['count'] == 0
    headers[17]['count'] = headers[16]['count']

    output = {}

    for i in range(32):
        if i == 31: # string section
            items = []
            offset = headers[i]['start']
            for _ in range(headers[i]['count']):
                #assert (offset-headers[i]['start']) in output[30]
                s = []
                while file_data[offset] != 0:
                    s.append(file_data[offset])
                    offset += 1
                offset += 1
                items.append(bytes(s).decode('ascii'))
            headers[i]['end'] = offset
        else:
            if sectionSpecs[i]['itemsize'] == -1: # 1, 23, 28 never have any data
                assert headers[i]['count'] == 0
            headers[i]['end'] = headers[i]['start'] + headers[i]['count']*sectionSpecs[i]['itemsize']
            items = []
            for j in range(headers[i]['count']):
                items.append(file_data[headers[i]['start'] + j*sectionSpecs[i]['itemsize']:headers[i]['start'] + (j+1)*sectionSpecs[i]['itemsize']])
                if sectionSpecs[i].get('fields'):
                    items[-1] = list(struct.unpack(sectionSpecs[i]['fields'], items[-1]))
                    for k in range(len(items[-1])):
                        if type(items[-1][k]) == float:
                            items[-1][k] = float(str(float32(items[-1][k])))
                    if len(items[-1]) == 1:
                        items[-1] = items[-1][0]
                else:
                    items[-1] = " ".join(["%02X"%x for x in items[-1]])
        if sectionSpecs[i]['endalignment']:
            headers[i]['paddedEnd'] = roundUp(headers[i]['end'])
        else:
            headers[i]['paddedEnd'] = headers[i]['end']
        assertZero(file_data[headers[i]['end']:headers[i]['paddedEnd']])
        if i == 31:
            assert headers[i]['paddedEnd'] == len(file_data)
        else:
            assert headers[i]['paddedEnd'] == headers[i+1]['start']
        output[i] = items

    for i,item in enumerate(output[26]):
        assert item[0] <= 4
        if item[0] == 0: # null
            assert item[1] == b'\x00\x00\x00\x00'
            output[26][i] = None
        elif item[0] == 1: # bool
            output[26][i] = [False, True][struct.unpack('<i', item[1])[0]]
        elif item[0] == 2: # int
            output[26][i] = struct.unpack('<i', item[1])[0]
        elif item[0] == 3: # float
            output[26][i] = float(str(float32(struct.unpack('<f', item[1])[0])))
        elif item[0] == 4: # string
            output[26][i] = output[31][struct.unpack('<i', item[1])[0]]
            
    for i,item in enumerate(output[0]):
        item[34] = hashes[item[34]]
        params = []
        for j in range(8):
            params.append(output[26][item[22+j]])
        while len(params) > 0 and params[-1] is None:
            params.pop()
        params0 = []
        for j in range(0,8,2):
            assert item[14+j+1] <= 4
            params0.append((output[26][item[14+j]], item[14+j+1]))
        while len(params0) > 0 and params0[-1] == (None, 4):
            params0.pop()
        output[0][i] = [item[:3]] + item[3:14] + [params0] + [params] + item[30:] # group the params
        
    for i,item in enumerate(output[2]):
        output[2][i] = hashes[item]

    true_output = {"Actors": [], "ActorParams": output[26], "Full data": output}

    actors = output[0]
    for actor in actors:
        true_output["Actors"].append({
            "Translate": {
                "X": actor[0][0],
                "Y": actor[0][1],
                "Z": actor[0][2]
            },
            "Actor name": actor[18],
            "Actor params": actor[13]
        })
        #true_output['ZZZActorFullData'].append(actor)

    return true_output

def parse_all_elo(version):

    for file in os.listdir(version + '/romfs/region_common/level'):
        if file.endswith('.elo'):
            with open(version + '/romfs/region_common/level/' + file, 'rb') as file_:
                file_data = file_.read()
            parsed_full = parse_elo(file_data, version)
            parsed_actors = parsed_full
            del parsed_actors['Full data']
            with open(f"elo/{version}/full/{file.replace('.elo', '.json')}", "w") as json_file:
                json_file.write(json.dumps(parsed_full, indent = 2))
            with open(f"elo/{version}/actors/{file.replace('.elo', '.json')}", "w") as json_file:
                json_file.write(json.dumps(parsed_actors, indent = 2))

parse_all_elo("100")
parse_all_elo("101")