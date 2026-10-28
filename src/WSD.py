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
    # Find the word or phrase within the <head> tags
    head_match = re.search(
        r"<head>(.*?)</head>",
        context,
        flags=re.IGNORECASE | re.DOTALL
    )

    target = head_match.group(1).strip().lower() if head_match else None

    # Remove the tags and preserve the surrounding text
    clean_context = re.sub(
        r"</?head>",
        "",
        context,
        flags=re.IGNORECASE
    )

    # Tokenize the context
    words = re.findall(r"\b\w+\b", clean_context.lower())

    # Exclude the target word from the feature list
    if target:
        target_tokens = re.findall(r"\b\w+\b", target)
        words = words.copy()

        start = len(re.findall(
            r"\b\w+\b",
            clean_context[:head_match.start()].lower()
        ))
        words[start:start + len(target_tokens)] = []

    return words

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
    total_instances = 0

    for instance in train_data:
        sense = instance["sense"]
        context = instance["context"]

        sense_counts[sense] += 1

        words = tokenize_context(context)

        for word in set(words):
            word_counts[sense][word] += 1

        total_instances += 1

    return sense_counts, word_counts, total_instances

def predict_sense(test_data, sense_counts, word_counts, total_instances):
    predictions = []

    for instance in test_data:
        words = tokenize_context(instance["context"])
        words = set(words)

        best_sense = None
        best_score = -float('inf')

        for sense, sense_count in sense_counts.items():
            # Log prior probability
            score = math.log(sense_count / total_instances)

            vocabulary_size = len(word_counts[sense])

            # Score each observed word using Laplace smoothing
            for word in words:
                word_count = word_counts[sense][word]

                probability = (
                    (word_count + 1) / 
                    (sense_count + vocabulary_size)
                )

                score += math.log(probability)

            if score > best_score:
                best_score = score
                best_sense = sense

        predictions.append(best_sense)

    return predictions


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
        sense_counts, word_counts, total_instances = collect_counts(train_data)

        # Predict the sense of each test instance
        predictions = predict_sense(test_data, sense_counts, word_counts, total_instances)

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
           


