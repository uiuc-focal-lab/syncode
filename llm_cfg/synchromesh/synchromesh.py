import copy
import regex
import synchromesh.trie as trie
from synchromesh.completion_engine import CompletionEngine, LarkCompletionEngine

class StreamingCSD:
    '''Streaming implementation of Constrained Semantic Decoding

    Use this if you want full control when sampling from the model
    (e.g., if you're using Hugging Face models, not OpenAI).

    This is the suggested approach:

    While not done sampling:
    - Predict distribution over next token from the language model.
    - Sample a token.
    - Check if can_token_follow returns True.
    -- If so, call feed_prediction and continue.
    -- Otherwise, call get_valid_tokens(), sample from that support set,
       then feed_prediction and continue.

    The reason for this is that can_token_follow is more efficient
    than get_valid_tokens (which iterates over the vocabulary, although
    with very heavy pruning). Thus, the fewer calls to get_valid_tokens()
    you can do, the better.
    '''

    def __init__(self,
                 completion_engine: CompletionEngine,
                 lm_vocabulary: list[str],
                 prefix: str = ''):
        self._trie = trie.Trie.from_vocabulary(lm_vocabulary)
        self._vocab = lm_vocabulary
        self._completion_engine = completion_engine
        self._completion_points: dict[str, regex.Pattern] = {}
        self._completion_points[''] = completion_engine.complete('')

        self.init_stream(prefix=prefix)

    def init_stream(self, prefix: str = ''):
        self._prefix_tokens = []
        self._prefix_str = prefix

    def can_token_follow(self, t: int):
        return is_prefix_valid(self._completion_engine,
                               copy.copy(self._completion_points),
                               self._prefix_str + self._vocab[t])

    def feed_prediction(self, t: int):
        self._prefix_tokens.append(t)
        self._prefix_str += self._vocab[t]

    def get_valid_tokens(self) -> list[int]:
        return self._trie.antimonotonic_filter(
                lambda t: is_prefix_valid(self._completion_engine,
                                          copy.copy(self._completion_points),
                                          self._prefix_str + t)
            )

    def get_current_prediction(self) -> str:
        return self._prefix_str

    def get_current_prediction_tokens(self) -> list[int]:
        return self._prefix_tokens

    def fast_forward(self):
        while not self._completion_engine.is_complete(self._prefix_str):
            v = self.get_valid_tokens()
            if len(v) == 1:
                self.feed_prediction(v[0])
                if self._completion_engine.is_complete(self._prefix_str):
                    break
            else:
                break

def is_prefix_valid(completion_engine: CompletionEngine,
                    completion_points,
                    s: str) -> bool:
    # 1- Find longest completion point that is a prefix of s.
    completion_point_indices = []
    for i in range(len(s)+1):
        if s[:i] in completion_points:
            completion_point_indices.append(i)
    
    longest_completion_point = 0
    if len(completion_point_indices) > 0:
        longest_completion_point = completion_point_indices[-1]

    # 2- Take the 'remainder'.
    completion_point_regex = completion_points[s[:longest_completion_point]]
    remainder = s[longest_completion_point:]

    if remainder == '':
        return True

    # print('Completion point:', s[:longest_completion_point])
    # print('Completion point regex:', completion_point_regex)
    # print('Remainder:', remainder)

    max_match_index = None

    # 3- Feed it character by character to the regex given by the completion point, and handle 3 cases:
    for i in range(len(remainder)):
        # print('i:', i, completion_point_regex.fullmatch(remainder[:i]))
        # print('Cur regex', completion_point_regex)
        # print('Current remainder:', remainder[:i])
        
        # If we have a violation of the regex.
        # BUG Removed: This will not work since partial match will always return True in many cases (e.g., '""".*"""').
        # if not completion_point_regex.fullmatch(remainder[:i+1], partial=True):
        
        # Check if we have a full match up to the previous character.
        if completion_point_regex.fullmatch(remainder[:i+1]):
            max_match_index = i+1
    
    # print(completion_point_regex)
    # print(repr(remainder))

    if max_match_index != None:
        # We found another completion point, reduce the problem and call recursively.
        new_completion_point = s[:longest_completion_point] + remainder[:max_match_index]
        new_completion_point_regex = completion_engine.complete(new_completion_point)
        completion_points[new_completion_point] = new_completion_point_regex
        return is_prefix_valid(completion_engine, completion_points, s)

    # TODO fix: This is not correct, since the partial match will always return True in many cases (e.g., '""".*"""')
    # We need a partial match implementation that checks if the prefix of the regex matches the remainder.
    is_partial_match = completion_point_regex.fullmatch(remainder, partial=True) != None

    if not is_partial_match:
        print('Not partial match:', repr(s))
        print(completion_point_regex, remainder)
    return is_partial_match

# def test_streaming_csd():
#     json_grammar = r"""
#         ?value: dict
#             | list
#             | string
#             | SIGNED_NUMBER      -> number
#             | "true"             -> true
#             | "false"            -> false
#             | "null"             -> null

#         list : "[" [value ("," value)*] "]"

#         dict : "{" [pair ("," pair)*] "}"
#         pair : string ":" value

#         string : "\"" /Some long string here that is fixed/ "\""

#         %import common.SIGNED_NUMBER
#         """

#     comp_engine = LarkCompletionEngine(json_grammar, 'dict', False)
#     lm = RandomLanguageModel()

#     csd = StreamingCSD(comp_engine, lm.vocabulary())

#     import time
#     start_time = time.time()

#     while not comp_engine.is_complete(csd.get_current_prediction()):
#         continuation, _ = lm.predict_unconstrained(csd.get_current_prediction(),
#                                                    max_tokens=1)
#         tokens = lm.tokenize(continuation)

#         if csd.can_token_follow(tokens[0]):
#             csd.feed_prediction(tokens[0])
#         else:
#             valid_tokens = csd.get_valid_tokens()
#             tokens, _ = lm.predict_token(csd.get_current_prediction(),
#                                          valid_tokens)
#             csd.feed_prediction(tokens[0])

#         s = csd.get_current_prediction()

#         if len(s) > 500:
#             break

#         csd.fast_forward()

#     delta = time.time() - start_time

#     print('Predicted:', repr(csd.get_current_prediction()))
#     print('Throughput:', len(csd.get_current_prediction_tokens()) / delta, 'tokens/s')
