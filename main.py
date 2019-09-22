import os
import os.path as path
import sys

import json

import skimage.io as ski_io
import skimage.transform as ski_transform

cwd = sys.path[0]

cfgfile = path.join(cwd, "config.json")

cfg = json.load(cfgfile) if os.path.exists(cfgfile) else None

if not cfg:
    print("config file not found:", cfgfile)

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
                if p[0] == ".":
                    continue
                list_all_files_ex(fullpath, files)
                continue

            ext = path.splitext(fullpath)[1]
            if image_type.get(ext):
                files.append(fullpath)
    
    list_all_files_ex(findpath, files)

def resize_image(imgpath, factor, dstpath):
    img = ski_io.imread(imgpath)
    shape = img.shape

    def recalc_shape_size():
        if  isinstance(factor[0], int) and factor[0] > 1 and isinstance(factor[1], int) and factor[1] > 1:
            return factor

        assert(isinstance(factor[0], float) and isinstance(factor[1], float))
        return (shape[0]*factor[0], shape[1]*factor[1])


    shapesize = recalc_shape_size()
    transformd_img = ski_transform.resize(img, 
                    (shapesize[0], shapesize[1]),
                    anti_aliasing=True)
    try:
        os.makedirs(os.path.dirname(dstpath))
    except IOError:
        print("os.makedirs failed")
        
    
    ski_io.imsave(dstpath, transformd_img)

def parse_factor(factor_cfg):
    elems = factor_cfg.split("x")
    numelem = len(elems)
    def check_cvt_to_int(v):
        try:
            return float(v)
        except:
            return None

    if numelem == 1:
        ff = check_cvt_to_int(factor_cfg)
        return (ff, ff)
    
    assert(numelem == 2)
    return (check_cvt_to_int(elems[0]), check_cvt_to_int(elems[1]))

if __name__ == "__main__":
    setting = {}
    for idx in range(1, 4):
        arg = sys.argv[idx]
        params = arg.split("=")
        setting[params[0]] = params[1]
    
    def check_path(name, defpath):
        pp = setting.get("src")
        if pp:
            if not os.path.isabs(pp):
                pp = path.realpath(path.join(cwd, pp))
            return pp
        
        return defpath

    currentpath = check_path("src", cwd)
    dstpath = check_path("dst", path.join(cwd, "results"))

    factorcfg = setting.get("factor")
    if not factorcfg:
        factorcfg = "0.5"

    factor = parse_factor(factorcfg)

    print("src:", currentpath, "dst:", dstpath, "factor:", factor[0], factor[1])

    files = []
    list_all_files(path.dirname(dstpath), currentpath, files)
    
    for f in files:
        resultfile = path.join(dstpath, os.path.relpath(f, currentpath))
        resize_image(f, factor, resultfile)

      