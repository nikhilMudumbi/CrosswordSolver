import fitz  # PyMuPDF
from PIL import Image
import numpy as np


def pdf_to_images(pdf_path):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    images = []

    # Iterate through each page
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        # Render page to an image
        pix = page.get_pixmap()
        # Convert the image to a PIL image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    return images

def findLineBorder(imageArr, width):
    for w in range(width - 1, width - 102, -1):
        for h in range(0, 101):
            pixel = imageArr[w][h]
            if pixel[0] != 255 or pixel[1] != 255 or pixel[2] != 255:
                return [w,h]

def findGridCorner(imageArr, lineBorder):
    for w in range(lineBorder[0] - 1, lineBorder[0] - 25, -1):
        for h in range(lineBorder[1] + 1, lineBorder[1] + 25):
            pixel = imageArr[w][h]
            if pixel[0] != 255 or pixel[1] != 255 or pixel[2] != 255:
                return [w,h]

def findSquareSize(imageArr, gridCorner):
    for w in range(gridCorner[0] - 1, gridCorner[0] - 50, -1):
        pixel = imageArr[w][gridCorner[1] + 10]
        if pixel[0] != 255 or pixel[1] != 255 or pixel[2] != 255:
            return gridCorner[0] - w

def checkForNumber(imageArr, i, j, gridCorner, squareSize):
    squareStart = [gridCorner[0] - (14 - j) * squareSize, gridCorner[1] + i * squareSize]
    if i == 1:
        print("j ==", j, ", start ==", squareStart)
    for w in range(squareStart[0] - 5, squareStart[0] - squareSize, -1):
        if imageArr[w][squareStart[1] + 3][0] != 255:
            if i == 1:
                print(imageArr[w][squareStart[1] + 3][0], ", ", squareStart[0] - 1 - w)
            return True
    return False

def print_crossword_grid(crosswordGrid):
    for row in crosswordGrid:
        line = ""
        for cell in row:
            if cell == -1:
                line += "███ "  # Black square representation
            elif cell == 0:
                line += "    "  # Empty white square representation
            else:
                line += f" {cell:2} "  # Labeled white square representation
        print(line)

def make_grid(pdf_path):
    pictures = pdf_to_images(pdf_path)
    imageArr = np.array(pictures[0])
    if imageArr.shape[0] > imageArr.shape[1]:
        imageArr = np.transpose(imageArr, (1, 0, 2))  # make sure the image is in portrait layout
    width = imageArr.shape[0]
    height = imageArr.shape[1]
    lineBorder = findLineBorder(imageArr, width)
    gridCorner = findGridCorner(imageArr, lineBorder)
    gridCorner[0] -= 1
    gridCorner[1] += 1
    #squareSize = findSquareSize(imageArr, gridCorner)
    squareSize = 21
    starting = [gridCorner[0] - 10, gridCorner[1] + 10]
    crosswordGrid = [
        [(0 if imageArr[starting[0] - squareSize * (14 - j)][starting[1] + squareSize * i][0] == 255 else -1)
         for j in range(15)] for i in range(15)]

    count = 1
    for i in range(15):
        for j in range(15):
            if crosswordGrid[i][j] == 0:
                if i == 0 or j == 0 or crosswordGrid[i - 1][j] == -1 or crosswordGrid[i][j - 1] == -1:
                    crosswordGrid[i][j] = count
                    count += 1

    questionPositions = [[]] * (count - 1)
    for i in range(15):
        for j in range(15):
            if crosswordGrid[i][j] > 0:
                horLength = 1
                vertLength = 1
                while j + horLength < 15 and crosswordGrid[i][j + horLength] >= 0:
                    horLength += 1
                while i + vertLength < 15 and crosswordGrid[i + vertLength][j] >= 0:
                    vertLength += 1
                questionPositions[crosswordGrid[i][j] - 1] = [i, j, horLength, vertLength]

    return crosswordGrid, questionPositions
