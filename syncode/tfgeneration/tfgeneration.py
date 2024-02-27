# import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer

# import copy
# import inspect
# import warnings
# from dataclasses import dataclass
# from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

# import torch
# import torch.distributed as dist
# from torch import nn

# from transformers import (
#     GenerationConfig,
#     LogitsProcessorList,
#     StoppingCriteriaList,
#     PreTrainedModel,
#     # Any other specific classes or utilities you need from the library...
# )
# import transformers

# METADATA_FIELDS = ("_from_model_config", "_commit_hash", "_original_object_hash", "transformers_version")
# # ModelOutput
# @dataclass
# class GenerateDecoderOnlyOutput():
#     """
#     Outputs of decoder-only generation models, when using non-beam methods.

#     Args:
#         sequences (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
#             The generated sequences. The second dimension (sequence_length) is either equal to `max_length` or shorter
#             if all batches finished early due to the `eos_token_id`.
#         scores (`tuple(torch.FloatTensor)` *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Processed prediction scores of the language modeling head (scores for each vocabulary token before SoftMax)
#             at each generation step. Tuple of `torch.FloatTensor` with up to `max_new_tokens` elements (one element for
#             each generated token), with each tensor of shape `(batch_size, config.vocab_size)`.
#         attentions (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size, num_heads, generated_length, sequence_length)`.
#         hidden_states (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size, generated_length, hidden_size)`.
#         past_key_values (`tuple(tuple(torch.FloatTensor)))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
#             NOTE: some models have a different `past_key_values` format, confirm with the model's documentation.
#             Usually a Tuple (one element for each layer of the decoder) of tuples (two elements, key tensor and value
#             tensor). The first Tuple is of length `config.n_layers`, with each tuple having 2 tensors of shape
#             `(batch_size, num_heads, sequence_length, embed_size_per_head)`) and optionally if
#             `config.is_encoder_decoder=True` 2 additional tensors of shape `(batch_size, num_heads,
#             encoder_sequence_length, embed_size_per_head)`.
#     """

#     sequences: torch.LongTensor = None
#     scores: Optional[Tuple[torch.FloatTensor]] = None
#     attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None

# # ModelOutput
# @dataclass
# class GenerateEncoderDecoderOutput():
#     """
#     Outputs of encoder-decider generation models, when using non-beam methods.

#     Args:
#         sequences (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
#             The generated sequences. The second dimension (sequence_length) is either equal to `max_length` or shorter
#             if all batches finished early due to the `eos_token_id`.
#         scores (`tuple(torch.FloatTensor)` *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Processed prediction scores of the language modeling head (scores for each vocabulary token before SoftMax)
#             at each generation step. Tuple of `torch.FloatTensor` with up to `max_new_tokens` elements (one element for
#             each generated token), with each tensor of shape `(batch_size, config.vocab_size)`.
#         encoder_attentions (`tuple(torch.FloatTensor)`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple of `torch.FloatTensor` (one for each layer of the decoder) of shape `(batch_size, num_heads,
#             sequence_length, sequence_length)`.
#         encoder_hidden_states (`tuple(torch.FloatTensor)`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
#             Tuple of `torch.FloatTensor` (one for the output of the embeddings + one for the output of each layer) of
#             shape `(batch_size, sequence_length, hidden_size)`.
#         decoder_attentions (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size, num_heads, generated_length, sequence_length)`.
#         cross_attentions (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size, num_heads, generated_length, sequence_length)`.
#         decoder_hidden_states (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size, generated_length, hidden_size)`.
#         past_key_values (`tuple(tuple(torch.FloatTensor)))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
#             NOTE: some models have a different `past_key_values` format, confirm with the model's documentation.
#             Usually a Tuple (one element for each layer of the decoder) of tuples (two elements, key tensor and value
#             tensor). The first Tuple is of length `config.n_layers`, with each tuple having 2 tensors of shape
#             `(batch_size, num_heads, sequence_length, embed_size_per_head)`) and optionally if
#             `config.is_encoder_decoder=True` 2 additional tensors of shape `(batch_size, num_heads,
#             encoder_sequence_length, embed_size_per_head)`.
#     """

#     sequences: torch.LongTensor = None
#     scores: Optional[Tuple[torch.FloatTensor]] = None
#     encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
#     encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
#     decoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     cross_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     decoder_hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None

# # ModelOutput
# @dataclass
# class GenerateBeamDecoderOnlyOutput():
#     """
#     Outputs of decoder-only generation models, when using beam methods.

#     Args:
#         sequences (`torch.LongTensor` of shape `(batch_size*num_return_sequences, sequence_length)`):
#             The generated sequences. The second dimension (sequence_length) is either equal to `max_length` or shorter
#             if all batches finished early due to the `eos_token_id`.
#         sequences_scores (`torch.FloatTensor` of shape `(batch_size*num_return_sequences)`, *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Final beam scores of the generated `sequences`.
#         scores (`tuple(torch.FloatTensor)` *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Beam transition scores for each vocabulary token at each generation step. Beam transition scores consisting
#             of log probabilities of tokens conditioned on log softmax of previously generated tokens in this beam.
#             Tuple of `torch.FloatTensor` with up to `max_new_tokens` elements (one element for each generated token),
#             with each tensor of shape `(batch_size*num_beams*num_return_sequences, config.vocab_size)`.
#         beam_indices (`torch.LongTensor`, *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Beam indices of generated token id at each generation step. `torch.LongTensor` of shape
#             `(batch_size*num_return_sequences, sequence_length)`.
#         attentions (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size*num_beams, num_heads, generated_length, sequence_length)`.
#         hidden_states (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size*num_beams*num_return_sequences, generated_length, hidden_size)`.
#         past_key_values (`tuple(tuple(torch.FloatTensor)))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
#             NOTE: some models have a different `past_key_values` format, confirm with the model's documentation.
#             Usually a Tuple (one element for each layer of the decoder) of tuples (two elements, key tensor and value
#             tensor). The first Tuple is of length `config.n_layers`, with each tuple having 2 tensors of shape
#             `(batch_size, num_heads, sequence_length, embed_size_per_head)`) and optionally if
#             `config.is_encoder_decoder=True` 2 additional tensors of shape `(batch_size, num_heads,
#             encoder_sequence_length, embed_size_per_head)`.
#     """

#     sequences: torch.LongTensor = None
#     sequences_scores: Optional[torch.FloatTensor] = None
#     scores: Optional[Tuple[torch.FloatTensor]] = None
#     beam_indices: Optional[torch.LongTensor] = None
#     attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None

# # ModelOutput
# @dataclass
# class GenerateBeamEncoderDecoderOutput():
#     """
#     Outputs of encoder-decoder generation models, when using beam methods.

#     Args:
#         sequences (`torch.LongTensor` of shape `(batch_size*num_return_sequences, sequence_length)`):
#             The generated sequences. The second dimension (sequence_length) is either equal to `max_length` or shorter
#             if all batches finished early due to the `eos_token_id`.
#         sequences_scores (`torch.FloatTensor` of shape `(batch_size*num_return_sequences)`, *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Final beam scores of the generated `sequences`.
#         scores (`tuple(torch.FloatTensor)` *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Beam transition scores for each vocabulary token at each generation step. Beam transition scores consisting
#             of log probabilities of tokens conditioned on log softmax of previously generated tokens in this beam.
#             Tuple of `torch.FloatTensor` with up to `max_new_tokens` elements (one element for each generated token),
#             with each tensor of shape `(batch_size*num_beams, config.vocab_size)`.
#         beam_indices (`torch.LongTensor`, *optional*, returned when `output_scores=True` is passed or when `config.output_scores=True`):
#             Beam indices of generated token id at each generation step. `torch.LongTensor` of shape
#             `(batch_size*num_return_sequences, sequence_length)`.
#         encoder_attentions (`tuple(torch.FloatTensor)`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple of `torch.FloatTensor` (one for each layer of the decoder) of shape `(batch_size, num_heads,
#             sequence_length, sequence_length)`.
#         encoder_hidden_states (`tuple(torch.FloatTensor)`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
#             Tuple of `torch.FloatTensor` (one for the output of the embeddings + one for the output of each layer) of
#             shape `(batch_size*num_beams*num_return_sequences, sequence_length, hidden_size)`.
#         decoder_attentions (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size*num_beams*num_return_sequences, num_heads, generated_length,
#             sequence_length)`.
#         cross_attentions (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_attentions=True` is passed or `config.output_attentions=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size, num_heads, generated_length, sequence_length)`.
#         decoder_hidden_states (`tuple(tuple(torch.FloatTensor))`, *optional*, returned when `output_hidden_states=True` is passed or when `config.output_hidden_states=True`):
#             Tuple (one element for each generated token) of tuples (one element for each layer of the decoder) of
#             `torch.FloatTensor` of shape `(batch_size*num_beams*num_return_sequences, generated_length, hidden_size)`.
#         past_key_values (`tuple(tuple(torch.FloatTensor)))`, *optional*, returned when `use_cache=True` is passed or when `config.use_cache=True`):
#             NOTE: some models have a different `past_key_values` format, confirm with the model's documentation.
#             Usually a Tuple (one element for each layer of the decoder) of tuples (two elements, key tensor and value
#             tensor). The first Tuple is of length `config.n_layers`, with each tuple having 2 tensors of shape
#             `(batch_size, num_heads, sequence_length, embed_size_per_head)`) and optionally if
#             `config.is_encoder_decoder=True` 2 additional tensors of shape `(batch_size, num_heads,
#             encoder_sequence_length, embed_size_per_head)`.
#     """

#     sequences: torch.LongTensor = None
#     sequences_scores: Optional[torch.FloatTensor] = None
#     scores: Optional[Tuple[torch.FloatTensor]] = None
#     beam_indices: Optional[torch.LongTensor] = None
#     encoder_attentions: Optional[Tuple[torch.FloatTensor]] = None
#     encoder_hidden_states: Optional[Tuple[torch.FloatTensor]] = None
#     decoder_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     cross_attentions: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     decoder_hidden_states: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
#     past_key_values: Optional[Tuple[Tuple[Tuple[torch.FloatTensor]]]] = None


# # Equivalent classes (kept for retrocompatibility purposes)
# GreedySearchDecoderOnlyOutput = GenerateDecoderOnlyOutput
# ContrastiveSearchDecoderOnlyOutput = GenerateDecoderOnlyOutput
# SampleDecoderOnlyOutput = GenerateDecoderOnlyOutput

# ContrastiveSearchEncoderDecoderOutput = GenerateEncoderDecoderOutput
# GreedySearchEncoderDecoderOutput = GenerateEncoderDecoderOutput
# SampleEncoderDecoderOutput = GenerateEncoderDecoderOutput

# BeamSearchDecoderOnlyOutput = GenerateBeamDecoderOnlyOutput
# BeamSampleDecoderOnlyOutput = GenerateBeamDecoderOnlyOutput

# BeamSearchEncoderDecoderOutput = GenerateBeamEncoderDecoderOutput
# BeamSampleEncoderDecoderOutput = GenerateBeamEncoderDecoderOutput

# GreedySearchOutput = Union[GreedySearchEncoderDecoderOutput, GreedySearchDecoderOnlyOutput]
# SampleOutput = Union[SampleEncoderDecoderOutput, SampleDecoderOnlyOutput]
# BeamSearchOutput = Union[BeamSearchEncoderDecoderOutput, BeamSearchDecoderOnlyOutput]
# BeamSampleOutput = Union[BeamSampleEncoderDecoderOutput, BeamSampleDecoderOnlyOutput]
# ContrastiveSearchOutput = Union[ContrastiveSearchEncoderDecoderOutput, ContrastiveSearchDecoderOnlyOutput]

# # Typing shortcuts
# GenerateNonBeamOutput = Union[GenerateDecoderOnlyOutput, GenerateEncoderDecoderOutput]
# GenerateBeamOutput = Union[GenerateBeamDecoderOnlyOutput, GenerateBeamEncoderDecoderOutput]
# GenerateOutput = Union[GenerateNonBeamOutput, GenerateBeamOutput]

# # ExplicitEnum
# class GenerationMode():
#     """
#     Possible generation modes, downstream of the [`~generation.GenerationMixin.generate`] method.
#     """

#     # Non-beam methods
#     CONTRASTIVE_SEARCH = "contrastive_search"
#     GREEDY_SEARCH = "greedy_search"
#     SAMPLE = "sample"
#     ASSISTED_GENERATION = "assisted_generation"
#     # Beam methods
#     BEAM_SEARCH = "beam_search"
#     BEAM_SAMPLE = "beam_sample"
#     CONSTRAINED_BEAM_SEARCH = "constrained_beam_search"
#     GROUP_BEAM_SEARCH = "group_beam_search"


# #__________________________________________________________________________________________________________________________________________________________
# #__________________________________________________________________________________________________________________________________________________________
# #__________________________________________________________________________________________________________________________________________________________



# class CustomModelWrapper:
#     def __init__(self, model):
#         self.model = model

#     def __getattr__(self, name):
#         # This method is called whenever an attribute is accessed on this object.
#         # If it's not found, we try to find it in the underlying model.
#         if name == "generate":
#             # Return the custom generate method if trying to access 'generate'
#             return self.__dict__[name]
#         return getattr(self.model, name)

#     def generateTF(
#         self,
#         inputs: Optional[torch.Tensor] = None,
#         generation_config: Optional[GenerationConfig] = None,
#         logits_processor: Optional[LogitsProcessorList] = None,
#         stopping_criteria: Optional[StoppingCriteriaList] = None,
#         prefix_allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], List[int]]] = None,
#         synced_gpus: Optional[bool] = None,
#         assistant_model: Optional["PreTrainedModel"] = None,
#         streamer: Optional["BaseStreamer"] = None,
#         negative_prompt_ids: Optional[torch.Tensor] = None,
#         negative_prompt_attention_mask: Optional[torch.Tensor] = None,
#         **kwargs,
#     ) -> Union[GenerateOutput, torch.LongTensor]:
#         # print(generation_config)
#         r"""

#         Generates sequences of token ids for models with a language modeling head.

#         <Tip warning={true}>

#         Most generation-controlling parameters are set in `generation_config` which, if not passed, will be set to the
#         model's default generation configuration. You can override any `generation_config` by passing the corresponding
#         parameters to generate(), e.g. `.generate(inputs, num_beams=4, do_sample=True)`.

#         For an overview of generation strategies and code examples, check out the [following
#         guide](../generation_strategies).

#         </Tip>

#         Parameters:
#             inputs (`torch.Tensor` of varying shape depending on the modality, *optional*):
#                 The sequence used as a prompt for the generation or as model inputs to the encoder. If `None` the
#                 method initializes it with `bos_token_id` and a batch size of 1. For decoder-only models `inputs`
#                 should of in the format of `input_ids`. For encoder-decoder models *inputs* can represent any of
#                 `input_ids`, `input_values`, `input_features`, or `pixel_values`.
#             generation_config (`~generation.GenerationConfig`, *optional*):
#                 The generation configuration to be used as base parametrization for the generation call. `**kwargs`
#                 passed to generate matching the attributes of `generation_config` will override them. If
#                 `generation_config` is not provided, the default will be used, which had the following loading
#                 priority: 1) from the `generation_config.json` model file, if it exists; 2) from the model
#                 configuration. Please note that unspecified parameters will inherit [`~generation.GenerationConfig`]'s
#                 default values, whose documentation should be checked to parameterize generation.
#             logits_processor (`LogitsProcessorList`, *optional*):
#                 Custom logits processors that complement the default logits processors built from arguments and
#                 generation config. If a logit processor is passed that is already created with the arguments or a
#                 generation config an error is thrown. This feature is intended for advanced users.
#             stopping_criteria (`StoppingCriteriaList`, *optional*):
#                 Custom stopping criteria that complement the default stopping criteria built from arguments and a
#                 generation config. If a stopping criteria is passed that is already created with the arguments or a
#                 generation config an error is thrown. If your stopping criteria depends on the `scores` input, make
#                 sure you pass `return_dict_in_generate=True, output_scores=True` to `generate`. This feature is
#                 intended for advanced users.
#             prefix_allowed_tokens_fn (`Callable[[int, torch.Tensor], List[int]]`, *optional*):
#                 If provided, this function constraints the beam search to allowed tokens only at each step. If not
#                 provided no constraint is applied. This function takes 2 arguments: the batch ID `batch_id` and
#                 `input_ids`. It has to return a list with the allowed tokens for the next generation step conditioned
#                 on the batch ID `batch_id` and the previously generated tokens `inputs_ids`. This argument is useful
#                 for constrained generation conditioned on the prefix, as described in [Autoregressive Entity
#                 Retrieval](https://arxiv.org/abs/2010.00904).
#             synced_gpus (`bool`, *optional*):
#                 Whether to continue running the while loop until max_length. Unless overridden this flag will be set to
#                 `True` under DeepSpeed ZeRO Stage 3 multiple GPUs environment to avoid hanging if one GPU finished
#                 generating before other GPUs. Otherwise it'll be set to `False`.
#             assistant_model (`PreTrainedModel`, *optional*):
#                 An assistant model that can be used to accelerate generation. The assistant model must have the exact
#                 same tokenizer. The acceleration is achieved when forecasting candidate tokens with the assistent model
#                 is much faster than running generation with the model you're calling generate from. As such, the
#                 assistant model should be much smaller.
#             streamer (`BaseStreamer`, *optional*):
#                 Streamer object that will be used to stream the generated sequences. Generated tokens are passed
#                 through `streamer.put(token_ids)` and the streamer is responsible for any further processing.
#             negative_prompt_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
#                 The negative prompt needed for some processors such as CFG. The batch size must match the input batch
#                 size. This is an experimental feature, subject to breaking API changes in future versions.
#             negative_prompt_attention_mask (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
#                 Attention_mask for `negative_prompt_ids`.
#             kwargs (`Dict[str, Any]`, *optional*):
#                 Ad hoc parametrization of `generate_config` and/or additional model-specific kwargs that will be
#                 forwarded to the `forward` function of the model. If the model is an encoder-decoder model, encoder
#                 specific kwargs should not be prefixed and decoder specific kwargs should be prefixed with *decoder_*.

#         Return:
#             [`~utils.ModelOutput`] or `torch.LongTensor`: A [`~utils.ModelOutput`] (if `return_dict_in_generate=True`
#             or when `config.return_dict_in_generate=True`) or a `torch.FloatTensor`.

#                 If the model is *not* an encoder-decoder model (`model.config.is_encoder_decoder=False`), the possible
#                 [`~utils.ModelOutput`] types are:

#                     - [`~generation.GenerateDecoderOnlyOutput`],
#                     - [`~generation.GenerateBeamDecoderOnlyOutput`]

#                 If the model is an encoder-decoder model (`model.config.is_encoder_decoder=True`), the possible
#                 [`~utils.ModelOutput`] types are:

#                     - [`~generation.GenerateEncoderDecoderOutput`],
#                     - [`~generation.GenerateBeamEncoderDecoderOutput`]
#         """
#         # print("This is from the generator made by Hangoo Kang")
#         # if synced_gpus is None:
#         #     if is_deepspeed_zero3_enabled() and dist.get_world_size() > 1:
#         #         synced_gpus = True
#         #     else:
#         #         synced_gpus = False

#         # 1. Handle `generation_config` and kwargs that might update it, and validate the `.generate()` call
#         self._validate_model_class()

#         # priority: `generation_config` argument > `model.generation_config` (the default generation config)
#         #___________________________________________________________________________________________
#         if generation_config is None:
#             # legacy: users may modify the model configuration to control generation. To trigger this legacy behavior,
#             # three conditions must be met
#             # 1) the generation config must have been created from the model config (`_from_model_config` field);
#             # 2) the generation config must have seen no modification since its creation (the hash is the same);
#             # 3) the user must have set generation parameters in the model config.
#             if (
#                 self.generation_config._from_model_config
#                 and self.generation_config._original_object_hash == hash(self.generation_config)
#                 and self.config._has_non_default_generation_parameters()
#             ):
#                 new_generation_config = GenerationConfig.from_model_config(self.config)
#                 if new_generation_config != self.generation_config:
#                     warnings.warn(
#                         "You have modified the pretrained model configuration to control generation. This is a"
#                         " deprecated strategy to control generation and will be removed soon, in a future version."
#                         " Please use and modify the model generation configuration (see"
#                         " https://huggingface.co/docs/transformers/generation_strategies#default-text-generation-configuration )"
#                     )
#                     self.generation_config = new_generation_config
#             generation_config = self.generation_config

# # ___________________________________________________________________________________________________

#         generation_config = copy.deepcopy(generation_config)
#         model_kwargs = generation_config.update(**kwargs)  # All unused kwargs must be model kwargs
#         generation_config.validate()
#         self._validate_model_kwargs(model_kwargs.copy())

#         # 2. Set generation parameters if not already defined
#         logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
#         stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()

#         if generation_config.pad_token_id is None and generation_config.eos_token_id is not None:
#             if model_kwargs.get("attention_mask", None) is None:
#                 logger.warning(
#                     "The attention mask and the pad token id were not set. As a consequence, you may observe "
#                     "unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results."
#                 )
#             eos_token_id = generation_config.eos_token_id
#             if isinstance(eos_token_id, list):
#                 eos_token_id = eos_token_id[0]
#             logger.warning(f"Setting `pad_token_id` to `eos_token_id`:{eos_token_id} for open-end generation.")
#             generation_config.pad_token_id = eos_token_id

#         # 3. Define model inputs
#         # inputs_tensor has to be defined
#         # model_input_name is defined if model-specific keyword input is passed
#         # otherwise model_input_name is None
#         # all model-specific keyword inputs are removed from `model_kwargs`
#         inputs_tensor, model_input_name, model_kwargs = self._prepare_model_inputs(
#             inputs, generation_config.bos_token_id, model_kwargs
#         )
#         batch_size = inputs_tensor.shape[0]

#         # 4. Define other model kwargs
#         model_kwargs["output_attentions"] = generation_config.output_attentions
#         model_kwargs["output_hidden_states"] = generation_config.output_hidden_states
#         # decoder-only models with inputs_embeds forwarding must use caching (otherwise we can't detect whether we are
#         # generating the first new token or not, and we only want to use the embeddings for the first new token)
#         if not self.config.is_encoder_decoder and model_input_name == "inputs_embeds":
#             model_kwargs["use_cache"] = True
#         else:
#             model_kwargs["use_cache"] = generation_config.use_cache

#         accepts_attention_mask = "attention_mask" in set(inspect.signature(self.forward).parameters.keys())
#         requires_attention_mask = "encoder_outputs" not in model_kwargs

#         if model_kwargs.get("attention_mask", None) is None and requires_attention_mask and accepts_attention_mask:
#             model_kwargs["attention_mask"] = self._prepare_attention_mask_for_generation(
#                 inputs_tensor, generation_config.pad_token_id, generation_config.eos_token_id
#             )

#         # decoder-only models should use left-padding for generation
#         if not self.config.is_encoder_decoder:
#             # If `input_ids` was given, check if the last id in any sequence is `pad_token_id`
#             # Note: If using, `inputs_embeds` this check does not work, because we want to be more hands-off.
#             if (
#                 generation_config.pad_token_id is not None
#                 and len(inputs_tensor.shape) == 2
#                 and torch.sum(inputs_tensor[:, -1] == generation_config.pad_token_id) > 0
#             ):
#                 logger.warning(
#                     "A decoder-only architecture is being used, but right-padding was detected! For correct "
#                     "generation results, please set `padding_side='left'` when initializing the tokenizer."
#                 )

#         if self.config.is_encoder_decoder and "encoder_outputs" not in model_kwargs:
#             # if model is encoder decoder encoder_outputs are created
#             # and added to `model_kwargs`
#             model_kwargs = self._prepare_encoder_decoder_kwargs_for_generation(
#                 inputs_tensor, model_kwargs, model_input_name
#             )

#         # 5. Prepare `input_ids` which will be used for auto-regressive generation
#         if self.config.is_encoder_decoder:
#             input_ids, model_kwargs = self._prepare_decoder_input_ids_for_generation(
#                 batch_size=batch_size,
#                 model_input_name=model_input_name,
#                 model_kwargs=model_kwargs,
#                 decoder_start_token_id=generation_config.decoder_start_token_id,
#                 bos_token_id=generation_config.bos_token_id,
#                 device=inputs_tensor.device,
#             )
#         else:
#             input_ids = inputs_tensor if model_input_name == "input_ids" else model_kwargs.pop("input_ids")

#         if streamer is not None:
#             streamer.put(input_ids.cpu())

#         # 6. Prepare `max_length` depending on other stopping criteria.
#         input_ids_length = input_ids.shape[-1]
#         has_default_max_length = kwargs.get("max_length") is None and generation_config.max_length is not None
#         if generation_config.max_new_tokens is not None:
#             if not has_default_max_length and generation_config.max_length is not None:
#                 logger.warning(
#                     f"Both `max_new_tokens` (={generation_config.max_new_tokens}) and `max_length`(="
#                     f"{generation_config.max_length}) seem to have been set. `max_new_tokens` will take precedence. "
#                     "Please refer to the documentation for more information. "
#                     "(https://huggingface.co/docs/transformers/main/en/main_classes/text_generation)"
#                 )
#             generation_config.max_length = generation_config.max_new_tokens + input_ids_length
#         self._validate_generated_length(generation_config, input_ids_length, has_default_max_length)

#         # 7. determine generation mode
#         generation_mode = self._get_generation_mode(generation_config, assistant_model)

#         if streamer is not None and (generation_config.num_beams > 1):
#             raise ValueError(
#                 "`streamer` cannot be used with beam search (yet!). Make sure that `num_beams` is set to 1."
#             )

#         if self.device.type != input_ids.device.type:
#             warnings.warn(
#                 "You are calling .generate() with the `input_ids` being on a device type different"
#                 f" than your model's device. `input_ids` is on {input_ids.device.type}, whereas the model"
#                 f" is on {self.device.type}. You may experience unexpected behaviors or slower generation."
#                 " Please make sure that you have put `input_ids` to the"
#                 f" correct device by calling for example input_ids = input_ids.to('{self.device.type}') before"
#                 " running `.generate()`.",
#                 UserWarning,
#             )

#         # 8. prepare distribution pre_processing samplers
#         prepared_logits_processor = self._get_logits_processor(
#             generation_config=generation_config,
#             input_ids_seq_length=input_ids_length,
#             encoder_input_ids=inputs_tensor,
#             prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
#             logits_processor=logits_processor,
#             model_kwargs=model_kwargs,
#             negative_prompt_ids=negative_prompt_ids,
#             negative_prompt_attention_mask=negative_prompt_attention_mask,
#         )

#         # 9. prepare stopping criteria
#         prepared_stopping_criteria = self._get_stopping_criteria(
#             generation_config=generation_config, stopping_criteria=stopping_criteria
#         )
#         # 10. go into different generation modes
#         if generation_mode == GenerationMode.ASSISTED_GENERATION:
#             if generation_config.num_return_sequences > 1:
#                 raise ValueError(
#                     "num_return_sequences has to be 1 when doing assisted generate, "
#                     f"but is {generation_config.num_return_sequences}."
#                 )
#             if batch_size > 1:
#                 raise ValueError("assisted generate is only supported for batch_size = 1")
#             if not model_kwargs["use_cache"]:
#                 raise ValueError("assisted generate requires `use_cache=True`")

#             # 11. Get the candidate generator, given the parameterization
#             candidate_generator = self._get_candidate_generator(
#                 generation_config=generation_config,
#                 input_ids=input_ids,
#                 inputs_tensor=inputs_tensor,
#                 assistant_model=assistant_model,
#                 logits_processor=logits_processor,
#                 model_kwargs=model_kwargs,
#             )

#             # 12. run assisted generate
#             return self.assisted_decoding(
#                 input_ids,
#                 candidate_generator=candidate_generator,
#                 do_sample=generation_config.do_sample,
#                 logits_processor=prepared_logits_processor,
#                 logits_warper=self._get_logits_warper(generation_config) if generation_config.do_sample else None,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 streamer=streamer,
#                 **model_kwargs,
#             )
#         if generation_mode == GenerationMode.GREEDY_SEARCH:
#             # 11. run greedy search
#             return self.greedy_search(
#                 input_ids,
#                 logits_processor=prepared_logits_processor,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 streamer=streamer,
#                 **model_kwargs,
#             )

#         elif generation_mode == GenerationMode.CONTRASTIVE_SEARCH:
#             if not model_kwargs["use_cache"]:
#                 raise ValueError("Contrastive search requires `use_cache=True`")

#             return self.contrastive_search(
#                 input_ids,
#                 top_k=generation_config.top_k,
#                 penalty_alpha=generation_config.penalty_alpha,
#                 logits_processor=prepared_logits_processor,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 streamer=streamer,
#                 sequential=generation_config.low_memory,
#                 **model_kwargs,
#             )

#         elif generation_mode == GenerationMode.SAMPLE:
#             # 11. prepare logits warper
#             logits_warper = self._get_logits_warper(generation_config)

#             # 12. expand input_ids with `num_return_sequences` additional sequences per batch
#             input_ids, model_kwargs = self._expand_inputs_for_generation(
#                 input_ids=input_ids,
#                 expand_size=generation_config.num_return_sequences,
#                 is_encoder_decoder=self.config.is_encoder_decoder,
#                 **model_kwargs,
#             )

#             # 13. run sample
#             return self.sample(
#                 input_ids,
#                 logits_processor=prepared_logits_processor,
#                 logits_warper=logits_warper,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 streamer=streamer,
#                 **model_kwargs,
#             )

#         elif generation_mode == GenerationMode.BEAM_SEARCH:
#             # 11. prepare beam search scorer
#             beam_scorer = BeamSearchScorer(
#                 batch_size=batch_size,
#                 num_beams=generation_config.num_beams,
#                 device=inputs_tensor.device,
#                 length_penalty=generation_config.length_penalty,
#                 do_early_stopping=generation_config.early_stopping,
#                 num_beam_hyps_to_keep=generation_config.num_return_sequences,
#                 max_length=generation_config.max_length,
#             )
#             # 12. interleave input_ids with `num_beams` additional sequences per batch
#             input_ids, model_kwargs = self._expand_inputs_for_generation(
#                 input_ids=input_ids,
#                 expand_size=generation_config.num_beams,
#                 is_encoder_decoder=self.config.is_encoder_decoder,
#                 **model_kwargs,
#             )
#             # 13. run beam search
#             return self.beam_search(
#                 input_ids,
#                 beam_scorer,
#                 logits_processor=prepared_logits_processor,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 **model_kwargs,
#             )

#         elif generation_mode == GenerationMode.BEAM_SAMPLE:
#             # 11. prepare logits warper
#             logits_warper = self._get_logits_warper(generation_config)

#             # 12. prepare beam search scorer
#             beam_scorer = BeamSearchScorer(
#                 batch_size=batch_size,
#                 num_beams=generation_config.num_beams,
#                 device=inputs_tensor.device,
#                 length_penalty=generation_config.length_penalty,
#                 do_early_stopping=generation_config.early_stopping,
#                 num_beam_hyps_to_keep=generation_config.num_return_sequences,
#                 max_length=generation_config.max_length,
#             )

#             # 13. interleave input_ids with `num_beams` additional sequences per batch
#             input_ids, model_kwargs = self._expand_inputs_for_generation(
#                 input_ids=input_ids,
#                 expand_size=generation_config.num_beams,
#                 is_encoder_decoder=self.config.is_encoder_decoder,
#                 **model_kwargs,
#             )

#             # 14. run beam sample
#             return self.beam_sample(
#                 input_ids,
#                 beam_scorer,
#                 logits_processor=prepared_logits_processor,
#                 logits_warper=logits_warper,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 **model_kwargs,
#             )

#         elif generation_mode == GenerationMode.GROUP_BEAM_SEARCH:
#             # 11. prepare beam search scorer
#             beam_scorer = BeamSearchScorer(
#                 batch_size=batch_size,
#                 num_beams=generation_config.num_beams,
#                 device=inputs_tensor.device,
#                 length_penalty=generation_config.length_penalty,
#                 do_early_stopping=generation_config.early_stopping,
#                 num_beam_hyps_to_keep=generation_config.num_return_sequences,
#                 num_beam_groups=generation_config.num_beam_groups,
#                 max_length=generation_config.max_length,
#             )
#             # 12. interleave input_ids with `num_beams` additional sequences per batch
#             input_ids, model_kwargs = self._expand_inputs_for_generation(
#                 input_ids=input_ids,
#                 expand_size=generation_config.num_beams,
#                 is_encoder_decoder=self.config.is_encoder_decoder,
#                 **model_kwargs,
#             )
#             # 13. run beam search
#             return self.group_beam_search(
#                 input_ids,
#                 beam_scorer,
#                 logits_processor=prepared_logits_processor,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 **model_kwargs,
#             )

#         elif generation_mode == GenerationMode.CONSTRAINED_BEAM_SEARCH:
#             final_constraints = []
#             if generation_config.constraints is not None:
#                 final_constraints = generation_config.constraints

#             if generation_config.force_words_ids is not None:

#                 def typeerror():
#                     raise ValueError(
#                         "`force_words_ids` has to either be a `List[List[List[int]]]` or `List[List[int]]` "
#                         f"of positive integers, but is {generation_config.force_words_ids}."
#                     )

#                 if (
#                     not isinstance(generation_config.force_words_ids, list)
#                     or len(generation_config.force_words_ids) == 0
#                 ):
#                     typeerror()

#                 for word_ids in generation_config.force_words_ids:
#                     if isinstance(word_ids[0], list):
#                         if not isinstance(word_ids, list) or len(word_ids) == 0:
#                             typeerror()
#                         if any(not isinstance(token_ids, list) for token_ids in word_ids):
#                             typeerror()
#                         if any(
#                             any((not isinstance(token_id, int) or token_id < 0) for token_id in token_ids)
#                             for token_ids in word_ids
#                         ):
#                             typeerror()

#                         constraint = DisjunctiveConstraint(word_ids)
#                     else:
#                         if not isinstance(word_ids, list) or len(word_ids) == 0:
#                             typeerror()
#                         if any((not isinstance(token_id, int) or token_id < 0) for token_id in word_ids):
#                             typeerror()

#                         constraint = PhrasalConstraint(word_ids)
#                     final_constraints.append(constraint)

#             # 11. prepare beam search scorer
#             constrained_beam_scorer = ConstrainedBeamSearchScorer(
#                 constraints=final_constraints,
#                 batch_size=batch_size,
#                 num_beams=generation_config.num_beams,
#                 device=inputs_tensor.device,
#                 length_penalty=generation_config.length_penalty,
#                 do_early_stopping=generation_config.early_stopping,
#                 num_beam_hyps_to_keep=generation_config.num_return_sequences,
#                 max_length=generation_config.max_length,
#             )
#             # 12. interleave input_ids with `num_beams` additional sequences per batch
#             input_ids, model_kwargs = self._expand_inputs_for_generation(
#                 input_ids=input_ids,
#                 expand_size=generation_config.num_beams,
#                 is_encoder_decoder=self.config.is_encoder_decoder,
#                 **model_kwargs,
#             )
#             # 13. run beam search
#             return self.constrained_beam_search(
#                 input_ids,
#                 constrained_beam_scorer=constrained_beam_scorer,
#                 logits_processor=prepared_logits_processor,
#                 stopping_criteria=prepared_stopping_criteria,
#                 pad_token_id=generation_config.pad_token_id,
#                 eos_token_id=generation_config.eos_token_id,
#                 output_scores=generation_config.output_scores,
#                 return_dict_in_generate=generation_config.return_dict_in_generate,
#                 synced_gpus=synced_gpus,
#                 **model_kwargs,
#             )



#     # def generate(self, *args, **kwargs):
#     #     print("Calling custom generate method...")
#     #     return self.model.generate(*args, **kwargs)






# # #______________________________________________________________________________________________________________________________
