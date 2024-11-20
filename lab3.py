import math
import sys
import pickle

MAX_TREE_DEPTH = 2
NUM_STUMPS = 10


class Data:
    def __init__(self, answer, string, weight):
        self.answer = answer
        self.string = string
        self.weight = weight


class Tree:
    def __init__(self, data, choice):
        self.data = data
        self.choice = choice
        self.left_child = None
        self.right_child = None


class WeightedHypothesis:
    def __init__(self, dt, weight):
        self.dt = dt
        self.weight = weight
    

class Hypothesis:
    def __init__(self, type, hypothesis):
        self.type = type
        self.hypothesis = hypothesis

def print_tree(tree) -> str:
    if tree.left_child == None:
        return ""
    return f"{tree.data} [{print_tree(tree.left_child)}] [{print_tree(tree.right_child)}]"


def find_entropy(examples):
    if(len(examples) == 1 or len(examples) == 0) :
        return 0

    weight_en = 0
    weight_nl = 0
    weight_total = 0
    for example in examples:
        if example.answer == "en":
            weight_en += example.weight
        else:
            weight_nl += example.weight
        weight_total += example.weight

    probability_en = weight_en/weight_total
    probability_nl = weight_nl/weight_total

    if probability_en == 0 or probability_nl == 0:
        return 0

    return -(probability_nl*math.log(probability_nl, 2) + probability_en*math.log(probability_en, 2))


# returns the root of a tree
def decision_tree(examples, features, curr_depth = 0):
    if curr_depth > MAX_TREE_DEPTH:
        return None
    if curr_depth == len(features):
        return None
    if len(examples) == 0:
        return None
    
    # figure out if all options are the same
    answer = examples[0].answer
    all_same = True
    for ex in examples:
        if ex.answer != answer:
            all_same = False
            break
    if(all_same):
        return Tree(-1, answer)
    
    best_entropy = 0
    best_idx = 0
    best_has = []
    best_hasnt = []
    for i in range(len(features)):
        has = []
        hasnt = []
        for example in examples:
            if features[i] in example.string:
                has.append(example)
            else:
                hasnt.append(example)

        has_entropy = (len(has)/len(examples)) * find_entropy(has)
        hasnt_entropy = (len(hasnt)/len(examples)) * find_entropy(hasnt)
        entropy = find_entropy(examples) - (has_entropy + hasnt_entropy)

        if entropy > best_entropy:
            best_entropy = entropy
            best_idx = i
            best_has = has
            best_hasnt = hasnt

    is_en = 0
    is_nl = 0
    for example in examples:
        if example.answer == "en":
            is_en += 1
        else:
            is_nl += 1

    this_node = Tree(best_idx, "en" if is_en >= is_nl else "nl")
    this_node.left_child = decision_tree(best_has, features, curr_depth+1)
    this_node.right_child = decision_tree(best_hasnt, features, curr_depth+1)
    
    
    return this_node


def normalize_weights(examples: list[Data]) -> list[Data]:
    total_weights = 0
    for example in examples:
        total_weights += example.weight
    for example in examples:
        example.weight = example.weight/total_weights
    return examples


def ada_solve(example, dt, features) -> str:
    if dt.left_child == None and dt.right_child == None:
        return dt.choice
    if(features[dt.data] in example.string):
        return ada_solve(example, dt.left_child, features)
    return ada_solve(example, dt.right_child, features)


# return type to be decided
def ada_boost(examples: list[Data], features: list[str]):
    H: list[Data] = []
    for i in range(NUM_STUMPS):
        h = decision_tree(examples, features)
        err = 0
        for example in examples:
            if ada_solve(example, h, features) != example.answer:
                err += example.weight
        DW = err/(1-err)
        for example in examples:
            if ada_solve(example, h, features) == example.answer:
                example.weight = example.weight*DW
        examples = normalize_weights(examples)
        H.append(WeightedHypothesis(h, (.5*math.log((1-err)/err))))
    return H
     

def train(examples_file, features_file, hypothesis_out_file, learning_type):
    examples = []
    file = open(examples_file, 'r', encoding="utf8")
    lines = file.readlines()
    for line in lines:
        data_list = line.split("|")
        if learning_type == 'ada':
            examples.append(Data(data_list[0], data_list[1].split(" "), 1/len(lines)))
        else:
            examples.append(Data(data_list[0], data_list[1].split(" "), 1))
    
    
    features = []
    for line in open(features_file, 'r', encoding="utf8"):
        features.append(line.strip())

    match learning_type:
        case "dt":
            hypothesis = Hypothesis("dt", decision_tree(examples, features))
        case "ada":
            hypothesis = Hypothesis("ada", ada_boost(examples, features))
        case _:
            print("Unknown Learning Type")

    pickle.dump(hypothesis, open(hypothesis_out_file, 'wb'))


def solve(example, dt, features) -> str:
    if dt.left_child == None and dt.right_child == None:
        return dt.choice
    if(features[dt.data] in example):
        return solve(example, dt.left_child, features)
    return solve(example, dt.right_child, features)


def calc_right():
    test = []
    for line in open("test.txt", 'r', encoding="utf8"):
        test.append(line.split("|")[0])
    
    out = []
    for line in open("predict.out", 'r',  encoding="utf8"):
        out.append(line.strip())

    right = 0
    for i in range(len(test)):
        if test[i] == out[i]:
            right += 1

    print(right/len(test))


def predict(examples_file, features_file, hypothesis_file):

    examples = []
    for line in open(examples_file, 'r', encoding="utf8"):
        examples.append(line)

    features = []
    for line in open(features_file, 'r', encoding="utf8"):
        features.append(line.strip())

    hypothesis = pickle.load(open(hypothesis_file, 'rb'))

    #file = open("predict.out", 'w')
    match hypothesis.type:
        case "dt":
            for example in examples:
                solved = solve(example, hypothesis.hypothesis, features)
                #file.write(solved+"\n")
                print(solved)
        case "ada":
            for example in examples:
                weight_en = 0
                weight_nl = 0
                for hyp in hypothesis.hypothesis:
                    if(solve(example, hyp.dt, features) == "en"):
                        weight_en += hyp.weight
                    else:
                        weight_nl += hyp.weight
                #file.write("en\n" if weight_en >= weight_nl else "nl\n")
                print("en" if weight_en >= weight_nl else "nl")
    #file.close()
    #calc_right()


if __name__ == "__main__":
    if len(sys.argv) == 0:
        print("Command Unknown, please try again")
    match sys.argv[1]:
        case "train":
            train(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        case "predict":
            predict(sys.argv[2], sys.argv[3], sys.argv[4])
        case _:
            print("Command Unknown, please try again")