import numpy as np
import os # 지정된 폴도내의 파일들을 열기위해
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score # 각 값들을 산출하기 위해
from PIL import Image # 이미지 크기를 가져오기 위해

def Ocr_ouput():
    '''
    files = []
    exts = ['jpg', 'png', 'jpeg', 'JPG']
    for parent, dirnm, filenms in os.walk("word_box"):
        for filenm in filenms:
            for ext in exts:
                if filenm.endswith(ext):
                    files.append(os.path.join(parent, filenm))
                    print(files)
                    break
    '''

    list = os.listdir("word_box")  # 현재 경로 폴더의 파일들을 불러온다.

    for item in list:

        filename, fileExtension = os.path.splitext(item)

        img = Image.open("word_box/"+filename+".jpg")
        width, height = img.size

        ans_image = [[0 for i in range(width)] for j in range(height)]

        my_image = [[0 for i in range(width)] for j in range(height)]

        with open("word_box/"+filename+".txt", 'r') as f1:
            with open("src/"+filename+".txt", 'r') as f2:

                while True:
                    rd = f1.readline()
                    rd = rd.replace("\n", "").split("\t")
                    rd.pop(0)
                    rd2 = f2.readline()

                    strr = rd2.strip('\n').split(",")
                    if len(strr)==1:
                        rd2 = f2.readline()
                        strr = rd2.strip('\n').split(",")

                    if strr[0] == '':
                        strr = []

                    if rd:
                        a_xmin = int(rd[0])
                        a_xmax = int(rd[2])
                        a_ymin = int(rd[1])
                        a_ymax = int(rd[5])

                        for a in range(height):
                            for b in range(width):
                                if a >= a_ymin and a <= a_ymax and b >= a_xmin and b <= a_xmax:
                                    ans_image[a][b] = 1

                    if strr:
                        p_xmin = int(strr[0])
                        p_xmax = int(strr[2])
                        p_ymin = int(strr[1])
                        p_ymax = int(strr[5])

                        for a in range(height):
                            for b in range(width):
                                if a >= p_ymin and a <= p_ymax and b >= p_xmin and b <= p_xmax:
                                    my_image[a][b] = 1

                    if not strr and not rd:
                        break

        acc = round(accuracy_score(my_image, ans_image), 2)
        prec = round(precision_score(my_image, ans_image, average='macro'), 2)
        reca = round(recall_score(my_image, ans_image, average='micro'), 2)
        fscore = round(f1_score(my_image, ans_image, average='micro'), 2)


        print(filename + '의 측정결과:\t Accuracy =', acc, '\tPrecision =', prec, '\tRecall =', reca, '\tF1 score = ', fscore)





Ocr_ouput()
print()