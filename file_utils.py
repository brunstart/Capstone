# -*- coding: utf-8 -*-
import os
import numpy as np
import cv2
import imgproc

# borrowed from https://github.com/lengstrom/fast-style-transfer/blob/master/src/utils.py
def get_files(img_dir):
    imgs, masks, xmls = list_files(img_dir)
    return imgs, masks, xmls

def list_files(in_path):
    img_files = []
    mask_files = []
    gt_files = []
    for (dirpath, dirnames, filenames) in os.walk(in_path):
        for file in filenames:
            filename, ext = os.path.splitext(file)
            ext = str.lower(ext)
            if ext == '.jpg' or ext == '.jpeg' or ext == '.gif' or ext == '.png' or ext == '.pgm':
                img_files.append(os.path.join(dirpath, file))
            elif ext == '.bmp':
                mask_files.append(os.path.join(dirpath, file))
            elif ext == '.xml' or ext == '.gt' or ext == '.txt':
                gt_files.append(os.path.join(dirpath, file))
            elif ext == '.zip':
                continue
    # img_files.sort()
    # mask_files.sort()
    # gt_files.sort()
    return img_files, mask_files, gt_files

#Accuracuy도 같이 측정함.
def saveResult(img_file, img, boxes, nn, dirname='./result/', verticals=None, texts=None):
        """ save text detection result one by one
        Args:
            img_file (str): image file name
            img (array): raw image contextwh
            boxes (array): array of result file
                Shape: [num_detections, 4] for BB output / [num_detections, 4] for QUAD output
        Return:
            None
        """
        img = np.array(img)

        # make result file list
        filename, file_ext = os.path.splitext(os.path.basename(img_file))

        # result directory
        res_file = dirname + "res_" + filename + '.txt'
        res_img_file = dirname + "res_" + filename + '.jpg'

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        ###정답 파일을 열어서 박스 좌표를 비교한다.
        #os.listdir로 디렉토리 내의 데이터를 확인한다.
        #pC마다 설정해 주기 나름..
        clist = os.listdir('./cmp_data')
        #데이터가 있는 디렉토리의 주소를 구한다.
        ddir = os.path.dirname('./cmp_data/0001.txt')
        #두개를 합쳐서 경로를 만든다.
        jdir = os.path.join(ddir,clist[nn])
        #해당하는 파일이 있는 경로를 연다.
        fs = open(jdir, 'r')

        #정확도를 구하기 위한 기준으로 rd의 길이를 누적시키기 위한 변수 선언
        alen = 0
        plen = 0
        with open(res_file, 'w') as f:
            accu = 0
            pccu = 0
            for i, box in enumerate(boxes):

                poly = np.array(box).astype(np.int32).reshape((-1))
                strResult = ', '.join([str(p) for p in poly]) + '\r\n'


                ##정확도 비교
                #rd가 이미지에 대해 box한 결과 (정답)
                rd = fs.readline()
                rd = rd.replace("\n","").split("\t")
                rd.pop(0)
                alen +=len(rd)
                #strr은 CRAFT가 이미지에대해 box한 결과 (예측)
                strr = strResult.replace(",", "").replace("\r\n", "").split(" ")
                plen +=len(strr)

                try:
                    #예측에 대해 정답이 있는 확률.
                    for i in range(len(strr)):
                        if rd[i] in strr:
                            accu +=1
                        else:
                            accu -=1
                except:
                    accu -=1
                #정답에 대해 예측이 얼마나 맞는지.
                for j in range(len(rd)):
                    if strr[i] in rd:
                        pccu +=1
                    else:
                        pccu -=1

                f.write(strResult)

                poly = poly.reshape(-1, 2)
                cv2.polylines(img, [poly.reshape((-1, 1, 2))], True, color=(0, 0, 255), thickness=2)
                ptColor = (0, 255, 255)
                if verticals is not None:
                    if verticals[i]:
                        ptColor = (255, 0, 0)

                if texts is not None:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    cv2.putText(img, "{}".format(texts[i]), (poly[0][0]+1, poly[0][1]+1), font, font_scale, (0, 0, 0), thickness=1)
                    cv2.putText(img, "{}".format(texts[i]), tuple(poly[0]), font, font_scale, (0, 255, 255), thickness=1)

        # Save result image
        cv2.imwrite(res_img_file, img)

        #Accuracy
        if accu < 0:
            accu *= -1
        r_accu = accu / plen
        #precision
        if pccu < 0:
            pccu *= -1
        r_pccu = pccu / alen
        #Recall
        r_rccu = accu / alen
        #F1 Score
        r_F1score = 2* r_pccu * r_rccu / (r_pccu + r_rccu)
        print(filename, "Accuracy is ", round(r_accu, 2), "Percision is ", round(r_pccu, 2), "Recall is ", round(r_rccu,2), "F1 Score is", round(r_F1score,2))

        return r_F1score
