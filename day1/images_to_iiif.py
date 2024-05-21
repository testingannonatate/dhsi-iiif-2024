import os, shlex
from iiif.static import IIIFStatic
import argparse
from pdf2image import convert_from_path

def clean_ext(filename):
    filename, ext = os.path.splitext(filename)
    return ext.strip('.').lower()

def allowed_type(filename):
    ext = clean_ext(filename)
    return ext in ['pdf', 'png', 'jpg', 'jp2', 'jpeg', 'tif', 'tiff']


def clean_files(image_path):
    allfiles = []
    for root_dir, folders, files in os.walk(image_path):
        image_files = list(filter(lambda x: allowed_type(x), files))
        for file in image_files:
            ext = clean_ext(file)
            fullfilepath = os.path.join(root_dir, file)
            if ext == 'pdf':
                images = convert_from_path(fullfilepath)
                for i in range(len(images)):
                    imagefilename = fullfilepath.replace('.pdf', "-{}.jpg".format(str(i)))
                    images[i].save(imagefilename, 'JPEG')
                    allfiles.append(imagefilename)
                os.remove(fullfilepath)
            elif ext != 'jpg' and ext != 'jpeg':
                print('fix jpg')
                os.system('convert {} {}'.format(shlex.quote(fullfilepath), shlex.quote(fullfilepath.replace(ext, 'jpg'))))
                allfiles.append(fullfilepath.replace(ext, 'jpg'))
                os.remove(fullfilepath)
            else:
                allfiles.append(fullfilepath)
    return allfiles



parser = argparse.ArgumentParser(description="A script that converts images into iiif tiles")
parser.add_argument('--root_dir', required=False, help='directory where images are located')
parser.add_argument('--base_url', required=False, help='url for where the images are going to be placed')
parser.add_argument('--dst', required=False, help='destination for where the iiif images are going to be placed')

args = parser.parse_args()

root_dir = args.root_dir if args.root_dir else '../images'
for file in clean_files(root_dir):
    baseurl =  args.base_url if args.base_url else '/'
    subfolder = os.path.dirname(file).replace(root_dir, '').strip('/')
    base_dst = args.dst if args.dst else '../iiif'
    dst = os.path.join(base_dst, subfolder)
    sg = IIIFStatic(prefix=baseurl, dst=dst)
    sggenerate = sg.generate(file)
    iiiffulldir = os.path.join(dst, os.path.splitext(os.path.basename(file))[0], 'full/full')
    if not os.path.isdir(iiiffulldir):
        os.mkdir(iiiffulldir)
        iiiffulldir = os.path.join(iiiffulldir, '0')
        os.mkdir(iiiffulldir)
    else:
        iiiffulldir = os.path.join(iiiffulldir, '0')
    os.system('cp {} {}'.format(file, os.path.join(iiiffulldir, 'default.jpg')))
