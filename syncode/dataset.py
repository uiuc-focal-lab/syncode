from datasets import load_dataset
from mxeval.data import write_jsonl, get_data, get_examples

class Dataset:
    """
    Class to handle dataset loading and processing
    Args:
    - dataset_name: str, name of the dataset
    - type: code, math, input or other
    - problems: list of dicts, each dict contains the problem and its metadata
    """
    def __init__(self, dataset, language=None, num_few_shot=0):
        dataset_dirmap = {"mbxp": "mbxp", "humaneval": "multi-humaneval", "mathqa-x": "mathqa-x"}
        if dataset in dataset_dirmap:
            self.dataset_name = dataset_dirmap[dataset]
            self.type = "code"
            if num_few_shot > 0:
                self.problems = {problem['task_id'] : problem for problem in get_examples(self.dataset_name, language, num_few_shot)}
            else:
                self.problems = get_data(self.dataset_name, language)
        elif dataset == "input":
            self.dataset_name = "input"
            self.type = "input"
        elif dataset == "gsm8k":
            self.dataset_name = "gsm8k"
            self.type = "math"
            problems = load_dataset(dataset, name="main", split="test")
            if num_few_shot > 0:
                examples = ""
                for problem in list(problems)[:num_few_shot]:
                    examples += 'Question:' + problem['question'] + "\n" + 'Answer:' + problem['answer'] + "\n\n"
                self.problems = []
                for problem in problems: # Add examples to each prompt
                    self.problems.append({**problem, 'question': examples + problem['question']})
            else:
                self.problems = problems
        else:
            # Use for other HF datasets
            self.type = "other"
            self.dataset_name = dataset
            self.problems = load_dataset(dataset, split="test")
    
    def __repr__(self) -> str:
        return self.dataset_name
    
    def post_process_answer(self, answer: str) -> str:
        if self.type == "math":
            answer = answer.lstrip("\n")
            answer = answer.split("\n\n")[0]
            return answer
        return answer
