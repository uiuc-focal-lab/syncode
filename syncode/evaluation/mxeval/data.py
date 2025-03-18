from typing import Iterable, Dict
import gzip
import json
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
MULTILINGUAL_HUMANEVAL_METADATA = os.path.join(ROOT, "data", "multilingual_humaneval", "metadata.json")
with open(MULTILINGUAL_HUMANEVAL_METADATA, "r", encoding="utf-8") as fr:
   MULTILINGUAL_HUMANEVAL_METADATA = json.load(fr)
HUMAN_EVAL_PYTHON = os.path.join(ROOT, "data", "multilingual_humaneval", MULTILINGUAL_HUMANEVAL_METADATA["python"])
HUMAN_EVAL = HUMAN_EVAL_PYTHON


def read_problems(evalset_file: str = HUMAN_EVAL_PYTHON) -> Dict[str, Dict]:
    return {task["task_id"]: task for task in stream_jsonl(evalset_file)}


def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    if filename.endswith(".gz"):
        with open(filename, "rb") as gzfp:
            with gzip.open(gzfp, 'rt') as fp:
                for line in fp:
                    if any(not x.isspace() for x in line):
                        yield json.loads(line)
    else:
        with open(filename, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)


def write_jsonl(filename: str, data: Iterable[Dict], append: bool = False):
    """
    Writes an iterable of dictionaries to jsonl
    """
    if append:
        mode = 'ab'
    else:
        mode = 'wb'
    filename = os.path.expanduser(filename)
    if filename.endswith(".gz"):
        with open(filename, mode) as fp:
            with gzip.GzipFile(fileobj=fp, mode='wb') as gzfp:
                for x in data:
                    gzfp.write((json.dumps(x) + "\n").encode('utf-8'))
    else:
        with open(filename, mode) as fp:
            for x in data:
                fp.write((json.dumps(x) + "\n").encode('utf-8'))


def get_metadata(dataset, metadata_type="problem"):
  assert metadata_type in ["problem", "example"]
  assert dataset in ["mbxp", "multi-humaneval", "mathqa-x"], f"Unsupported dataset {dataset}"
  dataset_dirmap = {"mbxp": "mbxp",
                    "multi-humaneval": "multilingual_humaneval",
                    "mathqa-x": "multilingual_mathqa"}
  typemap = {"problem": "metadata.json",
             "example": "metadata_examples.json"}
  datadir = os.path.join(ROOT, "data", dataset_dirmap[dataset])
  path =  os.path.join(datadir, typemap[metadata_type])
  with open(path, "r") as f:
    metadata = json.load(f)
    return metadata, datadir


def get_supported_langs(dataset):
  metadata, _ = get_metadata(dataset, metadata_type="problem")
  return list(metadata.keys())


def get_data(dataset="mbxp", language="python"):
  metadata, datadir = get_metadata(dataset, metadata_type="problem")
  if language.lower() not in metadata:
    raise ValueError(f"Language {language} not found in metadata file")
  datafile = metadata[language.lower()]
  print(f"Loading {dataset} | language = {language}")
  return read_problems(os.path.join(datadir, datafile))


# due to similar format, examples from mbxp are sufficient to be used
# for few-shot prompting in multi-humaneval
def get_examples(dataset="mbxp", language="python", num_examples=None):
  assert dataset in ["mbxp"], f"No fewshot examples in dataset {dataset}"
  metadata, datadir = get_metadata(dataset=dataset, metadata_type="example")
  if language.lower() not in metadata:
    raise ValueError(f"Language {language} not found in metadata file")
  datafile = metadata[language.lower()]
  print(f"Loading examples from {dataset} | language = {language}")
  # use streams
  if num_examples is None:
    # return the entire stream
    return stream_jsonl(os.path.join(datadir, datafile))
  else:
    problems = get_data(dataset=dataset, language=language)
    stream = get_examples(dataset=dataset, language=language)
    examples = []
    for idx, example in enumerate(stream):
      if idx == num_examples:
        break
      task_id = example["task_id"]
      prompt = problems[task_id]["prompt"]
      example["prompt"] = prompt
      examples.append(example)
    return examples
