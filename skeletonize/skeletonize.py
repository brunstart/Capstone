from skimage import img_as_bool, io, color, morphology
import matplotlib.pyplot as plt
from skimage.util import invert
from skimage.morphology import skeletonize
import os, cv2

#원본데이터 경로
path = "input/"
#결과데이터 경로
result_path = "result/"

files = []
exts = ['jpg', 'png', 'jpeg', 'JPG']
for parent, dirnames, filenames in os.walk(path):
    for filename in filenames:
        for ext in exts:
            if filename.endswith(ext):
                files.append(os.path.join(parent, filename))
                break

print('Find {} images'.format(len(files)))

file_list = os.listdir(path)

for i in range(0,len(files)):
    img = cv2.imread(files[i], cv2.IMREAD_GRAYSCALE)
    thr = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    blur = cv2.GaussianBlur(thr, (3, 3), 0)

    image = invert(img_as_bool(blur))
    out = skeletonize(image)
    #skeletonzie한 결과 저장
    io.imsave(result_path + file_list[i], out)
    
    f, (ax0, ax1) = plt.subplots(1, 2)
    ax0.imshow(img, cmap='gray')
    ax0.axis('off')
    ax0.set_title('original', fontsize=20)

    ax1.imshow(out, cmap='gray')
    ax1.axis('off')
    ax1.set_title('skeleton', fontsize=20)
    #출력 결과보려면 plt.show() 주석처리 제거
    #plt.show()