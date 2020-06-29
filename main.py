import os
import sys
import configparser
import requests
import time
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
from PIL import Image     #pip install pillow
import json

#Config Parser 초기화
config = configparser.ConfigParser()
#Config File 읽기
config.read(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'envs' + os.sep + 'property.ini')

def ocrToStr(fullPath, outTxtPath, fileName):
    missing_env = False
    # Add your Computer Vision subscription key and endpoint to your environment variables.
    if 'COMPUTER_VISION_ENDPOINT' in os.environ:
        endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
    else:
        print("From Azure Cogntivie Service, retrieve your endpoint and subscription key.")
        print(
            "\nSet the COMPUTER_VISION_ENDPOINT environment variable, such as \"https://westus2.api.cognitive.microsoft.com\".\n")
        missing_env = True

    if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
        subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
    else:
        print("From Azure Cogntivie Service, retrieve your endpoint and subscription key.")
        print(
            "\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable, such as \"1234567890abcdef1234567890abcdef\".\n")
        missing_env = True

    if missing_env:
        print("**Restart your shell or IDE for changes to take effect.**")
        sys.exit()

    analyze_url = endpoint + "/vision/v3.0/read/analyze"

    image_path = fullPath
    aaa = os.path.splitext(os.path.basename(fullPath))

    print(aaa)

    boxName = os.path.join(outTxtPath, 'box', aaa[0])
    txtName = os.path.join(outTxtPath, aaa[0])

    image_data = open(image_path, "rb").read()
    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}
    params = {'visualFeatures': 'Categories,Description,Color'}
    response = requests.post(analyze_url, headers=headers, params=params, data=image_data)
    response.raise_for_status()

    # Extracting text requires two API calls: One call to submit the
    # image for processing, the other to retrieve the text found in the image.

    # Holds the URI used to retrieve the recognized text.
    operation_url = response.headers["Operation-Location"]

    analysis = {}
    poll = True
    while (poll):
        response_final = requests.get(
            response.headers["Operation-Location"], headers=headers)
        analysis = response_final.json()

        #print(json.dumps(analysis, indent=4))

        time.sleep(1)
        if ("analyzeResult" in analysis):
            poll = False
        if ("status" in analysis and analysis['status'] == 'failed'):
            poll = False

    polygons = []
    if ("analyzeResult" in analysis):
        # Extract the recognized text, with bounding boxes.
        polygons = [(line["boundingBox"], line["text"])
                    for line in analysis["analyzeResult"]["readResults"][0]["lines"]]
        boxToTxt(boxName, polygons)
        txtToTxt(txtName, polygons)


def boxToTxt(txtName, polygons):
    with open(txtName + '.txt', 'w', encoding='utf-8') as f:
        for i in polygons:
            f.write(str(i[0]) + '\n')

def txtToTxt(txtName, polygons):
    with open(txtName + '.txt', 'w', encoding='utf-8') as f:
        for i in polygons:
            f.write(str(i[1]) + '\n')


def scoreOcr(fullPath):

    image_path = fullPath
    aaa = os.path.splitext(os.path.basename(fullPath))

    img = Image.open(fullName)
    width, height = img.size

    txtName = aaa[0] + '.txt'

    # box 위지 정답이 있는 폴더
    wlist = os.path.dirname(os.path.realpath(__file__)) + config['Path']['boxAnswerPath'] + '/' + txtName

    # ms ocr 가 예측한 위치가 있는 폴더
    plist = os.path.dirname(os.path.realpath(__file__)) + config['Path']['OcrTxtPath'] + '/box/' + txtName

    # 정답
    ans_image = [[0 for i in range(width)] for j in range(height)]

    # 나의 예측
    my_image = [[0 for i in range(width)] for j in range(height)]

    with open(wlist, 'r') as f:  # f = 정답
        with open(plist, 'r') as fd:  # fd = ms ocr 예측 결과

            while True:
                rd = f.readline()
                rd = rd.replace("\n", "").split("\t")
                rd.pop(0)
                rd2 = fd.readline()
                rd2 = rd2.lstrip('[')
                strr = rd2.replace("]\n", "").split(", ")

                if strr[0] == '':
                    strr = []

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

    acc = round(accuracy_score(my_image, ans_image), 2)
    prec = round(precision_score(my_image, ans_image, average='macro'), 2)
    reca = round(recall_score(my_image, ans_image, average='micro'), 2)
    f1 = round(f1_score(my_image, ans_image, average='micro'), 2)

    print(fname + '의 측정결과:\t Accuracy =', acc, '\tPrecision =', prec, '\tRecall =', reca, '\tF1 score = ', f1)
    st.write(str(fname) + '\t' + str(acc) + '\t' + str(prec) + '\t' +
             str(reca) + '\t' + str(f1) +'\n')

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
                #print(fullName)
                #한글+영어 추출(kor, eng , kor+eng)
                ocrToStr(fullName, outTxtPath, fname)
                time.sleep(5)

                scoreOcr(fullName)
                print()