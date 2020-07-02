import numpy as np #이미지 좌표를 찾기 위한 배열을 위해 선언
import os # 지정된 폴도내의 파일들을 열기위해
from shapely.geometry import Polygon

'''
#iou를 추출하기 위한 함수 ( 직사각형이나 정사각형과 같은 두개의 좌표만 있을시->상황에 선택해서 사용)
def bb_intersection_over_union(boxA, boxB):
	# 교차 사각형의 (x, y) 좌표를 결정
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    
    # 교차 사각형의 면적을 계산
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    
    # 직사각형
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

'''
#두번쨰 과정) 다각형 꼴 바운더리에 대한 iou를 구하기 위함->상황에 맞게 bb_intersection_over_union 중에서 선택해서 사용
def calculate_iou(box_1, box_2):
    poly_1 = Polygon(box_1)
    poly_2 = Polygon(box_2)
    iou = poly_1.intersection(poly_2).area / poly_1.union(poly_2).area
    return iou

def score(TP,FN,FP,TN):
    Precision = (TP / (TP + FP))*100
    Recall = (TP / (TP + FN))*100
    Accuracy = ((TP + TN) / (TP + FP + FN + TN))*100
    F1score = 2 * (Precision * Recall / (Precision + Recall))
    print(round(Precision,2),"%, ",round(Recall,2),"%, ",round(Accuracy,2),"%, ",round(F1score,2))

def Ocr_ouput():


    list = os.listdir(word_box_file)
    for item in list:
        filename, fileExtension = os.path.splitext(item)
        try:  # (FileNotFoundError)파일을 찾을 수 없는경우에 대한 오류를 피하기 위한 코드

            if (fileExtension==".txt"): #확장자가 .txt파일인것만 검증
                file=filename+fileExtension

                with open(word_box_file+"/" + file, 'r') as f1:
                    total_word_count=0
                    total_scr_count=0
                    TP = 0
                    check=0

                    with open(east_file + "/" + file, 'r') as f2:

                        for line1 in f1:

                            total_word_count+=1
                            rd = line1.replace("\n", "").split("\t")
                            rd.pop(0)
                            box1=[[int(rd[0]),int(rd[1])],
                                  [int(rd[2]),int(rd[3])],
                                  [int(rd[4]),int(rd[5])],
                                  [int(rd[6]),int(rd[7])]]

                            for line2 in f2:
                                rd2=line2.strip().split(",")
                                if (len(rd2)>1):
                                    total_scr_count+=1
                                    box2 = [[int(rd2[0]), int(rd2[1])],
                                        [int(rd2[2]), int(rd2[3])],
                                        [int(rd2[4]), int(rd2[5])],
                                        [int(rd2[6]), int(rd2[7])]]
                                    
                                    iou=calculate_iou(box1,box2)

                                    #scr의 총 박스 좌표를 자료형(리스트, 튜플, 딕셔너리 등)로 만들고 싶다면 여기 라인에 삽입하는 코드를 작성하면 됌

                                    if (iou>0.7): #면적에 대한 비율 조정
                                        TP +=1
                                        check +=1
                                        # TF좌표 확인,(변형이 필요시)여기 라인에서 다른 파일에 기록하거나, 배열에 삽입하는 등의 코드를 작성하면 됌
                                        #print(box1,"->",box2," : TF")

                            ''' 
                            if(check==0):
                                #FN좌표 확인,(변형이 필요시)여기 라인에서 다른 파일에 기록하거나, 배열에 삽입하는 등의 코드를 작성하면 됌
                                print(box1," : FN") 
                            check=0
                            '''

                            f2.seek(0)
                            FP=total_scr_count-TP
                            TN=0
                            total_scr_count=0

                        FN=total_word_count-TP


                        #print(TP, FN, FP, TN)
                        print(filename, "의 Precision,Recall,Accuracy,F1score: ", end=" ")
                        score(TP,FN,FP,TN)





        except FileNotFoundError: #(FileNotFoundError)오류발생시 무시하고, 프로세스 계속진행
            pass



east_file="src"
word_box_file="word_box"
Ocr_ouput()



'''
#1) 첫번째 과정:이미지 좌표 찾기 위함 과정-> 쥬피터 혹은 cv 이용
import cv2, sys
from matplotlib import pyplot as plt
image = cv2.imread('src/com.elevenst_0001.jpg')
b, g, r = cv2.split(image)
image2 = cv2.merge([r, g, b])



cv2.rectangle(image, (0, 0), (550, 550), (0, 255, 0))

cv2.imshow('img', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

plt.imshow(image)
plt.xticks([])
plt.yticks([])
plt.show()
'''

