import string

import numpy as np
from AppCode.ImageProcessing import make_grid
from AppCode.TextProcessing import accessQuestions
import ollama

M = 15
N = 15
crosswordGrid = None
questionPositions = None
pdf = None
questions = None
grid = np.full((M, N), ' ', dtype='<U1')

def gridExtraction(pdf_path):
    global crosswordGrid
    global questionPositions
    global pdf
    pdf = pdf_path
    crosswordGrid, questionPositions = make_grid(pdf_path)
    print(crosswordGrid)
    return crosswordGrid

def questionExtraction():
    global questions
    questions = accessQuestions(pdf, questionPositions)

def correctLetters(word, existingLetters):
    for i in range(len(word)):
        if existingLetters[i] != " " and word[i] != existingLetters[i]:
            return False
    return True

def getAnswers(clue, size, number, sensitivity, existingLetters):
    ''' gets answers for a given question, given existing letters
    by asking the LLM repeatedly and looking for common answers '''
    pluralTest = "Is the phrase '" + clue + "' singular or plural? Just give one of those two words as the answer"
    response = ollama.chat(model='llama3', messages=[
        {
        'role': 'user',
        'content': pluralTest,
        },
    ])
    pluralBool = response['message']['content'].lower() == "plural"
    text = "What's an answer to the crossword clue \"" + clue + "\"? Give nothing else except the answer. The answer MUST have exactly " + str(size) + " letters"
    if pluralBool:
        text += " and should be plural. "
    else:
        text += ". "
    existing = False
    for i in range(len(existingLetters)):
        if existingLetters[i] != " ":
            text += "letter #" + str(i+1) + " should be " + existingLetters[i] + ", "
            existing = True
    if existing:
        text = text[:-2]
    text += " Forget all previous answers."
    answersFrequency = {}

    translator = str.maketrans('', '', string.punctuation + ' ')
    for i in range(number):
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        answer = response['message']['content'].upper().translate(translator)
        answersFrequency[answer] = answersFrequency.setdefault(answer, 0) + 1
    for word, freq in answersFrequency.items():
        if len(word) == size and freq >= sensitivity and correctLetters(word, existingLetters):
            return word
    return ""

def print_final_grid():
    ''' for debugging purposes '''
    for i in range(M):
        row = ""
        for j in range(N):
            if crosswordGrid[i][j] == -1:
                row += " █ "
            else:
                row += " " + grid[i][j] + " "
        print(row)

def step(number, sensitivity):
    ''' makes one pass through the grid, filling in each question based on
    common answers from LLM and existing letters'''
    count = 0
    for q in questions:
        count += 1
        existingLetters = []
        for i in range(q.size):
            existingLetters.append(grid[q.starting[0]][q.starting[1] + i] if q.orientation else grid[q.starting[0] + i][q.starting[1]])
        answer = getAnswers(q.question, q.size, number, sensitivity, existingLetters)
        if answer != "":
            for i in range(q.size):
                if q.orientation:
                    grid[q.starting[0]][q.starting[1] + i] = answer[i]
                else:
                    grid[q.starting[0] + i][q.starting[1]] = answer[i]
    print_final_grid()

def initialize():
    questionExtraction()


def stepSolver():
    ''' one method of solving that makes four passes through
    the grid and iteratively fills in, demanding less accuracy
    each time '''
    step(5, 5)
    step(5, 3)
    step(5, 1)
    step(5, 1)
    return grid

