# Largely adapated from https://github.com/zeldamods/evfl
import struct
import io
import binascii
try:
    import mmh3
except ImportError:
    raise ImportError("mmh3 not found, try running pip install mmh3 then try again")

def get_string(data, offset):
    if type(data) != bytes:
        data = data.read()
    end = data.find(b'\x00', offset)
    return data[offset:end].decode('utf-8')

class Stream:
    __slots__ = ["stream"]

    def __init__(self, stream) -> None:
        self.stream = stream

    def seek(self, *args) -> None:
        self.stream.seek(*args)

    def tell(self) -> int:
        return self.stream.tell()

    def skip(self, skip_size) -> None:
        self.stream.seek(skip_size, 1)

class ReadStream(Stream):
    def __init__(self, data) -> None:
        stream = io.BytesIO(memoryview(data))
        super().__init__(stream)
        self.data = data

    def read(self, *args) -> bytes:
        return self.stream.read(*args)
    
    def read_u8(self, end="<") -> int:
        return struct.unpack(f"{end}B", self.read(1))[0]
    
    def read_u16(self, end="<") -> int:
        return struct.unpack(f"{end}H", self.read(2))[0]
    
    def read_s16(self, end="<") -> int:
        return struct.unpack(f"{end}h", self.read(2))[0]
    
    def read_u24(self, end="<") -> int:
        if end == "<":
            return struct.unpack(f"{end}I", self.read(3) + b'\x00')[0]
        else:
            return struct.unpack(f"{end}I", b'\x00' + self.read(3))[0]
        
    def read_s24(self, end="<") -> int:
        if end == "<":
            return struct.unpack(f"{end}i", self.read(3) + b'\x00')[0]
        else:
            return struct.unpack(f"{end}i", b'\x00' + self.read(3))[0]
    
    def read_u32(self, end="<") -> int:
        return struct.unpack(f"{end}I", self.read(4))[0]
    
    def read_s32(self, end="<") -> int:
        return struct.unpack(f"{end}i", self.read(4))[0]
    
    def read_u64(self, end="<") -> int:
        return struct.unpack(f"{end}Q", self.read(8))[0]
    
    def read_s64(self, end="<") -> int:
        return struct.unpack(f"{end}q", self.read(8))[0]
    
    def read_ptr(self, align=8, end="<") -> int:
        while self.stream.tell() % align != 0:
            self.read(1)
        return struct.unpack(f"{end}Q", self.read(8))[0]
    
    def read_f16(self, end="<") -> float:
        return struct.unpack(f"{end}e", self.read(2))[0]

    def read_f32(self, end="<") -> float:
        return struct.unpack(f"{end}f", self.read(4))[0]
    
    def read_f64(self, end="<") -> float:
        return struct.unpack(f"{end}d", self.read(8))[0]

    def read_string(self, offset=None, size=4): # Data should be a slice beginning at the string pool
        pos = self.stream.tell()
        if offset == None:
            if size == 4:
                ptr = self.read_u32()
            elif size == 2:
                ptr = self.read_u16()
            elif size == 8:
                ptr = self.read_u64()
            else:
                raise Exception("Please provide relative offset for other data sizes")
        else:
            ptr = offset
        string = get_string(self.stream, ptr)
        self.stream.seek(pos)
        return string

    def read_string_sarc(self):
        string = b''
        current_char = self.stream.read(1)
        while current_char != b'\x00':
            string += current_char
            current_char = self.stream.read(1)
        return string.decode('utf-8')
    
class PlaceholderWriter:
    __slots__ = ["_offset"]

    def __init__(self, offset):
        self._offset = offset

    def write(self, stream, data):
        pos = stream.tell()
        stream.seek(self._offset)
        stream.write(data)
        stream.seek(pos)

class WriteStream(Stream):
    def __init__(self, stream):
        super().__init__(stream)
        self._string_list = [] # List of strings in file
        self._strings = b'' # String pool to write to file
        self._string_refs = {} # Maps strings to relative offsets
        self._string_list_exb = [] # List of strings in file
        self._strings_exb = b'' # String pool to write to file
        self._string_refs_exb = {} # Maps strings to relative offsets

    def add_string(self, string):
        if string not in self._string_list:
            encoded = string.encode()
            self._string_list.append(string)
            self._string_refs[string] = len(self._strings)
            self._strings += encoded
            if encoded[-1:] != b'\x00': # All strings must end with a null termination character
                self._strings += b'\x00'

    def add_string_exb(self, string):
        if string not in self._string_list_exb:
            encoded = string.encode()
            self._string_list_exb.append(string)
            self._string_refs_exb[string] = len(self._strings_exb)
            self._strings_exb += encoded
            if encoded[-1:] != b'\x00': # All strings must end with a null termination character
                self._strings_exb += b'\x00'

    def write(self, data):
        self.stream.write(data)

    def write_at_offset(self, data, offset):
        pos = self.stream.tell()
        self.stream.seek(offset)
        self.write(data)
        self.stream.seek(pos)

    def align_up(self, alignment):
        while self.stream.tell() % alignment != 0:
            self.skip(1)

    def read(self, *args) -> bytes:
        return self.stream.read(*args)
    
    def read_u8(self, end="<") -> int:
        return struct.unpack(f"{end}B", self.read(1))[0]
    
    def read_u16(self, end="<") -> int:
        return struct.unpack(f"{end}H", self.read(2))[0]
    
    def read_s16(self, end="<") -> int:
        return struct.unpack(f"{end}h", self.read(2))[0]
    
    def read_u24(self, end="<") -> int:
        if end == "<":
            return struct.unpack(f"{end}I", self.read(3) + b'\x00')[0]
        else:
            return struct.unpack(f"{end}I", b'\x00' + self.read(3))[0]
        
    def read_s24(self, end="<") -> int:
        if end == "<":
            return struct.unpack(f"{end}i", self.read(3) + b'\x00')[0]
        else:
            return struct.unpack(f"{end}i", b'\x00' + self.read(3))[0]
    
    def read_u32(self, end="<") -> int:
        return struct.unpack(f"{end}I", self.read(4))[0]
    
    def read_s32(self, end="<") -> int:
        return struct.unpack(f"{end}i", self.read(4))[0]
    
    def read_u64(self, end="<") -> int:
        return struct.unpack(f"{end}Q", self.read(8))[0]
    
    def read_s64(self, end="<") -> int:
        return struct.unpack(f"{end}q", self.read(8))[0]
    
    def read_ptr(self, align=8, end="<") -> int:
        while self.stream.tell() % align != 0:
            self.read(1)
        return struct.unpack(f"{end}Q", self.read(8))[0]
    
    def read_f32(self, end="<") -> float:
        return struct.unpack(f"{end}f", self.read(4))[0]
    
    def read_f64(self, end="<") -> float:
        return struct.unpack(f"{end}d", self.read(4))[0]

    def read_string(self, offset=None, size=4): # Data should be a slice beginning at the string pool
        pos = self.stream.tell()
        if offset == None:
            if size == 4:
                ptr = self.read_u32()
            elif size == 2:
                ptr = self.read_u16()
            elif size == 8:
                ptr = self.read_u64()
            else:
                raise Exception("Please provide relative offset for other data sizes")
        else:
            ptr = offset
        string = get_string(self.stream, ptr)
        self.stream.seek(pos)
        return string

    def read_string_sarc(self):
        string = b''
        current_char = self.stream.read(1)
        while current_char != b'\x00':
            string += current_char
            current_char = self.stream.read(1)
        return string.decode('utf-8')

class SeekContext:
    def __init__(self, stream: Stream, offset: int = -1):
        self._stream = stream
        self._offset = offset
        self._jumpack = stream.tell()

    def __enter__(self):
        if self._offset != -1:
            self._stream.seek(self._offset)
        return self._offset
    
    def __exit__(self, *args):
        self._stream.seek(self._jumpack)

def u8(value):
    return struct.pack("<B", value)

def s8(value):
    return struct.pack("<b", value)

def u16(value, end="<"):
    return struct.pack(f"{end}H", value)

def s16(value, end="<"):
    return struct.pack(f"{end}h", value)

def u24(value, end="<"):
    ret = struct.pack(f"{end}I", value)
    return ret[1:] if end == ">" else ret[:-1]

def s24(value, end="<"):
    ret = struct.pack(f"{end}i", value)
    return ret[1:] if end == ">" else ret[:-1]

def u32(value, end="<"):
    return struct.pack(f"{end}I", value)

def s32(value, end="<"):
    return struct.pack(f"{end}i", value)

def u64(value, end="<"):
    return struct.pack(f"{end}Q", value)

def s64(value, end="<"):
    return struct.pack(f"{end}q", value)

def f32(value, end="<"):
    return struct.pack(f"{end}f", value)

def f64(value, end="<"):
    return struct.pack(f"{end}d", value)

def byte_custom(value, size, end="<"):
    return struct.pack(f"{end}{size}s", value)

def string(value):
    return value.encode('utf-8')

def vec3f(values, end="<"):
    ret = b''
    for value in values:
        ret += f32(value, end)
    return ret

def padding(count):
    return struct.pack(f"{count}s", b'\x00')

def hash(value):
    return mmh3.hash(value, signed=False)

def crc32(value):
    return binascii.crc32(value)