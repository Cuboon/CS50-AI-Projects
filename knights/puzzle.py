from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# common knowledge
# A,B, and C are either knights or knaves and not both
common_knowledge = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave))
)

# Puzzle 0
# a says he's both knight and knave
# the statement is impossible:
# a knight can't also be a knave, and a knave always lies
# the claim is false. therefore, A is a knave
knowledge0 = And(

    common_knowledge,
    # if A is a knight, the claim is true
    Implication(AKnight, And(AKnight, AKnave)),
    # if A is a knave, the claim is false
    Implication(AKnave, Not(And(AKnight, AKnave)))
)

# Puzzle 1
# A says A and B are knaves
# but if A is a knight, the claim is true, and it implies A is a knave
# A is a knave, and B is a knight
knowledge1 = And(
    common_knowledge,
    # neither A or B can be both knights and knaves
    Implication(AKnight, And(AKnave, BKnave)),
    # A states that A and B are knaves
    Implication(AKnave, Not(And(AKnave, BKnave)))
)


# Puzzle 2
# A says A and B are both knights and knaves
# B says A and B are different kinds
# claimes must be measured together for consistency
knowledge2 = And(
    common_knowledge,
    # entity A
    Implication(AKnight, Or(And(AKnight, BKnight),
                            And(AKnave, BKnave))),

    Implication(AKnight, Not(Or(And(AKnight, BKnight),
                                And(AKnave, BKnave)))),

    # for  the entity B
    Implication(BKnight, Or(And(AKnave, BKnight),
                            And(AKnave, BKnave))),

    Implication(BKnave, Not(Or(And(AKnave, BKnight),
                            And(AKnave, BKnave)))),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but neither claims are certain.
# B says "A said 'I am a knave'.", and A is in fact a knave
# B says "C is a knave."
# C says "A is a knight."
# there is consistency between the statements, honesty rules, and mutual exclusivity of roles
knowledge3 = And(
    common_knowledge,

    # for entities A and B
    Implication(BKnight, And(Implication(AKnight, AKnave),
                             Implication(AKnave, Not(AKnave)))),

    Implication(BKnight, Not(And(Implication(AKnight, AKnave),
                                 Implication(AKnave, Not(AKnave))))),

    # for entities B and C
    Implication(BKnight, CKnave),

    Implication(BKnave, Not(CKnave)),

    # for entities C and A
    Implication(CKnight, AKnight),

    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
