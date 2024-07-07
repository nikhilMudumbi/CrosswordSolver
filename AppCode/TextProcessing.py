import pdfminer.high_level as reader

from AppCode.Question import Question


def accessQuestions(pdf_path, questionPositions):
    text = reader.extract_text(pdf_path)
    textList = text.splitlines()
    print(textList)

    questionList = []

    # reading across questions

    acrossPos = textList.index("ACROSS")
    downPos = textList.index("DOWN")

    print(acrossPos)

    currQuestion = ""
    index = 0
    for i in range(acrossPos + 1, downPos):
        line = textList[i]
        if len(line) == 0:
            continue
        try:
            spaceIndex = line.index(" ")
        except ValueError:
            continue
        if line[:spaceIndex].isdigit():
            if currQuestion != "":
                q = questionPositions[index-1]
                questionList.append(Question(currQuestion, index, q[2], True, [q[0], q[1]]))
            index = int(line[:spaceIndex])
            currQuestion = line[(spaceIndex + 1):]
        else:
            currQuestion += line

    currQuestion = ""
    ignore = False
    for i in range(downPos, len(textList)):
        line = textList[i]
        if len(line) == 0:
            continue
        try:
            spaceIndex = line.index(" ")
        except ValueError:
            continue
        if line[:spaceIndex].isdigit():
            if line[(spaceIndex + 1):] == " " and ignore:
                continue
            if currQuestion != "":
                q = questionPositions[index-1]
                if index == 8:
                    print([q[0], q[1]])
                questionList.append(Question(currQuestion, index, q[3], False, [q[0], q[1]]))
            index = int(line[:spaceIndex])
            currQuestion = line[(spaceIndex + 1):]
            if line[(spaceIndex+1):] == "" or line[(spaceIndex+1):] == " ":
                ignore = True
                continue
        else:
            currQuestion += line

    return questionList
