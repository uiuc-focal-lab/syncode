"""bytetokenizerr.py: an example of a shim to turn bytelevel encoded strings to bytes and back. See tokenization.md for details.


The `ByteTokenizer` class implements a homomorphic wrapper raound a Huggingface tokenizer.

Examples:
---------

We purposely do not decode the byte representation into the character
representation in this example. Python's str datatype is an array of code
points. This array is encoded by utf-8 bytes for storage. Since `ByteTokenizer`
operates at the byte level, the behavior is more explicit when representing the
output at the byte level.

>>> '你好吗？'.encode()
b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef\xbc\x9f'
>>> b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef\xbc\x9f'.decode()
'你好吗？'
>>> tok = ByteTokenizer.from_pretrained('deepseek-ai/deepseek-r1')
>>> tok.encode(b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef\xbc\x9f')
[30594, 3467, 1148]
>>> tok.encode(b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef\xbc\x9f'[:7])
[30594, 164]
>>> tok.encode(b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef\xbc\x9f'[7:])
[241, 248, 1148]
>>> tok.decode([30594, 164] + [241, 248, 1148])
b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef\xbc\x9f'
>>> (tok.decode([30594, 164]) + tok.decode([241, 248, 1148])).decode('utf-8')
b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef\xbc\x9f'

"""
from transformers import AutoTokenizer
from functools import reduce, cache


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


@cache
def enbyte(token: str) -> bytes:
    """Turn a token into the corresponding bytes.

    Example:
    --------
    >>> enbyte('âĪ')
    b'\xe2\x88'
    """
    dict_bytes = {v: k for k, v in bytes_to_unicode().items()}
    # Deepseek-ai uses U+FF5C ｜ FULLWIDTH VERTICAL LINE and U+2581 ▁ LOWER ONE
    # EIGHTH BLOCKin their special tokens (<｜begin▁of▁sentence｜> and the
    # like) rather than the ASCII equivalents U+007C | VERTICAL LINE and U+005F
    # _ LOW LINE. With apologies to the Deepseek team, replace the characters
    # with their ASCII equivalents to improve compatibility.
    token = token.replace('｜', '|').replace('▁', '_')
    return bytes([dict_bytes[c] for c in token])


def debyte(array: bytes) -> list[str]:
    """Turn bytes into a list of the corresponding code points.

    Example:
    --------
    >>> debyte(b'\xe2\x88')
    ['â', 'Ī']
    """
    byte_dict = bytes_to_unicode()
    return [byte_dict[b] for b in array]


class ByteTokenizer(AutoTokenizer):
    """A class to convert a tokenizer that works on code points to one that works on bytes. Expects a tokenizer that has a ByteLevel preprocessor."""

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.byte_vocab = dict(
            map(lambda p: (enbyte(p[0]), p[1]), self.tokenizer.vocab.items())
        )
        self.vocab_byte = {v: k for k, v in self.byte_vocab.items()}

    @classmethod
    def from_pretrained(cls, model_id):
        tokenizer = super().from_pretrained(model_id)
        return cls(tokenizer)

    def decode(self, token_ids: list[int]) -> bytes:
        """Decode token_ids as bytes.

        Examples:
        ---------
        >>> tok = ByteTokenizer.from_pretrained('gpt2')
        >>> tok.decode([19526, 254, 25001, 121, 28938, 245, 171, 120, 253]).decode()
        '你好吗？'

        >>> tok = ByteTokenizer.from_pretrained('gpt2')
        >>> tok.decode([121, 254, 25001, 121, 28938, 245, 171])
        b'\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef'
        >>> '你好吗？'.encode()[1:-2]
        b'\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97\xef'
        """
        return reduce(
            lambda p, q: p + q, map(lambda id: self.vocab_byte[id], token_ids)
        )

    def encode(self, byte_text: bytes) -> list[int]:
        """Encode to token_ids, with bytes.

        Examples:
        ---------
        >>> tok = ByteTokenizer.from_pretrained('gpt2')
        >>> tok.encode('你好吗？'.encode())
        [19526, 254, 25001, 121, 28938, 245, 171, 120, 253]

        >>> tok = ByteTokenizer.from_pretrained('gpt2')
        >>> tok.encode('你好吗？'.encode()[1:-2])
        [121, 254, 25001, 121, 28938, 245, 171]
        """
        """Return the item or sequence of items key indexes in byte_vocab."""
        # FIXME: This is a very naive implementation of tokenization. There are
        # probably ways to speed this up.
        input_ids = []
        while byte_text:
            # Repeat until text has become an empty string.
            for i in range(len(byte_text), 0, -1):
                # Find largest prefix in dictionary.
                try:
                    input_ids.append(self.byte_vocab[byte_text[:i]])
                except KeyError:
                    continue
                # If all went well, truncate text from the beginning.
                byte_text = byte_text[i:]
                break

        return input_ids
