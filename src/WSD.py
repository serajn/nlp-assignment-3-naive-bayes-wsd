import re
import sys
import math
from collections import Counter, defaultdict

def load_dataset(filename):
    instances = []

    with open(filename, 'r') as file:
        context = []
        collecting_context = False
        instance_id = None
        sense_id = None

        for line in file:
            line = line.strip()

            if line.startswith("<answer"):
                instance_id = line.split('instance="')[1].split('"')[0]
                sense_id = line.split('senseid="')[1].split('"')[0]

            elif line.startswith("<context>"):
                collecting_context = True

            elif line == "</context>":
                collecting_context = False

                instances.append({
                    "id": instance_id,
                    "sense": sense_id,
                    "context": " ".join(context)
                })

                context = []

            elif collecting_context:
                context.append(line)

    return instances

def tokenize_context(context):
    return re.findall(r"\b\w+\b", context.lower())

def create_folds(instances):
    n = len(instances)
    fold_size = math.ceil(n / 5)

    folds = []

    for i in range(4):
        start = i * fold_size
        end = start + fold_size
        folds.append(instances[start:end])

    folds.append(instances[4 * fold_size:])

    return folds

def collect_counts(train_data):
    sense_counts = Counter()
    word_counts = defaultdict(Counter)
    total_words_per_sense = Counter()

    for instance in train_data:
        sense = instance["sense"]
        context = instance["context"]

        sense_counts[sense] += 1

        words = tokenize_context(context)

        for word in words:
            word_counts[sense][word] += 1
            total_words_per_sense[sense] += 1
    return sense_counts, word_counts, total_words_per_sense


def run_cross_validation(instances):
    folds = create_folds(instances)
    all_predictions = []
    all_gold_labels = []

    for i in range(5):
        test_data = folds[i]

        train_data = []
        for j in range(5):
            if j != i:
                train_data.extend(folds[j])

        # Learn statistics from the training fold
        # Predict the sense of each test instance
        # Save predictions and gold labels
    return None

def main():
    filename = sys.argv[1]

    dataset = load_dataset(filename)

    with open("../debug/instances.txt", 'w') as output_file:
        for instance in dataset:
            output_file.write(f"Instance ID: {instance['id']}\n")
            output_file.write(f"Sense ID: {instance['sense']}\n")
            output_file.write(f"Context: {instance['context']}\n")
            output_file.write("\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
           


