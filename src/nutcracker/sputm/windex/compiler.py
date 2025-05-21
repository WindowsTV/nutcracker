from __future__ import annotations

import re
from pathlib import Path

from nutcracker.sputm.script.opcodes_v5 import Variable

BREAK_OPCODE = 0x80
INCREMENT_OPCODE = 0x46
DECREMENT_OPCODE = 0xC6

_VAR_RE = re.compile(r'([VLB])\.(\d+)')


def parse_variable(token: str) -> Variable:
    match = _VAR_RE.fullmatch(token)
    if not match:
        raise ValueError(token)
    prefix, num = match.groups()
    base = {
        'V': 0,
        'L': 0x4000,
        'B': 0x8000,
    }[prefix]
    return Variable(base + int(num))


def compile_line(line: str) -> bytes:
    line = line.strip()
    if not line or line.startswith((';', 'room')):
        return b''
    if line.startswith('break-here'):
        parts = line.split()
        count = int(parts[1]) if len(parts) > 1 else 1
        return bytes([BREAK_OPCODE] * count)
    inc = re.match(r'^\+\+(\S+)$', line)
    if inc:
        var = parse_variable(inc.group(1))
        return bytes([INCREMENT_OPCODE]) + var.to_bytes()
    dec = re.match(r'^--(\S+)$', line)
    if dec:
        var = parse_variable(dec.group(1))
        return bytes([DECREMENT_OPCODE]) + var.to_bytes()
    raise NotImplementedError(f'Unsupported statement: {line}')


def compile_scu(path: Path) -> bytes:
    target = Path(path)
    data = bytearray()
    for line in target.read_text().splitlines():
        data += compile_line(line)
    return bytes(data)
