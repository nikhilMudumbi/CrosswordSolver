import numpy as np
from langchain_openai import ChatOpenAI
from ImageProcessing import make_grid
from Question import Question
from TextProcessing import accessQuestions
import ollama
import string
from typing import List
from collections import deque
import random
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
N = 15
M = 15

pdf_path = "/Users/nikhil/Downloads/LA Times, Mon, Jun 24, 2024.pdf"
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

crosswordGrid, questionPositions = make_grid(pdf_path)
questions = accessQuestions(pdf_path, questionPositions)

grid = np.full((M, N), ' ', dtype='<U1')

def AC3(questionList: List[Question]):
    adjList = np.empty(len(questionList), dtype=object)
    # generating edges
    for i in range(len(questionList)):
        adjList[i] = []

    queue = deque()

    for i, q1 in enumerate(questionList):
        for j, q2 in enumerate(questionList):
            if q1.orientation + q2.orientation == 1:
                xDist = abs(q1.starting[0] - q2.starting[0]) + 1
                yDist = abs(q1.starting[1] - q2.starting[1]) + 1
                if q1.orientation and yDist <= q1.size and xDist <= q2.size:
                    adjList[i].append(j)
                    adjList[j].append(i)
                    queue.append([i,j])
                elif q2.orientation and yDist <= q2.size and xDist <= q1.size:
                    adjList[i].append(j)
                    adjList[j].append(i)
                    queue.append([i,j])

    while queue:
        con = queue.popleft()
        q1 = questionList[con[0]]
        q2 = questionList[con[1]]
        if q1.orientation:
            pos1 = q2.starting[1] - q1.starting[1]
            pos2 = q1.starting[0] - q2.starting[0]
        else:
            pos1 = q2.starting[0] - q1.starting[0]
            pos2 = q1.starting[1] - q2.starting[1]
        deletionList = []
        modified = False
        for words1 in q1.potentialAnswers:
            matchExists = False
            for words2 in q2.potentialAnswers:
                matchExists = words1[pos1] == words2[pos2]
            if not matchExists:
                modified = True
                deletionList.append(words1)
        q1.potentialAnswers = [word for word in q1.potentialAnswers if word not in deletionList]
        '''if modified:
            for k in adjList[con[0]]:
                if k != con[1]:
                    queue.append([con[0],k])'''
        deletionList = []
        modified = False
        for words2 in q2.potentialAnswers:
            matchExists = False
            for words1 in q1.potentialAnswers:
                matchExists = words2[pos2] == words1[pos1]
            if not matchExists:
                modified = True
                deletionList.append(words2)
        q2.potentialAnswers = [word for word in q2.potentialAnswers if word not in deletionList]
        '''if modified:
            for k in adjList[con[1]]:
                if k != con[0]:
                    queue.append([con[1], k])'''

def generatePossibleWords(questionList: List[Question]):
    for i, q in enumerate(questionList):
        print("index, ", i)
        text = ("Give me 10 different answers to the crossword clue \""
                + q.question + "\". Each answer should have exactly " + str(q.size) + " letters. Put each answer on a separate line")
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        words = response['message']['content'].split("\n")
        for line in words:
            word = []
            for c in line:
                if c.isalpha():
                    word.append(c.upper())
            if len(word) == q.size:
                q.potentialAnswers.append("".join(word))
                sentences = [q.potentialAnswers[-1], q.question]
                embeddings = model.encode(sentences)
                q.answerWeights.append(np.exp(2 * (1 - cosine(embeddings[0], embeddings[1]))))
                sum = 0
                for weight in q.answerWeights:
                    sum += weight
                for i in range(len(q.answerWeights)):
                    q.answerWeights[i] /= sum

def trackGrid(questionList, gridPositions):
    for i in range(len(questionList)):
        q = questionList[i]
        pos = [q.starting[0], q.starting[1]]
        for i in range(q.size):
            gridPositions[pos[0]][pos[1]].append(i)
            if q.orientation:
                pos[1] += 1
            else:
                pos[0] += 1

def clearWord(q):
    pos = [q.starting[0], q.starting[1]]
    for i in range(q.size):
        grid[pos[0]][pos[1]] = ' '
        if q.orientation:
            pos[1] += 1
        else:
            pos[0] += 1

def simulatedAnnealing(questionList, time, param, gridPositions):
    for t in range(time):
        if t < time / 10:
            T = param
        else:
            T = np.exp(((time / 10) - t) * (6 / time)) * param
        randomIndex = random.randint(0, len(questionList) - 1)
        randomQuestion = questionList[randomIndex]
        if len(randomQuestion.potentialAnswers) == 0:
            continue
        print(str(randomIndex) + ", " + randomQuestion.question + ", " + str(randomQuestion.size))
        print(randomQuestion.starting)
        randomWord = np.random.choice(randomQuestion.potentialAnswers, p = randomQuestion.answerWeights)
        contradictions = 0
        pos = [randomQuestion.starting[0], randomQuestion.starting[1]]
        for i in range(randomQuestion.size):
            if grid[pos[0]][pos[1]] != ' ' and randomWord[i] != grid[pos[0]][pos[1]]:
                contradictions += 1
            if randomQuestion.orientation:
                pos[1] += 1
            else:
                pos[0] += 1
        if random.randint(0, 1) < np.exp(-contradictions / T):
            pos = [randomQuestion.starting[0], randomQuestion.starting[1]]
            for i in range(randomQuestion.size):
                if grid[pos[0]][pos[1]] != ' ':
                    for j in gridPositions[pos[0]][pos[1]]:
                        if j != randomIndex:
                            clearWord(questionList[j])
                grid[pos[0]][pos[1]] = randomWord[i]
                if randomQuestion.orientation:
                    pos[1] += 1
                else:
                    pos[0] += 1



def correctLetters(word, existingLetters):
    for i in range(len(word)):
        if existingLetters[i] != " " and word[i] != existingLetters[i]:
            return False
    return True

def getAnswers(clue, size, number, sensitivity, existingLetters):

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
        print(i)
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

def step(number, sensitivity):
    count = 0
    for q in questions:
        print("question count ==", count)
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

def oneStep():
    currQuestions = []
    for q in questions:
        if not q.finished:
            currQuestions.append(((str(q.size) + " letters required - " + q.question + "\n"), q)) # (str(len(currQuestions)+1)) + ". " +
    text = "Answer the following crossword questions. It is extremely important that the answer has the required number of letters (not counting punctuation or spaces). Just give the answers, don't say \"Here are the answers\": \n"
    submittingText = text
    answers = []
    for i in range(len(currQuestions)):
        print("i ==", i)
        #print(currQuestions[i][1].size)
        if i % 1 == 0 and i > 0:
            response = ollama.chat(model='llama3', messages=[
                {
                    'role': 'user',
                    'content': submittingText,
                },
            ])
            answers += response['message']['content'].split("\n")
            submittingText = ""
        submittingText += "What's a " + str(currQuestions[i][1].size) + " letter answer to the crossword clue " + currQuestions[i][0] + "? Give nothing else except the answer." # (str((i % 5) + 1) + ". ") +
    if submittingText != "":
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': submittingText,
            },
        ])
        answers += response['message']['content'].split("\n")

    print(answers)
    for i, a in enumerate(answers):
        print("i ==", i, ", a == ", a)
        newA = ""
        for char in a:
            if char.isalpha():
                newA += char.upper()
        question = currQuestions[i][1]
        if len(newA) == question.size:
            mistakes = False
            for i in range(question.size):
                mistakes = (newA[i] == grid[question.starting[0]][question.starting[1] + i] if question.orientation \
                    else grid[question.starting[0] + i][question.starting[1]])
            if not mistakes:
                for i in range(question.size):
                    if question.orientation:
                        grid[question.starting[0]][question.starting[1] + i] = newA[i]
                    else:
                        grid[question.starting[0] + i][question.starting[1]] = newA[i]

def print_final_grid():
    for i in range(M):
        row = ""
        for j in range(N):
            if crosswordGrid[i][j] == -1:
                row += " █ "
            else:
                row += " " + grid[i][j] + " "
        print(row)

