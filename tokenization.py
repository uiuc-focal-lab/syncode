"""tokenization.py: an example of a shim to turn bytelevel encoded strings to bytes and back. See tokenization.md for details."""


def bytes_to_unicode():
    """
    Returns list of utf-8 byte and a corresponding list of unicode strings.
    The reversible bpe codes work on unicode strings.
    This means you need a large # of unicode characters in your vocab if you want to avoid UNKs.
    When you're at something like a 10B token dataset you end up needing around 5K for decent coverage.
    To avoid that, we want lookup tables between utf-8 bytes and unicode strings.
    And avoids mapping to whitespace/control characters the bpe code barfs on.
    """
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))


def enbyte(token: str) -> bytes:
    """Turn a token into the corresponding bytes.

    Example:
    --------
    >>> enbyte('âĪ')
    b'\xe2\x88'
    """
    dict_bytes = {v: k for k, v in bytes_to_unicode().items()}
    return bytes([dict_bytes[c] for c in token])


def debyte(array: bytes) -> list[str]:
    """Turn bytes into a list of the corresponding code points.

    Example:
    --------
    >>> xdebyte(b'\xe2\x88')
    ['â', 'Ī']
    """
    byte_dict = bytes_to_unicode()
    return [byte_dict[b] for b in array]
