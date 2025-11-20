import copy 
import random

def generateAttackSequence(attackList):
    attacks = copy.copy(attackList) * 3
    attacks = shuffle(attacks)
    return solve(attacks, [])

def solve(attacks, result):
    if attacks == []:
        return result
    else:
        for i in range(len(attacks)):
            if isLegal(result, attacks[i]):
                result.append(attacks.pop(i))
                solution = solve(attacks, result)
                if solution != None:
                    return solution
                attacks.insert(i, result.pop())
        return None
    
def isLegal(result, attack):
    if result == []:
        return True
    else:
        if attack == 'lightning' and result[-1] == 'lightning':
            return False
        elif attack == 'charge':
            if len(result) == 1:
                return True
            else:
                if result[-1] == 'charge' and result[-2] == 'charge':
                    return False
        return True

def shuffle(attacks):
    attacks = copy.copy(attacks)
    return solveShuffle(attacks, [])

def solveShuffle(attacks, result):
    if attacks == []:
        return result
    else:
        firstIdx = random.randint(0, len(attacks)-1)
        first = attacks.pop(firstIdx)
        result.append(first)
        return solveShuffle(attacks, result)
