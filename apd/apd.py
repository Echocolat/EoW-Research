import struct

def readInt(f):
    return int.from_bytes(f.read(4), 'little')

def getStr(buf, offset):
    if offset == -1:
        return None
    s = []
    while buf[offset] != 0:
        s.append(buf[offset])
        offset += 1
    return bytes(s).decode('ascii')

def parse_apd(version):

    file = open(f'{version}/romfs/region_common/actor/ActorProfile.apd', 'rb')
    header = file.read(12)
    uk1 = file.read(4 * header[5])

    actorlistbuf_size = readInt(file)
    actorlistbuf = file.read(actorlistbuf_size)

    strbuf_size = readInt(file)
    strbuf = file.read(strbuf_size)

    rest = file.read()
    file.close()

    file = open(f'apd/{version}/ActorProfile.txt', 'w')

    for offset in range(0, actorlistbuf_size, 0x10):

        a, b, index, strOffset, e, shunOffset = struct.unpack('<BBhiii', actorlistbuf[offset: offset + 0x10])
        file.write(getStr(strbuf, strOffset) + '\n')
    file.close()

parse_apd('100')
parse_apd('101')
parse_apd('102')