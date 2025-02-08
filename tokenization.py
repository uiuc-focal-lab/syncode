"""tokenization.py: an example of a shim to turn bytelevel encoded strings to bytes and back. See tokenization.md for details."""

from huggingface_hub import HfApi
from transformers import AutoTokenizer
from joblib import delayed, Parallel
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
        prefix, text, postfix = self.split_bytes(byte_text)
        return (
            self.iterative_lookup(prefix)
            + self.tokenizer.encode(text, add_special_tokens=False)
            + self.iterative_lookup(postfix)
        )

    def split_bytes(self, byte_text: bytes) -> (bytes, str, bytes):
        """Break the text into valid and invalid UTF-8.

        Returns: (prefix, text, postfix) where text is the encoded valid text and prefix and postfix are invalid bytes.

        Examples:
        ---------
        >>> tok = ByteTokenizer.from_pretrained('gpt2')
        >>> tok.split_bytes('你好吗？'.encode()[1:-2])
        (b'\xbd\xa0', '好吗', b'\xef')
        """
        # FIXME: This implementation isn't terribly readable, but it takes
        # advantage of python's builtin utf-8 capabilities. Unfortunately we
        # have to handle broken utf-8 strings, detecting where they break, and
        # the way to access that information is through the exception
        # system. An alternative interface would make it easier to deal with
        # partially-valid utf-8 strings. which would let this function be
        # rewritten more readably.
        prefix = b""
        postfix = b""
        text = ""

        try:
            text = byte_text.decode()
        except UnicodeDecodeError as err:
            if err.start == 0:
                # Failure began at first byte.
                i = 0
                while i < len(err.object) and bin(err.object[i])[2:4] == "10":
                    # Scan forward to the next uft-8 start byte (doesn't begin with '10').
                    i += 1
                prefix = byte_text[:i]
                byte_text = byte_text[i:]

        try:
            text = byte_text.decode()
        except UnicodeDecodeError as err:
            postfix = byte_text[err.start :]
            text = byte_text[: err.start].decode()

        # If at the end we only got bytes in the prefix, treat it as the postfix.
        if prefix and not text and not postfix:
            return b"", "", prefix

        return prefix, text, postfix

    def iterative_lookup(self, key: str) -> list[int]:
        """Return the item or sequence of items key indexes in byte_vocab."""
        items = []
        while key:
            # Repeat until key has become an empty string.
            for i in range(len(key), 0, -1):
                # Find largest prefix in dictionary.
                try:
                    items.append(self.byte_vocab[key[:i]])
                except KeyError:
                    continue
                # If all went well, truncate key from the beginning.
                key = key[i:]
                break

        return items


api = HfApi()


def check(model):
    if not model.gated:
        try:
            tok = AutoTokenizer.from_pretrained(model.id)
            return (model.id, "ByteLevel" in repr(tok.backend_tokenizer.pre_tokenizer))
        except:
            return (model.id, "failed")

        else:
            return (model.id, "gated")


# byte_level =
# Parallel(n_jobs=16)(delayed(check)(model) for model in api.list_models(task='text-generation'))
