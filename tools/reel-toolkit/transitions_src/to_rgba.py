import glob
from PIL import Image
n=0
for f in glob.glob('*/[0-9][0-9][0-9][0-9].png'):
    im=Image.open(f)
    if im.mode!='RGBA': im.convert('RGBA').save(f);n+=1
print('converted',n)
