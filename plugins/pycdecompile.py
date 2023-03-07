import struct
import subprocess

from core import Plugin

PYTHON_MAGIC = {
    # Python 1
    20121: (1, 5),
    50428: (1, 6),

    # Python 2
    50823: (2, 0),
    60202: (2, 1),
    60717: (2, 2),
    62011: (2, 3),  # a0
    62021: (2, 3),  # a0
    62041: (2, 4),  # a0
    62051: (2, 4),  # a3
    62061: (2, 4),  # b1
    62071: (2, 5),  # a0
    62081: (2, 5),  # a0
    62091: (2, 5),  # a0
    62092: (2, 5),  # a0
    62101: (2, 5),  # b3
    62111: (2, 5),  # b3
    62121: (2, 5),  # c1
    62131: (2, 5),  # c2
    62151: (2, 6),  # a0
    62161: (2, 6),  # a1
    62171: (2, 7),  # a0
    62181: (2, 7),  # a0
    62191: (2, 7),  # a0
    62201: (2, 7),  # a0
    62211: (2, 7),  # a0

    # Python 3
    3000: (3, 0),
    3010: (3, 0),
    3020: (3, 0),
    3030: (3, 0),
    3040: (3, 0),
    3050: (3, 0),
    3060: (3, 0),
    3061: (3, 0),
    3071: (3, 0),
    3081: (3, 0),
    3091: (3, 0),
    3101: (3, 0),
    3103: (3, 0),
    3111: (3, 0),  # a4
    3131: (3, 0),  # a5

    # Python 3.1
    3141: (3, 1),  # a0
    3151: (3, 1),  # a0

    # Python 3.2
    3160: (3, 2),  # a0
    3170: (3, 2),  # a1
    3180: (3, 2),  # a2

    # Python 3.3
    3190: (3, 3),  # a0
    3200: (3, 3),  # a0
    3220: (3, 3),  # a1
    3230: (3, 3),  # a4

    # Python 3.4
    3250: (3, 4),  # a1
    3260: (3, 4),  # a1
    3270: (3, 4),  # a1
    3280: (3, 4),  # a1
    3290: (3, 4),  # a4
    3300: (3, 4),  # a4
    3310: (3, 4),  # rc2

    # Python 3.5
    3320: (3, 5),  # a0
    3330: (3, 5),  # b1
    3340: (3, 5),  # b2
    3350: (3, 5),  # b2
    3351: (3, 5),  # 3.5.2

    # Python 3.6
    3360: (3, 6),  # a0
    3361: (3, 6),  # a0
    3370: (3, 6),  # a1
    3371: (3, 6),  # a1
    3372: (3, 6),  # a1
    3373: (3, 6),  # b1
    3375: (3, 6),  # b1
    3376: (3, 6),  # b1
    3377: (3, 6),  # b1
    3378: (3, 6),  # b2
    3379: (3, 6),  # rc1

    # Python 3.7
    3390: (3, 7),  # a1
    3391: (3, 7),  # a2
    3392: (3, 7),  # a4
    3393: (3, 7),  # b1
    3394: (3, 7),  # b5

    # Python 3.8
    3400: (3, 8),  # a1
    3401: (3, 8),  # a1
    3410: (3, 8),  # a1
    3411: (3, 8),  # b2
    3412: (3, 8),  # b2
    3413: (3, 8),  # b4

    # Python 3.9
    3420: (3, 9),  # a0
    3421: (3, 9),  # a0
    3422: (3, 9),  # a0
    3423: (3, 9),  # a2
    3424: (3, 9),  # a2
    3425: (3, 9),  # a2

    # Python 3.10
    3430: (3, 10),  # a1
    3431: (3, 10),  # a1
    3432: (3, 10),  # a2
    3433: (3, 10),  # a2
    3434: (3, 10),  # a6
    3435: (3, 10),  # a7
    3436: (3, 10),  # b1
    3437: (3, 10),  # b1
    3438: (3, 10),  # b1
    3439: (3, 10),  # b1
}


class PycUtil:
    @staticmethod
    def magic_to_version(magic_word):
        if not isinstance(magic_word, int):
            magic_word = struct.unpack("<H", magic_word)[0]
        try:
            return PYTHON_MAGIC[magic_word]
        except KeyError:
            return None

    @staticmethod
    def fetch_pyc_magic(pyc_file: str):
        with open(pyc_file, 'rb') as f:
            magic = f.read(4)
        magic_word = int.from_bytes(magic[:2], 'little')
        return magic_word

    @staticmethod
    def fetch_pyc_magic_from_bytes(pyc_bytes: bytes):
        magic = pyc_bytes[:4]
        magic_word = int.from_bytes(magic[:2], 'little')
        return magic_word

    def decompile_pyc(self, fullpath: str, output_comment: str = '# Decompiled on CTFever Premium'):
        pyc_version = self.magic_to_version(self.fetch_pyc_magic(fullpath))
        if pyc_version[0] >= 3 and pyc_version[1] >= 9:
            decompiler = 'bin/pycdc'
            split_by = 2
        else:
            decompiler = 'decompyle3'
            split_by = 7
        subp = subprocess.Popen(f'{decompiler} {fullpath}', shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        output = subp.stdout.readlines()[split_by:-1]
        subp.stdout.close()
        result = ''
        for s in output:
            result += str(s.decode('utf-8'))
        return output_comment + '\r\n' + result.strip('\r\n')


class Pycdecompile(Plugin):
    def __init__(self):
        super().__init__()
        self.pyc_util = None

    def load(self):
        self.fetch_data_package(
            'https://file.i0x0i.ltd/api/v3/file/source/811/pycdc.zip'
            '?sign=dIObWXS-g2kXvl1oUDUcHB1n1BnWHVDEpfGkTYEQEZY%3D%3A0'
        )

    def unload(self):
        pass

    def activate(self):
        self.pyc_util = PycUtil()

    async def params_validater(self, params):
        if not params.get('file'):
            return 'file is required'
        file_content = await params['file'].read()
        if len(file_content) < 4:
            return 'file is required'
        if self.pyc_util.fetch_pyc_magic_from_bytes(file_content) not in PYTHON_MAGIC:
            return 'file is not a valid pyc file'
        return False

    async def decompile(self, params):
        await params.get('file').seek(0)
        file_content = await params.get('file').read()
        version = self.pyc_util.magic_to_version(self.pyc_util.fetch_pyc_magic_from_bytes(file_content))
        return {
            'version': f'{version[0]}.{version[1]}',
        }
