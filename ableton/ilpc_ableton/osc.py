"""Minimal OSC 1.0 message encoding/decoding (stdlib only).

Supports the type tags AbletonOSC uses: i (int32), f (float32), s (string),
b (blob), T/F (booleans), N (nil). Bundles are decoded (AbletonOSC can reply
with them) but only messages are encoded.
"""
from __future__ import annotations

import struct
from typing import Any, Iterable

OscArg = int | float | str | bool | bytes | None


def _pad(data: bytes) -> bytes:
    return data + b"\x00" * (-len(data) % 4)


def _encode_string(value: str) -> bytes:
    return _pad(value.encode("utf-8") + b"\x00")


def encode_message(address: str, args: Iterable[OscArg] = ()) -> bytes:
    if not address.startswith("/"):
        raise ValueError(f"OSC address must start with '/': {address!r}")
    tags = ","
    payload = b""
    for arg in args:
        # bool must be checked before int (bool is a subclass of int)
        if isinstance(arg, bool):
            tags += "T" if arg else "F"
        elif arg is None:
            tags += "N"
        elif isinstance(arg, int):
            if not -(2**31) <= arg < 2**31:
                raise ValueError(f"int out of int32 range: {arg}")
            tags += "i"
            payload += struct.pack(">i", arg)
        elif isinstance(arg, float):
            tags += "f"
            payload += struct.pack(">f", arg)
        elif isinstance(arg, str):
            tags += "s"
            payload += _encode_string(arg)
        elif isinstance(arg, (bytes, bytearray)):
            tags += "b"
            payload += struct.pack(">i", len(arg)) + _pad(bytes(arg))
        else:
            raise TypeError(f"Unsupported OSC argument type: {type(arg).__name__}")
    return _encode_string(address) + _encode_string(tags) + payload


def _read_string(data: bytes, offset: int) -> tuple[str, int]:
    end = data.index(b"\x00", offset)
    value = data[offset:end].decode("utf-8")
    offset = end + 1
    offset += -offset % 4
    return value, offset


def decode_message(data: bytes) -> tuple[str, list[Any]]:
    address, offset = _read_string(data, 0)
    if offset >= len(data):
        return address, []
    tags, offset = _read_string(data, offset)
    if not tags.startswith(","):
        raise ValueError("Malformed OSC message: missing type tag string")
    args: list[Any] = []
    for tag in tags[1:]:
        if tag == "i":
            args.append(struct.unpack_from(">i", data, offset)[0]); offset += 4
        elif tag == "f":
            args.append(struct.unpack_from(">f", data, offset)[0]); offset += 4
        elif tag == "d":
            args.append(struct.unpack_from(">d", data, offset)[0]); offset += 8
        elif tag == "h":
            args.append(struct.unpack_from(">q", data, offset)[0]); offset += 8
        elif tag == "s":
            value, offset = _read_string(data, offset); args.append(value)
        elif tag == "b":
            size = struct.unpack_from(">i", data, offset)[0]; offset += 4
            args.append(data[offset:offset + size]); offset += size + (-size % 4)
        elif tag == "T":
            args.append(True)
        elif tag == "F":
            args.append(False)
        elif tag == "N":
            args.append(None)
        else:
            raise ValueError(f"Unsupported OSC type tag: {tag!r}")
    return address, args


def decode_packet(data: bytes) -> list[tuple[str, list[Any]]]:
    """Decode a message or a (possibly nested) bundle into a flat list of messages."""
    if data.startswith(b"#bundle\x00"):
        messages = []
        offset = 16  # '#bundle\0' + 8-byte timetag
        while offset < len(data):
            size = struct.unpack_from(">i", data, offset)[0]; offset += 4
            messages.extend(decode_packet(data[offset:offset + size])); offset += size
        return messages
    return [decode_message(data)]
