import math
import sys
import pickle

MAX_TREE_DEPTH = 19
NUM_STUMPS = 10
STUMP_DEPTH = 1


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


def find_B(examples):
    if(len(examples) == 1 or len(examples) == 0) :
        return 0

    weight_en = 0
    weight_total = 0
    for example in examples:
        if example.answer == "en":
            weight_en += example.weight
        weight_total += example.weight

    probability_en = weight_en/weight_total

    if probability_en == 0 or probability_en == 1:
        return 0
    
    return probability_en*math.log((1/probability_en),2) + (1-probability_en)*math.log(1/(1-probability_en), 2)


def get_lst_weight(examples):
    total = 0
    for example in examples:
        total += example.weight
    return total


def find_remainder(examples, has, hasnt):
    examples_weight = get_lst_weight(examples)
    rem_has = (get_lst_weight(has)/examples_weight)*find_B(has)
    rem_hasnt = (get_lst_weight(hasnt)/examples_weight)*find_B(hasnt)

    return rem_has + rem_hasnt


def argemax(examples, features):
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
        
        entropy = find_B(examples) - find_remainder(examples, has, hasnt)

        if entropy > best_entropy:
            best_entropy = entropy
            best_idx = i
            best_has = has
            best_hasnt = hasnt
        if best_entropy == 0:
            best_idx = i
            best_has = has
            best_hasnt = hasnt

    return best_idx, best_has, best_hasnt


def Majority_Answer(examples):
    num_en = 0
    num_nl = 0
    for example in examples:
        if example.answer == "en":
            num_en += 1
        else:
            num_nl += 1
    return "en" if num_en > num_nl else "nl"


def is_Same_Classification(examples):
    classification = examples[0].answer
    for example in examples:
        if example.answer != classification:
            return False
    return True


# returns the root of a tree
def decision_tree(examples, features, curr_depth = 0, max_depth = MAX_TREE_DEPTH):
    if len(examples) == 0:
        return 1
    majority_answer = Majority_Answer(examples)
    if is_Same_Classification(examples):
        return Tree(-1, majority_answer)
    if len(features) == curr_depth:
        return Tree(-1, majority_answer)
    if curr_depth == max_depth:
        return Tree(-1, majority_answer)
    
    A, has, hasnt = argemax(examples, features)
    
    node = Tree(A, majority_answer)
    dt_left_child = decision_tree(has, features, curr_depth+1, max_depth)
    if dt_left_child == 1:
        dt_left_child = Tree(-1, majority_answer)
    node.left_child = dt_left_child

    dt_right_child = decision_tree(hasnt, features, curr_depth+1, max_depth)
    if dt_right_child == 1:
        dt_right_child = Tree(-1, majority_answer)
    node.right_child = dt_right_child

    return node


def normalize_weights(examples: list[Data]) -> list[Data]:
    total_weights = 0
    for example in examples:
        total_weights += example.weight
    for example in examples:
        example.weight = example.weight/total_weights
    return examples


def ada_solve(example, dt, features) -> str:
    if dt.data == -1:
        return dt.choice
    if(features[dt.data] in example.string):
        return ada_solve(example, dt.left_child, features)
    return ada_solve(example, dt.right_child, features)


# return type to be decided
def ada_boost(examples: list[Data], features: list[str]):
    H: list[Data] = []
    for i in range(NUM_STUMPS):
        h = decision_tree(examples, features, 0,  STUMP_DEPTH)
        err = 0
        for example in examples:
            if ada_solve(example, h, features) != example.answer:
                err += example.weight
        DW = err/(1-err)
        if DW == 0:
            DW = 1
        for example in examples:
            if ada_solve(example, h, features) == example.answer:
                example.weight = example.weight*DW
        examples = normalize_weights(examples)
        if err == 0:
            H.append(WeightedHypothesis(h, 1))
        else:
            H.append(WeightedHypothesis(h, (.5*math.log((1-err)/err))))
    return H
     

def train(examples_file, features_file, hypothesis_out_file, learning_type):
    examples = []
    file = open(examples_file, 'r', encoding="utf8")
    lines = file.readlines()
    for line in lines:
        data_list = line.split("|")
        if learning_type == 'ada':
            examples.append(Data(data_list[0], data_list[1].strip(), 1/len(lines)))
        else:
            examples.append(Data(data_list[0], data_list[1].strip(), 1))
    
    
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
    if dt.data == -1:
        return dt.choice
    if features[dt.data] in example:
        return solve(example, dt.left_child, features)
    return solve(example, dt.right_child, features)


def predict(examples_file, features_file, hypothesis_file):

    examples = []
    for line in open(examples_file, 'r', encoding="utf8"):
        examples.append(line)

    features = []
    for line in open(features_file, 'r', encoding="utf8"):
        features.append(line.strip())

    hypothesis = pickle.load(open(hypothesis_file, 'rb'))

    match hypothesis.type:
        case "dt":
            for example in examples:
                solved = solve(example, hypothesis.hypothesis, features)
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
                print("en" if weight_en >= weight_nl else "nl")


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