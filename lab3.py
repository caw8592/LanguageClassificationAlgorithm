import math
import sys
import pickle

MAX_TREE_DEPTH = 4
NUM_STUMPS = 10


class Data:
    def __init__(self, answer, words):
        self.answer = answer
        self.string = words


class Tree:
    def __init__(self, data, choice):
        self.data = data
        self.choice = choice
        self.left_child = None
        self.right_child = None


def print_tree(tree) -> str:
    if tree.left_child == None:
        return ""
    return f"{tree.data} [{print_tree(tree.left_child)}] [{print_tree(tree.right_child)}]"

def find_entropy(examples):
    if(len(examples) == 1 or len(examples) == 0) :
        return 0

    num_en = 0
    num_nl = 0
    for example in examples:
        if example.answer == "en":
            num_en += 1
        else:
            num_nl += 1

    probability_en = num_en/len(examples)
    probability_nl = num_nl/len(examples)

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


# return type to be decided
def ada_boost(examples, features):
    return
        

def train(examples_file, features_file, hypothesis_out_file, learning_type):
    
    examples = []
    for line in open(examples_file, 'r', encoding="utf8"):
        data_list = line.split("|")
        examples.append(Data(data_list[0], data_list[1].split(" ")))
    
    features = []
    for line in open(features_file, 'r', encoding="utf8"):
        features.append(line.strip())

    match learning_type:
        case "dt":
            hypothesis = decision_tree(examples, features)
        case "ada":
            hypothesis = ada_boost(examples, features)
        case _:
            print("Unknown Learning Type")

    pickle.dump(hypothesis, open(hypothesis_out_file, 'wb'))


def solve(example, dt, features) -> str:
    if dt.left_child == None and dt.right_child == None:
        return dt.choice
    if(features[dt.data] in example):
        return solve(example, dt.left_child, features)
    return solve(example, dt.right_child, features)


def predict(examples_file, features_file, hypothesis_file):

    examples = []
    for line in open(examples_file, 'r', encoding="utf8"):
        examples.append(line)

    features = []
    for line in open(features_file, 'r', encoding="utf8"):
        features.append(line.strip())

    trained_dt = pickle.load(open(hypothesis_file, 'rb'))

    file = open("predict.out", 'w')
    for example in examples:
        solved = solve(example, trained_dt, features)
        file.write(solved+"\n")
        #print(solved)


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