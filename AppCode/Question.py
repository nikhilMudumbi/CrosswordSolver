class Question:
    def __init__(self, question, number, size, orientation, starting):
        self.question = question
        self.number = number
        self.size = size
        self.answerWeights = []
        self.orientation = orientation # true means horizontal, false means vertical
        self.starting = starting
        self.finished = False
        self.potentialAnswers = []