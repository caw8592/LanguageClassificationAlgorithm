import math

class data:
    def __init__(self, attributes, answer):
        self.attributes = attributes
        self.answer = answer


def findEnt(list):
    if(len(list) == 1 or len(list) == 0) :
        return 0

    numA = 0
    numB = 0
    for i in list:
        if i.answer == "A":
            numA += 1
        else:
            numB += 1

    pA = numA/len(list)
    pB = numB/len(list)

    return -(pB*math.log(pB, 2) + pA*math.log(pA, 2))

def bestChoice(datalist):
    bestEnt = 0
    bestyes = []
    bestno = []
    bestidx = 0
    for i in range(7):
        yes = []
        no = []
        for j in datalist:
            if(j.attributes[i] == "True"):
                yes.append(j)
            else:
                no.append(j)

        entyes = (len(yes)/len(datalist)) * findEnt(yes)
        entno = (len(no)/len(datalist)) * findEnt(no)
        ent = findEnt(datalist) - (entyes + entno)

        if ent > bestEnt:
            bestEnt = ent
            bestyes = yes
            bestno = no
            bestidx = i

    return bestyes, bestno, bestidx, bestEnt


def countTF(list):
    numA = 0
    numB = 0
    for i in list:
        if i.answer == "A":
            numA += 1
        else:
            numB += 1
    return numA, numB

def removeQuestion(list, idx):
    for i in list:
        i.attributes.pop(idx)


def main():

    f = open("data.txt", "r")
    
    datalist = []
    for i in f:
        attributes = i.split(' ')
        answer = attributes[8].removesuffix('\n')
        attributes.pop(8)
        
        datalist.append(data(attributes, answer))

    # lst1 = choice true | lst2 = choose false
    lst1, lst2, idx, ent = bestChoice(datalist)

    print("Best True:", countTF(lst1))
    print("Best False:", countTF(lst2))
    print("Best Idx:", idx)
    print("ent:", ent)

    print("==============")

    lst11, lst12, idx1, ent1 = bestChoice(lst1)
    lst21, lst22, idx2, ent2 = bestChoice(lst2)

    print("Best True 1:", countTF(lst11))
    print("Best False 1:", countTF(lst12))
    print("Best Idx 1:", idx1)
    print("ent 1:",ent1)

    print("==============")

    print("Best True 2:", countTF(lst21))
    print("Best False 2:", countTF(lst22))
    print("Best Idx 2:", idx2)
    print("ent 2:", ent2)

    f.close

if __name__ == "__main__":
    main()