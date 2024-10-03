from utils import *
from enum import Enum
from pathlib import Path
from typing import Any

import csv
import os
import yaml

class Type(Enum):
    Int = 0
    _01 = 1
    _02 = 2
    String = 3
    Array = 4
    Dictionary = 5
    Struct = 6
    Numeric = 7

class VarInt:
    def __init__(self):
        self.value: int
        self.is_valid = True

def resolve_hash(hash: int) -> str:
    for row in hashes:
        if ("%08x" % hash) == row[0]:
            return row[2]
    return hash

def read_data(stream: ReadStream) -> Any:
    flag = stream.read_u8()
    if (flag >> 5) == 7:
        return read_numeric(stream, flag & 0x1f)
    value: VarInt = read_varint(stream, flag & 0x1f)
    match Type(flag >> 5):
        case Type.Int:
            return resolve_hash(value.value)
        case Type._01:
            return ~value.value
        case Type._02:
            return stream.read(value.value) # binary blob that seems to usually be float data
        case Type.String:
            return stream.read(value.value).decode("utf-8")
        case Type.Array:
            return [read_data(stream) for i in range(value.value)]
        case Type.Dictionary:
            # CRC32 hash + value
            return {read_data(stream): read_data(stream) for i in range(value.value)}
        case Type.Struct:
            return read_data(stream)
        case _:
            raise ValueError(f"Unknown type {flag >> 5}")

def read_varint(stream: ReadStream, flag: int) -> VarInt:
    result = VarInt()
    match flag:
        case 0x18:
            result.value = stream.read_u8()
        case 0x19:
            result.value = stream.read_u16(">")
        case 0x1a:
            result.value = stream.read_u32(">")
        case 0x1b:
            result.value = stream.read_u64(">")
        case 0x1c | 0x1d | 0x1e | 0x1f:
            result.is_valid = False
        case _:
            result.value = flag
    return result

def read_numeric(stream: ReadStream, flag: int) -> Any:
    match flag:
        case 0x14:
            return False
        case 0x15:
            return True
        case 0x16:
            return None # TODO is this correct
        case 0x17:
            return f"UNK_TYPE_17" # TODO figure this out
        case 0x19:
            return stream.read_f16(">")
        case 0x1a:
            return stream.read_f32(">")
        case 0x1b:
            return stream.read_f64(">")
        case _:
            raise ValueError("Invalid numeric type")

def from_binary(data: bytes) -> Any:
    stream: ReadStream = ReadStream(data)
    # BFNTPJ
    if stream.read_u32() == 0x4a50544e:
        assert stream.read_u32() == 1, "Invalid bfntpj version, must be version 1"
        stream.read(4) # idk
        size = stream.read_u32()
        assert len(data) == size + 0x10
    # BFACTR
    else:
        stream.seek(0x0)
    return read_data(stream)

def from_file(path: str) -> Any:
    return from_binary(Path(path).read_bytes())

def dump_yaml(path: str, outdir: str = "") -> Any:
    data: Any = from_file(path)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, os.path.basename(path))
    with open(f"{path}.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, f)

with open("bfactr/hashcat.txt", "r", encoding="utf-8") as f:
    hashes = list(csv.reader(f, delimiter=":"))

def list_bfactr(version):

    file_list = []
    for subdir, dirs, files in os.walk(version):
        for file in files:
            if file.endswith('.bfactr'):
                file_list.append(os.path.join(subdir, file))

    return file_list

def parse_all(version):

    file_list = list_bfactr(version)
    
    for file in file_list:
        dump_yaml(file, f"bfactr/{version}")

    dump_yaml(f"{version}/romfs/region_common/nectar/villa.bfntpj", f"bfntpj/{version}")

parse_all('100')
parse_all('101')