import os
import re
import Image
from django import template


register = template.Library()

@register.filter
def br(text):
    text = re.sub('\n\s*(-|\*)(?P<line>.+)','<li>\g<line></li>',text) 
    text = re.sub('</li>(?!<li>)\n*','</li></ul>',text)
    text = re.sub('\n*(?<!</li>)<li>','<ul><li>',text)
    return text.replace('\n','<br/>')

@register.filter
def times(count):
    return range(int(count))

@register.filter
def thumbnail(file, size='70x70'):
    # defining the size
    x, y = [int(x) for x in size.split('x')]
    # defining the filename and the miniature filename
    filehead, filetail = os.path.split(file.path)
    basename, format = os.path.splitext(filetail)
    miniature = basename + '_thumb' + size + format
    filename = file.path
    miniature_filename = os.path.join(filehead,miniature)
    filehead, filetail = os.path.split(file.url)
    miniature_url = filehead + '/' + miniature
    if os.path.exists(miniature_filename) and os.path.getmtime(filename)>os.path.getmtime(miniature_filename):
        os.unlink(miniature_filename)
    # if the image wasn't already resized, resize it
    if not os.path.exists(miniature_filename):
        image = Image.open(filename)
        image.thumbnail([x, y], Image.ANTIALIAS)
        try:
            image.save(miniature_filename, image.format, quality=90, optimize=1)
        except:
            image.save(miniature_filename, image.format, quality=90)

    return miniature_url

@register.filter
def scaleh(file, size="300"):

    y = int(size)
    if y >= file.height: # no need to scale
        return file.url

    x = int(file.width*file.height/float(y))

    # defining the filename and the scaled filename
    filehead, filetail = os.path.split(file.path)
    basename, format = os.path.splitext(filetail)
    scaled = basename + '_scaledh' + size + format
    filename = file.path
    scaled_filename = os.path.join(filehead,scaled)
    filehead, filetail = os.path.split(file.url)
    scaled_url = filehead + '/' + scaled
    if os.path.exists(scaled_filename) and os.path.getmtime(filename)>os.path.getmtime(scaled_filename):
        os.unlink(scaled_filename)
    # if the image wasn't already resized, resize it
    if not os.path.exists(scaled_filename):
        image = Image.open(filename)
        image.thumbnail([x, y], Image.ANTIALIAS)
        try:
            image.save(scaled_filename, image.format, quality=90, optimize=1)
        except:
            image.save(scaled_filename, image.format, quality=90)

    return scaled_url


@register.filter
def scale2(file, size="70"):

    # figure out how to scale the message
    m = int(size)
    if file.height <= m:
        if file.width <= m: # no need to scale
            return file.url
        else:
            x = m
            y = int(file.height*file.width/float(x))
    elif file.width <= m:
        y = m
        x = int(file.width*file.height/float(y))
    elif file.width > file.height:
        x = m
        y = int(file.height*file.width/float(x))
    else:
        y = m
        x = int(file.width*file.height/float(y))


    # defining the filename and the scaled filename
    filehead, filetail = os.path.split(file.path)
    basename, format = os.path.splitext(filetail)
    scaled = basename + '_scale' + size + format
    filename = file.path
    scaled_filename = os.path.join(filehead,scaled)
    filehead, filetail = os.path.split(file.url)
    scaled_url = filehead + '/' + scaled
    if os.path.exists(scaled_filename) and os.path.getmtime(filename)>os.path.getmtime(scaled_filename):
        os.unlink(scaled_filename)
    # if the image wasn't already resized, resize it
    if not os.path.exists(scaled_filename):
        image = Image.open(filename)
        image.thumbnail([x, y], Image.ANTIALIAS)
        try:
            image.save(scaled_filename, image.format, quality=90, optimize=1)
        except:
            image.save(scaled_filename, image.format, quality=90)

    return scaled_url
