import sys
import os
import argparse

from mxeval.data import get_metadata
from mxeval.evaluation import evaluate_functional_correctness


def get_datafile(dataset="mbxp", language="python"):
  metadata, datadir = get_metadata(dataset, metadata_type="problem")
  if language.lower() not in metadata:
    raise ValueError(f"Language {language} not found in metadata file")
  datafile = metadata[language.lower()]
  return os.path.join(datadir, datafile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="Enter the filename")
    parser.add_argument("--language", choices = ["python", "go"], default = "python", help = "language")
    parser.add_argument("--dataset", choices = ["mbxp", "humaneval", "mathqa"], default = "humaneval", help = "language")
    parser.add_argument("--k", default = "1,", help = "k param for pass@k")
    parser.add_argument("--timeout", default= 15.0, type = float, help = "timeout")
    args = parser.parse_args()
    
    n_workers = os.cpu_count() - 1
    results = evaluate_functional_correctness(args.filename, eval(args.k), n_workers, args.timeout, get_datafile(args.dataset, args.language))

    with open(args.filename + "_passatk.json", "w") as f:
        f.write(str(results))
 
    print(results)

if __name__ == "__main__":
    main()