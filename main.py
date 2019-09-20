import os
import os.path as path
import sys

import skimage.io as ski_io
import skimage.transform as ski_transform

image_type = {
    ".png": True,
    ".jpg": True,
    ".jpeg": True,
    ".dds": True,
    ".tiff": True,
}

def list_all_files(rootpath, findpath, files):
    resultpath = path.join(rootpath, "results")
    def list_all_files_ex(currentpath, files):
        for p in os.listdir(currentpath):
            fullpath = path.join(currentpath, p)

            #exclude results path
            if fullpath == resultpath:
                continue

            if os.path.isdir(fullpath):
                list_all_files_ex(p, files)
                continue

            ext = path.splitext(fullpath)[1]
            if image_type.get(ext):
                files.append(fullpath)
    
    list_all_files_ex(findpath, files)

def resize_image(imgpath, factor, dstpath):
    img = ski_io.imread(imgpath)
    shape = img.shape
    transformd_img = ski_transform.resize(img, 
                    (shape[0]*factor, shape[1]*factor),
                    anti_aliasing=True)
    os.makedirs(os.path.dirname(dstpath))
    ski_io.imsave(dstpath, transformd_img)

if __name__ == "__main__":
    setting = {}
    for arg in sys.argv:
        params = arg.split("=")
        setting[params[1]] = params[2]
    
    currentpath = setting.get("src")
    if not currentpath:
        currentpath = os.getcwd()

    dstpath = setting.get("dst")
    if dstpath:
        path.join(dstpath)
    else:
        dstpath = path.join(os.getcwd(), "results")

    factor = setting.get("factor")
    if not factor:
        factor = 0.5

    files = []
    rootpath = os.getcwd()
    list_all_files(path.dirname(dstpath), currentpath, files)
    
    for f in files:
        resultfile = path.join(dstpath, os.path.relpath(f, currentpath))
        resize_image(f, factor, resultfile)

     