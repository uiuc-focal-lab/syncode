Computers deal with numbers, but humans deal with text. The tokenizer is the component of an LLM that converts between the numbers the model interacts with and the text the humans interact with. This blog post explains a peculiar corner of some really-existing tokenizers.

# Incremental tokenization as a downstream application
We want to implement homomorphic detokenization as an efficiency boost. If we're doing constrained decoding, we would like to be able to detokenize one input id at a time, rather than re-detokenizing the entire string.

# Characters, graphemes, codepoints, encodings, bytes, oh my!

This section introduces code point​s, character​s, and character encoding scheme​s. I include the relevant concepts from the Unicode Standard&rsquo;s glossary (Commitee 2025) in a footnote.[^1] I will attempt to use these terms  as they are defined in the Unicode Standard, even though these meanings are not always intuitive. An abstract character is a unit of information used for the storage and manipulation of text. A code point is a number. An encoded character is a mapping between an abstract character and a code point. I will represent code point​s as hexidecimal numbers preceded by &ldquo;U+&rdquo;.

> 你 is an abstract character, pronounced *nǐ* and meaning &ldquo;you&rdquo;.
> 
> U+4F60 is a code point, a number whose decimal value is 20320.
> 
> The mapping 你 ↔ U+4F60 is an encoded character, indicating that under the Unicode Standard, the abstract character 你 is uniquely associated with the code point U+4F60.

We can represent these code point​s in the computer in many different ways. A system of mapping from code point​s to a binary representation in memory is called a character encoding scheme. For a number of practical and historical reasons, the dominant character encoding scheme is UTF-8,[^2] which, as of 2025, is used by 98.5% of all websites.[^3] Here is an example:

|                              | 1        | 2        | 3        | 4        |
|------------------------------|----------|----------|----------|----------|
| Abstract character sequence: | 你       | 好       | 吗       | ？       |
| Code point​s:                 | U+4F60   | U+597D   | U+5417   | U+FF1F   |
| UTF-8 (encoded form):        | E4 BD A0 | E5 A5 BD | E5 90 97 | EF BC 9F |

In the computer, the bytes represented on the last row will be stored in the file. When the user opens the file, the program used will recognize the encoding as UTF-8, map the bytes to the code point​s, then render the code point​s using the user&rsquo;s selected font.

The concept of "character" is intentionally left vague. The unicode standard says that what the user thinks of as a character is actually a grapheme, a minimally-distinctive unit of writing in the context of a given writing system. This is a concept from linguistics that does not necessarily map exactly on to our concept of a character. 

For the remainder of this blog post, I will be speaking of code points and their byte-encoded form. When I show a code point, I will often use the associated abstract character to visualize it. This will, in turn, be displayed to you as a certain glyph, depending on the font you are using. "Chraracter" will be used to refer to what the Unicode Standard calls an "abstract character," the basic unit of information in text. Each chraracter is identified with a unique code point.

# Tokenization[^4]

Humans interact with text, which is built out of (abstract) characters. As we have seen, however, these characters are represented in the computer's memory as a sequence of bytes, often more than one byte per character. Transformer-based language models take as their input as sequence of input ids, non-negative integers in a bounded range, and put out a probability distribution across their vocabulary of input ids. The tokenizer is the component that maps between text the user sees and input ids the model sees. Tokenization is the process of converting text into input ids, and detokenization is the inverse conversion from input ids to text.[^6]

Each input id, further, is associated with a sequence of characters known as a token. In principle, the tokenizer works by breaking the input string into tokens according to its vocabulary and then turning those tokens into their proper input ids. The first token in the vocabulary is input id 0, the second is 1, and so on. In principle, this operation is homomorphic, which (Geng et al. 2024) define as follows:
> Given two operations ⊕ and ⊙ on two alphabets Σ∗ and N∗ respectively, a function h : Σ∗ → N∗ is a string homomorphism if ∀u, v ∈ Σ∗, h(u ⊕ v) = h(u) ⊙ h(v).
Consider ⊕ to be string concatenation and ⊙ to be the concatenation of sequences of integers. This means, intuitively, that cutting a string in two, tokenizing its two parts, and appending the resulting lists of input ids will always get you the same thing you would have gotten if you had tokenized the string all at once. Similarly, the inverse homomorphism holds that if you detokenize two lists of input ids and concatenate the resulting string, then the string you get will be the same as if you had concatenated the lists of input ids and detokenized.

To clarify this, let us take some examples. Here we&rsquo;re using GPT-2&rsquo;s tokenizer (Radford et al. 2019). Let&rsquo;s begin by looking at the input ids you get from this string.

```python
>>> tokenizer.encode("Hello, tokenizing world!")
[15496, 11, 11241, 2890, 995, 0]
```

And if we detokenize, we get back the string we started with.

```python
>>> tokenizer.decode([15496, 11, 11241, 2890, 995, 0])
"Hello, tokenizing world!"
```

If we encode two parts of the string seperately, we can get back a different list of input ids.

```python
>>> tokenizer.encode("Hello, tokeniz") + tokenizer.encode("ing world!")
[15496, 11, 11241, 528, 278, 995, 0]
```

This means that tokenization, in this implementation, is not homomorphic: we just showed an example where the property was violated, to wit,
$$
tokenize(\textrm{"Hello, tokeniz"} ⊕ \textrm{"ing world!"}) \ne tokenize(\textrm{"Hello, tokeniz"}) ⊙ tokenize(\textrm{"ing world!"})
$$

(Geng et al. 2024) show by a similar example that tokenization is not homomorphic, but that the detokenization procedure is homomorphic.

```python
>>> tokenizer.decode([15496, 11, 11241] + [528, 278, 995, 0])
"Hello, tokenizing world!"
```

```python
>>> tokenizer.decode([15496, 11, 11241]) + tokenizer.decode([528, 278, 995, 0])
"Hello, tokenizing world!"
```

We get the whole string back. This example satisfies our homomorphism property described above, since concatenating strings and concatenating lists of input ids are equivalent.

$$
detokenize([15496, 11, 11241] ⊙ [528, 278, 995, 0]) = detokenize([15496, 11, 11241]) ⊕ detokenize([528, 278, 995, 0])
$$

Let&rsquo;s try a naughtier example to see whether detokenization is always homomorphic for this tokenizer.

```python
>>> tokenizer.encode('∀')
[24861, 222]
```

We&rsquo;re already getting into strange territory: this is a single character, but we get two input ids. This seems counter-intuitive, since we&rsquo;d expect an input id to be at least one character big. When we detokenize the pair we get back what we expect.

```python
>>> tokenizer.decode([24861, 222])
"∀"
```

But if we attempt to detokenize the individual input ids&#x2026;

```python
>>> tokenizer.decode([24861])
"�"
```

we get nonsense results&#x2026;

```python
>>> tokenizer.decode([222])
"�"
```

that don&rsquo;t behave the way we want them to.

```python
>>> tokenizer.decode([24861]) + tokenizer.decode([222])
"��"
```

What&rsquo;s going wrong? Why does this particular example break the homomorphism of detokenization? Are there other examples that behave a similar way? To answer this we&rsquo;ll have to go deeper into what&rsquo;s going on under the hood.

# Clustering characters and byte-pair encoding
You might have noticed that the number of input ids produced by the tokenizer is often far smaller than the number of abstract characters (i.e. code points) that the tokenizer takes in. This is because, in an auto-regressive model, the time it takes to generate a token is constant, regardless of the number of characters the token represents. We can speed up generation by simply making each token represent more characters, because the cost of supporting a larger vocabulary is memory, which we can easily trade for time. The question becomes: given a corpus, how do we efficiently cluster its characters into tokens that will most efficiently represent the text?

One common approach is to use byte pair encoding, which is a compression algorithm. It finds most-frequently appearing pairs of adjacent bytes in the input data with a byte that was not in the original data. Along with the compressed data, the algorithm writes out a table of pair substitutions (Gage 1994). (Sennrich, Haddow, and Birch 2016) introduced byte pair encoding to natural language processing as a way to represent an open vocabulary of a language through a fixed-size vocabulary of character sequences, avoiding out-of-vocabulary errors while efficiently representing the input text. (Berglund and van der Merwe 2023) provides a formal analysis of the algorithm and the problem it solves. The current fastest implementation of the algorithm scales linearly in the length of its input (Van Antwerpen and Neubeck 2024) when working with a pre-computed vocabulary.

Vocabularies computed with byte pair encoding have the property that all of their tokens are either initial tokens provided by the user or concatenations of other tokens. This means that an initial vocabulary of 256 tokens, one for each byte, is adequate to represent all text. Remember that UTF-8 (and for that matter all other character encoding schemes) represent all code points as a sequence of bytes. By learning how to cluster these bytes, we can produce a vocabulary that both efficiently encodes texts from an identical, independent distribution (in the sense that the number of tokens needed is minimized) and avoids any unknown characters (since any input can always be tokenized as a sequence of bytes, and we know that the vocabulary will at least contain bytes).

# Bytes to Code Point​s
The challenge with byte pair encoding is that the tokens that result are not guarateed to be valid UTF-8. Consider our initial example:

|                              | 1        | 2        | 3        | 4        |
|------------------------------|----------|----------|----------|----------|
| Abstract character sequence: | 你       | 好       | 吗       | ？       |
| Code point​s:                 | U+4F60   | U+597D   | U+5417   | U+FF1F   |
| UTF-8 (encoded form):        | E4 BD A0 | E5 A5 BD | E5 90 97 | EF BC 9F |

There is no reason our vocabulary shouldn't include the tokens E4BD and A0E5, neither of which are valid utf-8 (remember, it's one of the properties of utf-8 that a sequence of bytes either is or isn't valid utf-8, and cutting a single code point's encoding always results in invalid utf-8). This would make it difficult for code that expected the input to be a valid utf-8 string to cope with the output of the model: if the model were cut off in its generation, say, the result might end with dangling bytes that don't make up a complete utf-8 encoded form of a code point (e.g. the model generated something ending with the token E4BD); worse, a token might be ragged on both ends, in the sense that neither end of the token is the end of a code point (e.g. A0A5DBE5).

A hacky solution is to turn each byte in the input into a Unicode Code Point.[^hacky] This way, we can treat each token in the vocabulary as a valid utf-8 string while still getting the efficiency advantages from byte-level byte pair encoding. The reference implementation of this dictionary is found in the following code, which comes from the GPT-2 repository.[^7] A Rust translation appears HuggingFace&rsquo;s tokenizer library.[^8] The GPT-2 paper does not mention this (Radford et al. 2019), nor are the commit messages that add the code to GPT-2 or tokenizers very informative. A form of this code is included in tiktoken to provide legacy support for GPT-2.[^9] As far as I can tell, none of the other tokenizers for newer OpenAI models use this hack. However, several popular models still do  use this behavior: the Codegen series, the Llama series, and DeepSeek AI&rsquo;s models (including DeepSeek-R1) all act this way. This behavior is documented in tokenizer&rsquo;s repository.[^10][^11]

```python
def bytes_to_unicode():
  """
  Returns list of utf-8 byte and a corresponding list of unicode strings.
  The reversible bpe codes work on unicode strings.
  This means you need a large # of unicode characters in your vocab if you want to avoid UNKs.
  When you're at something like a 10B token dataset you end up needing around 5K for decent coverage.
  To avoid that, we want lookup tables between utf-8 bytes and unicode strings.
  And avoids mapping to whitespace/control characters the bpe code barfs on.
  """
  bs = list(range(ord("!"), ord("~")+1))+list(range(ord("¡"), ord("¬")+1))+list(range(ord("®"), ord("ÿ")+1))
  cs = bs[:]
  n = 0
  for b in range(2**8):
      if b not in bs:
          bs.append(b)
          cs.append(2**8+n)
          n += 1
  cs = [chr(n) for n in cs]
  return dict(zip(bs, cs))
```

This code generates a dictionary mapping bytes to Unicode Code Points. The dictionary maps the bytes that name printable, non-whitespace ASCII characters (21<sub>16</sub> through 7E<sub>16</sub>) to that ASCII character's code point[^ascii] and all other bytes to some arbitrary non-whitespace code point. This allows us to transform a sequence of bytes into a sequence of code points, which we can, in turn, encode as utf-8 bytes. 

Let's get an intuition for how this behaves with some examples. For readability, I define a dictionary `byte_dict` that maps from bytes to code points, and a dictionary `dict_byte` that maps from code points to bytes, like so:

```python
byte_dict = bytes_to_unicode()
dict_byte = {v: k for k, v in byte_dict.items()} # Inverse mapping.
```

Let&rsquo;s begin by getting the code point representing each of the bytes in the UTF-8 encoding of ∀.

```python
>>> [byte_dict[byte] for byte in '∀'.encode()]
['â', 'Ī', 'Ģ']
```

We can confirm that we are getting what we expect by passing these characters through the inverse mapping and representing them as hexadecimal bytes.

```python
>>> [bytes([dict_byte[char]]) for char in ['â', 'Ī', 'Ģ']]
[b'\xe2', b'\x88', b'\x80']
```

This is exactly the three bytes of the UTF-8 encoding of ∀:

```python
>>> '∀'.encode()
b'\xe2\x88\x80'
```

This trick turns each byte of the input into the corresponding code point. That way we can represent the input as Unicode code points and work with it as a string in the space of the character abstraction. We can learn the byte pair encodings beginning with a 256-member vocabulary of code points, since we have one for each byte.

Because we have so many overloaded terms ("encode", "tokenize",...) I will coin some neologisms for this transformation: turning the bytes into code points I will call `debyte`ing, and turning the code points back into bytes I will call `enbyte`ing. All of the tokens in the model's vocabulary are already `debyte`d, which explains the presence of tokens like "çļĦæĦŁåıĹ" in GPT2's vocabulary (which `enbyte`s to "的感受", meaning, roughly, "'s feelings"[^mandarin]).

# Tricky corners of the huggingface tokenizer API

This transformation, converting the bytes of the input string to code points that represent those bytes, is handled tacitly by those tokenizers that do it. The `encode` and `decode` methods of huggingface's tokenizers do this for the user, turning the string into input ids and back without revealing this underlying hack. 

Secretly, however, the tokenizer first `debyte`s the input string before breaking it into tokens. This internal representation is accessible through the series of methods `convert_ids_to_tokens`, `convert_tokens_to_ids`, and `convert_tokens_to_string`. The last, `convert_tokens_to_string`, is equivalent to what I have called `enbyte`, above. The methods that convert ids to tokens and back map between the `debyte`d token and its index in the vocabulary.

Here are some examples using the input ids we got from ∀:
```python
>> tokenizer.convert_ids_to_tokens([24861])
['âĪ']
>>> tokenizer.convert_ids_to_tokens([222])
['Ģ']
>>> tokenizer.convert_ids_to_tokens([24861, 222])
['âĪ', 'Ģ']
>>> tokenizer.convert_ids_to_tokens([24861]) + tokenizer.convert_ids_to_tokens([222])
['âĪ', 'Ģ']
```
This example shows that `convert_ids_to_tokens` is, infact, homomorphic: in the space of `debyte`d tokens, concatenating input ids then detokenizing (`convert_ids_to_tokens`ing) is equivalent to detokenizing then concatenating. Then we can use the method `convert_tokens_to_string` to recover the `enbyte`d string we'd like to show the user:
```python
>>> tokenizer.convert_tokens_to_string(['âĪ', 'Ģ'])
'∀'
```

# Huggingface tokenizer's cobwebby corners
Many of the models on the huggingface hub use a tokenizer implemented using huggingface's tokenizers library, or a tokenizer implemented directly in their transformers library as a fallback, and tend to use the ByteLevel pre-tokenizer and associated decoder in their stack.[^13] This is the component of a huggingface tokenizer object that implements the transformation described in the previous section. In particular, the component implements the operations that I have called `enbyte` and `debyte`.

When the user passes a string in to the tokenizer, the `ByteLevel` pre-tokenizer `debyte`s that string before passing it to the rest of the tokenizer.[^pretoken] When the tokenizer returns a string to the user, it is `enbyte`d, and all unknown bytes are turned to the Unicode code point U+FFFD, called REPLACEMENT CHARACTER, which appears as � to the user.[^12] This is what we got back when we attempted to detokenize the fragments of the ∀ character earlier and is what breaks homomorphism in detokenization.

# Conclusion
We have seen an unintuitive aspect of several really-existing tokenizers that breaks the property of homomorphism. We discussed the reason for this behavior, explored why it is done this way, and showed how to see what the tokenizer is doing under the hood. This explains the presence of strange characters in models' vocabularies. This will be useful, in particular, for those implementing constrained generation for models whose vocabularies are `debyte`d: in order to correctly match the restriction the user provides, implementors will have to either `debyte` the user's constraints or `enbyte` the model's vocabulary.

# Bibliography

Antwerpen, Hendrik van, and Alexander Neubeck. 2024. “So Many Tokens, so Little Time: Introducing a Faster, More Flexible Byte-Pair Tokenizer.” GitHub Blog, December. <https://github.blog/ai-and-ml/llms/so-many-tokens-so-little-time-introducing-a-faster-more-flexible-byte-pair-tokenizer/>.

Berglund, Martin, and Brink van der Merwe. 2023. “Formalizing BPE Tokenization.” Electronic Proceedings in Theoretical Computer Science 388 (September). Open Publishing Association: 16–27. https://doi.org/10.4204/eptcs.388.4.

Cognetta, Marco, and Naoaki Okazaki. 2024. “Tokenization as Finite-State Transduction.” <https://arxiv.org/abs/2410.15696>.

Commitee, Unicode Technical. 2025. “Unicode Standard.” Unicode, Inc. <https://www.unicode.org/versions/latest/>.

Gage, Philip. 1994. “A New Algorithm for Data Compression.” <https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm>.

Geng, Saibo, Sankalp Gambhir, Chris Wendler, and Robert West. 2024. “Byte BPE Tokenization as an Inverse String Homomorphism.” <https://arxiv.org/abs/2412.03160>.

Pike, Rob, and Ken Thompson. 1993. “Hello World, or Καλημέρα Κόσμε, or こんにちは 世界.” Bell Labs. <https://9p.io/sys/doc/utf.pdf>.

Radford, Alec, Jeff Wu, Rewon Child, David Luan, Dario Amodei, and Ilya Sutskever. 2019. “Language Models Are Unsupervised Multitask Learners.” OpenAI. <https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf>.

Sennrich, Rico, Barry Haddow, and Alexandra Birch. 2016. “Neural Machine Translation of Rare Words with Subword Units.” In Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), edited by Katrin Erk and Noah A. Smith, 1715–25. Berlin, Germany: Association for Computational Linguistics. https://doi.org/10.18653/v1/P16-1162.


# Footnotes

[^1]:
	> *Abstract Character.* A unit of information used for the organization, control, or representation of textual data.
	> 
	> *Character*. (1) The smallest component of written language that has semantic value; refers to the abstract meaning and/or shape, rather than a specific shape (see also glyph), though in code tables some form of visual representation is essential for the reader’s understanding. (2) Synonym for abstract character. (3) The basic unit of encoding for the Unicode character encoding.
	> 
	> *Character Encoding Form.* Mapping from a character set definition to the actual code units used to represent the data.
	> 
	> *Character Encoding Scheme.* A character encoding form plus byte serialization. There are seven character encoding schemes in Unicode: UTF-8, UTF-16, UTF-16BE, UTF-16LE, UTF-32, UTF-32BE, and UTF-32LE.
	> 
	> *Character Set.* A collection of elements used to represent textual information.
	> 
	> *Code Point.* (1) Any value in the Unicode codespace; that is, the range of integers from 0 to 10FFFF16. (See definition D10 in Section 3.4, Characters and Encoding.) Not all code points are assigned to encoded characters. See code point type. (2) A value, or position, for a character, in any coded character set.
	> 
	> *Encoded character*. An association (or mapping) between an abstract character and a code point. 
	> 
	> *Glyph.* (1) An abstract form that represents one or more glyph images. (2) A synonym for glyph image. In displaying Unicode character data, one or more glyphs may be selected to depict a particular character. These glyphs are selected by a rendering engine during composition and layout processing.
	> 
	> *Glyph Image.* The actual, concrete image of a glyph representation having been rasterized or otherwise imaged onto some display surface.
	> 
	> *Grapheme.* (1) A minimally distinctive unit of writing in the context of a particular writing system. For example, ‹b› and ‹d› are distinct graphemes in English writing systems because there exist distinct words like big and dig. Conversely, a lowercase italiform letter a and a lowercase Roman letter a are not distinct graphemes because no word is distinguished on the basis of these two different forms. (2) What a user thinks of as a character. <https://www.unicode.org/glossary/index.html>

[^2]: The details of how UTF-8 encodings are computed for a given code point are not significant to this blog post. The interested reader is directed to (Commitee 2025, 3 .) for details and (Pike and Thompson 1993) for an early account of the encoding scheme. As always, the [relevant Wikipedia page](https://en.wikipedia.org/wiki/UTF-8) is also excellent.

[^3]: <https://w3techs.com/technologies/cross/character_encoding/ranking>

[^4]: This discussion is based on (Geng et al. 2024) and (Cognetta and Okazaki 2024).

[^5]: This is huggingface&rsquo;s terminology. See <https://huggingface.co/docs/transformers/glossary#input-ids>.

[^6]: Confusingly, the huggingface API exposes these procedures as `tokenizer.encode` and `tokenizer.decode` respectively. To prevent name collisions with the concepts in Unicode, I will refer to these as tokenization and detokenization within the text.

[^7]: <https://github.com/openai/gpt-2/blob/9b63575ef42771a015060c964af2c3da4cf7c8ab/src/encoder.py#L9>

[^8]: <https://github.com/huggingface/tokenizers/blob/c45aebd1029acfbe9e5dfe64e8b8441d9fae727a/tokenizers/src/pre_tokenizers/byte_level.rs#L14>

[^9]: <https://github.com/openai/tiktoken/blob/63527649963def8c759b0f91f2eb69a40934e468/tiktoken/load.py#L84>

[^10]: <https://github.com/huggingface/tokenizers/blob/c45aebd1029acfbe9e5dfe64e8b8441d9fae727a/docs/source/components.rst>

[^11]: The bpe crate released by GitHub works with pre-trained vocabulary lists; it does not use merges and cannot train a new byte pair encoding from a corpus: it relies on existing vocabulary lists (Van Antwerpen and Neubeck 2024). It also works directly on the underlying bytes, unlike the BPE implementation used here. Therefore it does not show this behavior.

[^hacky]: This should feel promiscuous and dirty, since we are mixing levels of abstraction. We are turning the bytes we use to encode code points back into code points, which themselves will be encoded by bytes. This is made especially confusing by the appearance of the abstract characters involved, as we shall see.

[^Ascii]: US cultural imperialism means that the ASCII character codes are the same as the equivalent Unicode code point (e.g. the abstract character "a" is 0x61 in ASCII and U+61 in Unicode. In utf-8, the code point U+61 is encoded as the byte 61). This is all baked into the Unicode Standard and the utf-8 encoding scheme in a way that privileges ASCII texts by giving them the most efficient encodings.

[^mandarin]: Any Mandarin speakers, please correct me. I am basing this translation off of mdbg.net and google translate!

[^pretoken]: This is implemented at https://github.com/huggingface/tokenizers/blob/c45aebd1029acfbe9e5dfe64e8b8441d9fae727a/tokenizers/src/pre_tokenizers/byte_level.rs#L145.

[^12]: The `enbyte`-ing happens at [this](https://github.com/huggingface/tokenizers/blob/c45aebd1029acfbe9e5dfe64e8b8441d9fae727a/tokenizers/src/pre_tokenizers/byte_level.rs#L166) spot in the tokenizers source, and the replacement with U+FFFD happens during [this](https://github.com/huggingface/tokenizers/blob/c45aebd1029acfbe9e5dfe64e8b8441d9fae727a/tokenizers/src/pre_tokenizers/byte_level.rs#L174) call to the Rust standard library's String function `from_utf8_lossy` https://doc.rust-lang.org/std/string/struct.String.html#method.from_utf8_lossy.

[^13]: TODO: design a script to check which of the models on the huggingface hub use this component. So far I've manually confirmed that deepseek-ai/DeepSeek-R1, mistralai/Mistral-Small-24B-Instruct-2501, meta-llama/Llama-3.3-70B-Instruct, and Qwen/Qwen2.5-VL-7B-Instruct do it.
