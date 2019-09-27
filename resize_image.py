import os
import os.path as path
import sys

import json

import skimage.io as ski_io
import skimage.transform as ski_transform

cwd = path.dirname(sys.argv[0])

print("cwd:", cwd)

image_type = {
    ".png": True,
    ".jpg": True,
    ".jpeg": True,
    ".dds": True,
    ".tiff": True,
}

def list_all_files(resultpath, findpath, files):
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
            if image_type.get(ext.lower()):
                files.append(fullpath)
    
    list_all_files_ex(findpath, files)

def resize_image(imgpath, factor, dstpath):
    try:
        img = ski_io.imread(imgpath)
    except SyntaxError:
        print("read image failed with SyntaxError")
        return False

    shape = img.shape

    def recalc_shape_size():
        if  isinstance(factor[0], int) and isinstance(factor[1], int):
            return factor

        assert(isinstance(factor[0], float) and isinstance(factor[1], float))
        return (int(shape[0]*factor[0]), int(shape[1]*factor[1]))


    shapesize = recalc_shape_size()
    print("shape size from:", shape[0], shape[1], ", to", shapesize[0], shapesize[1])

    try:
        transformd_img = ski_transform.resize(img, 
                        (shapesize[0], shapesize[1]),
                        anti_aliasing=True)
    except SyntaxError:
        print("resize image failed with SyntaxError")

    try:
        parentpath = path.dirname(dstpath)
        if not path.exists(parentpath):
            os.makedirs(parentpath)
    except IOError:
        print("os.makedirs failed:", parentpath)
        
    try:
        ski_io.imsave(dstpath, transformd_img)
    except:
        print("save file failed", dstpath)
    return True

def parse_factor(factor_cfg):
    elems = factor_cfg.split("x")
    numelem = len(elems)
    def tofloat(v):
        try:
            return float(v)
        except:
            return 0.0

    if numelem == 1:
        return (tofloat(elems[0]), elems[0])
    
    assert(numelem == 2)
    def tonumber(v):
        pos = v.find(".")
        if pos != -1:
            return tofloat(v)
        try:
            return int(v)
        except:
            return 0

    return (tonumber(elems[0]), tonumber(elems[1]))

def parse_args():
    cfg = {}
    paths = []
    for idx in range(1, len(sys.argv)):
        arg = sys.argv[idx]
        paris = arg.split('=')
        if len(paris) > 1:
            cfg[paris[0]] = paris[1]
        else:
            paths.append(paris[0])
    
    return (cfg, paths)


def fetch_convert_paths():
    cfgfile = path.join(cwd, "config.json")
    if path.exists(cfgfile):
        ff = open(cfgfile)
        cfg = json.load(ff)
        paths = cfg.get("paths")
        if paths:
            cfg["paths"] = None
        return (cfg, paths)
    else:
        print("config.json not found")
        return (None, None)

def merge_setting(lhs, rhs):
    lhs_cfg = lhs[0]
    rhs_cfg = rhs[0]
    lhs_paths = lhs[1]
    rhs_paths = rhs[1]

    cfg = {}
    if lhs_cfg:
        for k in lhs_cfg.keys():
            cfg[k] = lhs_cfg[k]
    
    if rhs_cfg:
        if k in rhs_cfg.keys():
            if cfg.get(k) == None:
                cfg[k] = rhs_cfg[k]

    paths = []
    if lhs_paths:
        paths.extend(lhs_paths)
    if rhs_paths:
        paths.extend(rhs_paths)

    return (cfg, paths)
    

if __name__ == "__main__":
    settings = merge_setting(parse_args(), fetch_convert_paths())

    cfg = settings[0]
    paths = settings[1]

    factorcfg = cfg.get("factor")
    if not factorcfg:
        factorcfg = "0.5"

    factor = parse_factor(factorcfg)

    print("factor:", factor)

    print("convert path:")
    paths_valid = []
    for p in paths:
        if path.exists(p):
            paths_valid.append(p)
            print(p)
        else:
            print(p, "path is not vaild")

    paths = paths_valid

    print("setting:")
    for k in cfg.keys():
        print(k, cfg[k])

    for cvtpath in paths:
        dstpath = path.join(cvtpath, "results")
        if not path.exists(dstpath):
            os.mkdir(dstpath)
        
        files = []
        list_all_files(dstpath, cvtpath, files)
        
        for f in files:
            resultfile = path.join(dstpath, path.relpath(f, cvtpath))
            try:
                if resize_image(f, factor, resultfile):
                    print("resize image successed:", f)
                else:
                    print("resize image failed:", f)
            except:
                print("resize image failed, unkonw error:", f)
