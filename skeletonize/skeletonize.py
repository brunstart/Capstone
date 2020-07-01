from skimage import img_as_bool, io, color, morphology
import matplotlib.pyplot as plt
from skimage.util import invert
from skimage.morphology import skeletonize
import os

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
    image = img_as_bool(color.rgb2gray(io.imread(files[i])))
    out = skeletonize(image)

    f, (ax0, ax1) = plt.subplots(1, 2)
    ax0.imshow(image, cmap='gray')
    ax0.axis('off')
    ax0.set_title('original', fontsize=20)

    ax1.imshow(out, cmap='gray')
    #skeletonzie한 결과 저장
    io.imsave(result_path+file_list[i], out)
    ax1.axis('off')
    ax1.set_title('skeleton', fontsize=20)
    #출력 결과보려면 plt.show() 주석처리 제거
    #plt.show()
