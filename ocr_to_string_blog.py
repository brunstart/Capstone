from PIL import Image     #pip install pillow
from pytesseract import * #pip install pytesseract
import configparser
import os
import csv
import cv2
import numpy as np
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

#Config Parser 초기화
config = configparser.ConfigParser()
#Config File 읽기
config.read(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'envs' + os.sep + 'property.ini')

#이미지 -> 문자열 추출
def ocrToStr(fullPath, outTxtPath, fileName, lang='eng'): #디폴트는 영어로 추출
    #이미지 경로

    img = Image.open(fullPath)

    width, height = img.size

    aaa = os.path.splitext(os.path.basename(fullPath))
    txtName = os.path.join(outTxtPath, aaa[0])
    txtName2 = os.path.join(outTxtPath, 'word', aaa[0])
    txtName3 = os.path.join(outTxtPath, 'box', aaa[0])
    txtName4 = os.path.join(outTxtPath, 'boox', aaa[0])

    #추출(이미지파일, 추출언어, 옵션)
    #preserve_interword_spaces : 단어 간격 옵션을 조절하면서 추출 정확도를 확인한다.

    #psm(페이지 세그먼트 모드 : 이미지 영역안에서 텍스트 추출 범위 모드)
    #psm 모드 : https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage

    # ocr 텍스트 측정
    outText = image_to_string(img, lang=lang, config='--psm 1 -c preserve_interword_spaces=1')

    # word 정보
    outData = pytesseract.image_to_data(img, lang=lang, config='--psm 1 -c preserve_interword_spaces=1', output_type=Output.DICT)

    # word 정보
    outData2 = pytesseract.image_to_data(img, lang=lang, config='--psm 1 -c preserve_interword_spaces=1')

    # box 정보
    outBox = pytesseract.image_to_boxes(img, lang=lang, config='--psm 1 -c preserve_interword_spaces=1')

    print('+++ OCT Extract Result +++')
    print('Extract FileName ->>> : ', fileName, ' : <<<-')

    scoreOcr(aaa[0], width, height)

    #print('\n\n')

    # 측정한 데이터값 출력
    #print(outData)
    #print(outText)

    #추출 문자 텍스트 파일 쓰기, 사용할 땐 outText의 주석을 풀어주세요
    strToTxt(txtName, outText)

    #측정한 Box의 전체적인 정보를 문서로 저장, 사용할 땐 outData2 의 주석을 풀어주세요
    dataToTxt(txtName4, outData2)

    # 측정한 word의 정보를 문서로 저장, 사용할 땐 outBox 의 주석을 풀어주세요
    boxToTxt(txtName2, outBox)

    # 측정한 바운드 박스 값을 문서로 저장, 사용할 땐 outData 의 주석을 풀어주세요
    #dataToCoo(txtName3, outData)

    #print('\n')

# 바인딩 박스의 4 coordinates 정보를 저장
def dataToCoo(txtName, outData):
    # \resource\ocr_result_txt\box 에 결과 저장
    with open(txtName + '.txt', 'w', encoding='utf-8') as f:
        text = outData

        data = {}
        for i in range(len(text['line_num'])):
            if not (text['text'][i] == '' or text['text'][i].isspace()):
                if text['block_num'][i] in data:

                    if text['line_num'][i] in data[text['block_num'][i]]:
                        data[text['block_num'][i]][text['line_num'][i]].append(
                            (text['text'][i], text['left'][i], text['top'][i], text['width'][i], text['height'][i]))
                    else:
                        # lastLineKey = text['line_num'][i]
                        # line[text['line_num'][i]] = []
                        data[text['block_num'][i]][text['line_num'][i]] = [
                            (text['text'][i], text['left'][i], text['top'][i], text['width'][i], text['height'][i])]
                        # line[lastLineKey].append()

                else:
                    data[text['block_num'][i]] = {}
                    data[text['block_num'][i]][text['line_num'][i]] = [
                        (text['text'][i], text['left'][i], text['top'][i], text['width'][i], text['height'][i])]

        linedata = {}
        idx = 0
        for _, b in data.items():
            for _, l in b.items():
                linedata[idx] = l
                idx += 1
        line_idx = 1
        for _, line in linedata.items():
            xmin, ymin = line[0][1], line[0][2]
            xmax, ymax = (line[-1][1] + line[-1][3]), (line[-1][2] + line[-1][4])
            print("Line {} : {}, {}, {}, {}".format(line_idx, xmin, ymin, xmax, ymax))

            x = [xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax]
            f.write('word')
            for z in x:
                f.write("\t")
                f.write(str(z))

            line_idx += 1

            f.write("\n")

# 개별 단어들의 정보 저장
def dataToTxt(txtName, outData):
    # \ocr_result_txt\word 에 결과 저장
    with open(txtName + '.txt', 'w',  encoding='utf-8') as f:
        f.write(outData)

# 박스의 전체적 정보 저장
def boxToTxt(txtName, outData):
    # # \resource\ocr_result_txt\boox 에 결과 저장
    with open(txtName + '.txt', 'w',  encoding='utf-8') as f:
        f.write(outData)

#문자열 -> 텍스트파일 개별 저장
def strToTxt(txtName, outText):
    # \resource\ocr_result_txt 에 결과 저장
    with open(txtName + '.txt', 'w', encoding='utf-8') as f:
        f.write(outText)

def scoreOcr(txtName, width, height):
    txtName = txtName + '.txt'

    # box 위지 정답이 있는 폴더
    wlist = os.path.dirname(os.path.realpath(__file__)) + config['Path']['boxAnswerPath'] + '/' + txtName

    # tesseract가 예측한 위치가 있는 폴더
    plist = os.path.dirname(os.path.realpath(__file__)) + config['Path']['OcrTxtPath'] + '/box/' + txtName

    # 정답
    ans_image = [[0 for i in range(width)] for j in range(height)]

    # 나의 예측
    my_image = [[0 for i in range(width)] for j in range(height)]


    with open(wlist, 'r') as f:             # f = 정답
        with open(plist, 'r') as fd:        # fd = 테서렉트 예측결과

            while True:
                rd = f.readline()
                rd = rd.replace("\n", "").split("\t")
                rd.pop(0)
                rd2 = fd.readline()
                strr = rd2.replace("\n", "").split("\t")
                strr.pop(0)

                if rd:
                    # 정답 박스의 x,y 좌표의 최대 최소값들. (박스를 직사각형이라 가정한다.)
                    a_xmin = int(rd[0])
                    a_xmax = int(rd[2])
                    a_ymin = int(rd[1])
                    a_ymax = int(rd[5])

                    # 순회하면서 박스 경계선의 안쪽이라 판명된 곳을 1로 채운다
                    for a in range(height):
                        for b in range(width):
                            if a >= a_ymin and a <= a_ymax and b >= a_xmin and b <= a_xmax:
                                ans_image[a][b] = 1

                if strr:
                    # 나의 예측 박스의 x, y 좌표의 최대 최소값들 (박스를 직사각형이라 가정한다.)
                    p_xmin = int(strr[0])
                    p_xmax = int(strr[2])
                    p_ymin = int(strr[1])
                    p_ymax = int(strr[5])

                    # 순회하면서 박스 경계선의 안쪽이라 판명된 곳을 1로 채운다
                    for a in range(height):
                        for b in range(width):
                            if a >= p_ymin and a <= p_ymax and b >= p_xmin and b <= p_xmax:
                                my_image[a][b] = 1

                if not strr and not rd:
                    break
    try:
        acc = round(accuracy_score(my_image, ans_image), 2)
        prec = round(precision_score(my_image, ans_image, average='micro', zero_division=0), 2)
        reca = round(recall_score(my_image, ans_image, average='micro', zero_division=0), 2)
        f1 = round(f1_score(my_image, ans_image, average='micro', zero_division=0), 2)
    except:
        print("에러")

    print(fname + '의 측정결과:\t Accuracy =', acc, '\tPrecision =', prec, '\tRecall =', reca, '\tF1 score = ', f1)
    st.write(str(fname) + '\t' + str(acc) + '\t' + str(prec) + '\t' +
             str(reca) + '\t' + str(f1) + '\n')

#메인 시작
if __name__ == "__main__":

    #텍스트 파일 저장 경로
    outTxtPath = os.path.dirname(os.path.realpath(__file__)) + config['Path']['OcrTxtPath']

    scoreTxt = os.path.dirname(os.path.realpath(__file__)) + '/resource/score.txt'

    with open(scoreTxt, 'w', encoding='utf-8') as st:
        st.write("file name\t\t\t\tAccuracy\tprecision\tRecall\tF1 Score\n")

        #OCR 추출 작업 메인
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__)) + config['Path']['OriImgPath']):
            for fname in files:
                fullName = os.path.join(root, fname)
                #한글+영어 추출(kor, eng , kor+eng)
                ocrToStr(fullName, outTxtPath, fname, 'kor+eng')

                print()
