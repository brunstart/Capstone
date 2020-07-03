import os
import shutil

path = '/Users/Bruns/word_box'                  #기존 파일이 저장되어 있는 디렉토리
newPath = '/Users/Bruns/word_box/new'           #새 파일들을 저장할 디렉토리

file_list = os.listdir(path)                    #기존 파일 디렉토리에서 파일 목록 생성

if not(os.path.isdir(newPath)):                 #새  파일들을 저장할 디렉토리를 생성
    os.makedirs(os.path.join(newPath))

file_list_txt = [file for file in file_list if file.endswith(".txt")]   #txt 파일만 추려냄
file_list_jpg = [file for file in file_list if file.endswith(".jpg")]   #jpg 파일만 추려냄


for i in file_list_txt:                         #텍스트 파일 열기
    f = open(path+"/"+i,'r')
    lines = f.readlines()
    f.close()

    fileNum = 1                                 #새로 생성될 파일 넘버링

    for line in lines:
        fileName = i[:-4] + "_" + str(fileNum) + ".txt"
        imageName = i[:-4] + "_" + str(fileNum) + ".jpg"

        fw = open(newPath+"/"+fileName, "a")
        fw.write(line)
        fw.close()

        shutil.copy(path+"/"+i[:-4]+".jpg",newPath+"/"+imageName)   #lines 수 만큼 image파일 생성

        fileNum = fileNum + 1

