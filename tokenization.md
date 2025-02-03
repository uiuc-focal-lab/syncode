Computers deal with numbers, but humans deal with text. The tokenizer is the component of an LLM that converts between the numbers the model interacts with and the text the humans interact with. This blog post explains a peculiar corner of some really-existing tokenizers.


# Characters, graphemes, codepoints, encodings, bytes, oh my!

This section introduces <a href="#orgbc9aeac">code point</a>​s, <a href="#org816fad7">character</a>​s, and <a href="#org93aaf4f">character encoding scheme</a>​s. I include the relevant concepts from the Unicode Standard&rsquo;s glossary (Commitee 2025) in a footnote.[^1] I will attempt to use these terms assiduously as they are defined in the Unicode Standard, even though these meanings are not always intuitive. An <a href="#org18ea2ee">abstract character</a> is a unit of information used for the storage and manipulation of text. A <a href="#orgbc9aeac">code point</a> is a number. An <a href="#orgda6772d">encoded character</a> is a mapping between an <a href="#org18ea2ee">abstract character</a> and a <a href="#orgbc9aeac">code point</a>. I will represent <a href="#orgbc9aeac">code point</a>​s as hexidecimal numbers preceded by &ldquo;U+&rdquo;.

> 你 is an <a href="#org18ea2ee">abstract character</a>, pronounced *nǐ* and meaning &ldquo;you&rdquo;.
> 
> U+4F60 is a <a href="#orgbc9aeac">code point</a>, a number whose decimal value is 20320.
> 
> The mapping 你 ↔ U+4F60 is an <a href="#orgda6772d">encoded character</a>, indicating that under the Unicode Standard, the <a href="#org18ea2ee">abstract character</a> 你 is uniquely associated with the <a href="#orgbc9aeac">code point</a> U+4F60.

We can represent these <a href="#orgbc9aeac">code point</a>​s in the computer in many different ways. A system of mapping from <a href="#orgbc9aeac">code point</a>​s to a binary representation in memory is called a <a href="#org93aaf4f">character encoding scheme</a>. For a number of practical and historical reasons, the dominant <a href="#org93aaf4f">character encoding scheme</a> is UTF-8,[^2] which, as of 2025, is used by 98.5% of all websites.[^3]

Here is a worked example:

|                              | 1        | 2        | 3        | 4        |
|------------------------------|----------|----------|----------|----------|
| Abstract character sequence: | 你       | 好       | 吗       | ？       |
| Code point​s:                 | U+4F60   | U+597D   | U+5417   | U+FF1F   |
| UTF-8:                       | E4 BD A0 | E5 A5 BD | E5 90 97 | EF BC 9F |

In the computer, the bytes represented on the last row will be stored in the file. When the user opens the file, the program used will recognize the encoding as UTF-8, map the bytes to the <a href="#orgbc9aeac">code point</a>​s, then render the <a href="#orgbc9aeac">code point</a>​s using the user&rsquo;s selected font.

# Tokenization[^4]

Humans interact with text, which is built out of characters. As we have seen above, the internal representation of these characters is not trivial or obvious, but the layers of abstraction used to display text to the user and to take it in from them are well understood. Transformer-based language models, on the other hand, interact with embedding vectors. Typically these are encapsulated as input ids, or token indices.[^5] An input id is an integer drawn from a bounded range, usually from about 30k to 120k unique integers. These integers index a lookup table of embedding vectors, one per input id.

The tokenizer is the component that maps between text the user sees and input ids the model sees. Tokenization is the process of converting text into input ids, and detokenization is the inverse conversion from input ids to text.[^6] In principle, this operation is homomorphic, which (Geng et al. 2024) define as follows:

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

We&rsquo;re already getting into strange territory: this is a single <a href="#org816fad7">character</a>, but we get two input ids. This seems counter-intuitive, since we&rsquo;d expect an input id to be at least one <a href="#org816fad7">character</a> big. When we detokenize the pair we get back what we expect.

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


# Everything you&rsquo;ve been told is a lie

So far I have elided the conversion from <a href="#org816fad7">character</a> sequences to input ids by saying that the tokenizer maps from one to the other. This isn&rsquo;t quite true: in practice, many tokenizers break the text into chunks of characters, then turn those chunks into input ids. Those chunks are tokens properly speaking, and they&rsquo;re what&rsquo;s learned by Byte Pair Encoding.

Let&rsquo;s revisit our devilish ∀ example, using some APIs from Huggingface we haven&rsquo;t had the opportunity to use yet: in addition to mapping between characters and input ids, we can map between input ids and the characters they represent.

```python
>> tokenizer.convert_ids_to_tokens([24861])
['âĪ']
```

```python
>>> tokenizer.onvert_ids_to_tokens([222])
['Ģ']
```

```python
>>> tokenizer.convert_ids_to_tokens([24861, 222])
['âĪ', 'Ģ']
```

```python
>>> tokenizer.convert_ids_to_tokens([24861])+ tokenizer.convert_ids_to_tokens([222])
['âĪ', 'Ģ']
```

What happens if we try to convert these tokens to strings?

```python
>>> tokenizer.convert_tokens_to_string(['âĪ'])
"�"
```

```python
>>> tokenizer.convert_tokens_to_string(['Ģ'])
"�"
```

We get back the same nonsense characters we had before, with no ∀ in sight. This is exceedingly bizarre. Where are these strange characters coming from? Astonishingly, the tokenizer is able to reconstruct the <a href="#org816fad7">character</a> from the concatenated tokens&#x2026;

```python
>>> tokenizer.convert_tokens_to_string(['âĪ'] + ['Ģ'])
"∀"
```

even if we cut the tokens apart into single characters.

```python
>>> tokenizer.convert_tokens_to_string(['â'] + ['Ī'] + ['Ģ'])
"∀"
```

Where is this strange behavior coming from? We&rsquo;ve chased it down to these weird mappings between input ids, tokens, and strings, but where doe these odd characters that make up the tokens come from?


# Bytes to <a href="#orgbc9aeac">Code Point</a>​s

The ultimate explanation is found in the following code, which comes from the GPT-2 repository.[^7] A Rust translation appears HuggingFace&rsquo;s tokenizer library.[^8]

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

The GPT-2 paper does not mention this (Radford et al. 2019), nor are the commit messages that add the code to GPT-2 or tokenizers very informative. A form of this code is included in tiktoken to provide legacy support for GPT-2.[^9] As far as I can tell, none of the other tokenizers for newer OpenAI models have this behavior. However, several models still display this behavior: the Codegen series, the Llama series, and DeepSeek AI&rsquo;s models (including DeepSeek-R1) all act this way. This behavior is documented in tokenizer&rsquo;s repository.[^10][^11]

There are two questions to answer at this point: why do we do this, and what does this do? It is easier to begin by answering the &ldquo;what&rdquo; question; once we know what is happening we will be able to explain why we are doing it by referencing what the result of this transformation is.

Simply, this is a one-to-one map from byte values to unicode code points. This is a devilish hack that makes many of the tokens in the vocabulary look like random noise and is the source of the strange behavior we observed in the previous section. When the tokenizer receives a series of bytes in UTF-8, it passes each byte through this dictionary. The bytes that represent visible characters of ASCII, 21<sub>16</sub> through 7E<sub>16</sub>, are mapped to themselves. The other bytes, both those that represent invisible ASCII characters (whitespace and control characters) are mapped to other <a href="#orgbc9aeac">code point</a>​s in the Unicode codespace.

For readability, I define the forward and backward dictionaries like so:

```python
byte_dict = bytes_to_unicode()
dict_byte = {v: k for k, v in byte_dict.items()} # Inverse mapping.
```

Now we can begin to explore the case we examined above. Let&rsquo;s begin by getting the <a href="#orgbc9aeac">code point</a> representing each of the bytes in the UTF-8 encoding of ∀.

```python
>>> [byte_dict[byte] for byte in '∀'.encode()]
['â', 'Ī', 'Ģ']
```

We can confirm by passing these characters through the inverse mapping and representing them as hexadecimal bytes.

```python
>>> [bytes([dict_byte[char]]) for char in ['â', 'Ī', 'Ģ']]
[b'\xe2', b'\x88', b'\x80']
```

This is exactly the three bytes of the UTF-8 encoding of ∀:

```python
>>> '∀'.encode()
b'\xe2\x88\x80'
```

This trick turns each byte of the input into the corresponding <a href="#orgbc9aeac">code point</a>. That way we can represent the input as Unicode code points and work with it as a string in the space of the <a href="#org816fad7">character</a> abstraction. We can learn the byte pair encodings beginning with a 256-member vocabulary, since we have one for each byte.


# BPE

Byte pair encoding is a compression algorithm. It finds most-frequently appearing pairs of adjacent bytes in the input data with a byte that was not in the original data. Along with the compressed data, the algorithm writes out a table of pair substitutions (Gage 1994).

(Sennrich, Haddow, and Birch 2016) introduced byte pair encoding to natural language processing as a way to represent an open vocabulary of a language through a fixed-size vocabulary of <a href="#org816fad7">character</a> sequences, avoiding out-of-vocabulary errors while efficiently representing the input text. (Berglund and van der Merwe 2023) provides a formal analysis of the algorithm and the problem it solves. The current fastest implementation of the algorithm scales linearly in the length of its input (Van Antwerpen and Neubeck 2024).


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

[^1]: <https://www.unicode.org/glossary/index.html>
> *<a id="org18ea2ee">Abstract Character</a>.* A unit of information used for the organization, control, or representation of textual data.
> 
> *<a id="org816fad7">Character</a>*. (1) The smallest component of written language that has semantic value; refers to the abstract meaning and/or shape, rather than a specific shape (see also <a href="#org224b976">glyph</a>), though in code tables some form of visual representation is essential for the reader’s understanding. (2) Synonym for <a href="#org18ea2ee">abstract character</a>. (3) The basic unit of encoding for the Unicode <a href="#org816fad7">character</a> encoding.
> 
> *<a id="org92871f3">Character Encoding Form</a>.* Mapping from a <a href="#orga7073fd">character set</a> definition to the actual code units used to represent the data.
> 
> *<a id="org93aaf4f">Character Encoding Scheme</a>.* A <a href="#org92871f3">character encoding form</a> plus byte serialization. There are seven <a href="#org816fad7">character</a> encoding schemes in Unicode: UTF-8, UTF-16, UTF-16BE, UTF-16LE, UTF-32, UTF-32BE, and UTF-32LE.
> 
> *<a id="orga7073fd">Character Set</a>.* A collection of elements used to represent textual information.
> 
> *<a id="orgbc9aeac">Code Point</a>.* (1) Any value in the Unicode codespace; that is, the range of integers from 0 to 10FFFF16. (See definition D10 in Section 3.4, Characters and Encoding.) Not all code points are assigned to encoded characters. See <a href="#orgbc9aeac">code point</a> type. (2) A value, or position, for a <a href="#org816fad7">character</a>, in any coded <a href="#orga7073fd">character set</a>.
> 
> *<a id="orgda6772d">Encoded character</a>*. An association (or mapping) between an <a href="#org18ea2ee">abstract character</a> and a <a href="#orgbc9aeac">code point</a>. 
> 
> *<a id="org224b976">Glyph</a>.* (1) An abstract form that represents one or more <a href="#org224b976">glyph</a> images. (2) A synonym for <a href="#org0f74265">glyph image</a>. In displaying Unicode <a href="#org816fad7">character</a> data, one or more glyphs may be selected to depict a particular <a href="#org816fad7">character</a>. These glyphs are selected by a rendering engine during composition and layout processing.
> 
> *<a id="org0f74265">Glyph Image</a>.* The actual, concrete image of a <a href="#org224b976">glyph</a> representation having been rasterized or otherwise imaged onto some display surface.
> 
> *<a id="org8300249">Grapheme</a>.* (1) A minimally distinctive unit of writing in the context of a particular writing system. For example, ‹b› and ‹d› are distinct graphemes in English writing systems because there exist distinct words like big and dig. Conversely, a lowercase italiform letter a and a lowercase Roman letter a are not distinct graphemes because no word is distinguished on the basis of these two different forms. (2) What a user thinks of as a <a href="#org816fad7">character</a>.

[^2]: The details of how UTF-8 encodings are computed for a given <a href="#orgbc9aeac">code point</a> are not significant to this blog post. The interested reader is directed to (Commitee 2025, 3 .) for details and (Pike and Thompson 1993) for an early account of the encoding scheme. As always, the [relevant Wikipedia page](https://en.wikipedia.org/wiki/UTF-8) is also excellent.

[^3]: <https://w3techs.com/technologies/cross/character_encoding/ranking>

[^4]: This discussion is based on (Geng et al. 2024) and (Cognetta and Okazaki 2024).

[^5]: This is huggingface&rsquo;s terminology. See <https://huggingface.co/docs/transformers/glossary#input-ids>.

[^6]: Confusingly, the huggingface API exposes these procedures as `tokenizer.encode` and `tokenizer.decode` respectively. To prevent name collisions with the concepts in Unicode, I will refer to these as tokenization and detokenization within the text.

[^7]: <https://github.com/openai/gpt-2/blob/9b63575ef42771a015060c964af2c3da4cf7c8ab/src/encoder.py#L9>

[^8]: <https://github.com/huggingface/tokenizers/blob/c45aebd1029acfbe9e5dfe64e8b8441d9fae727a/tokenizers/src/pre_tokenizers/byte_level.rs#L14>

[^9]: <https://github.com/openai/tiktoken/blob/63527649963def8c759b0f91f2eb69a40934e468/tiktoken/load.py#L84>

[^10]: <https://github.com/huggingface/tokenizers/blob/c45aebd1029acfbe9e5dfe64e8b8441d9fae727a/docs/source/components.rst>

[^11]: The bpe crate released by GitHub works with pre-trained vocabulary lists; it does not use merges and cannot train a new byte pair encoding from a corpus: it relies on existing vocabulary lists (Van Antwerpen and Neubeck 2024). It also works directly on the underlying bytes, unlike the BPE implementation used here. Therefore it does not show this behavior.
