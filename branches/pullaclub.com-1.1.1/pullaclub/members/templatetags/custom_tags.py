import os
import re
import Image
from django import template


register = template.Library()

lire = re.compile('\n\s*(-|\*)(?P<line>.+)')
culre = re.compile('</li>(?!<li>)\s*')
oulre = re.compile('\s*(?<!</li>)<li>')
qre = re.compile('[^=](?P<quote>"[^"]+")($|\s+|,)')

@register.filter
def tags(text):
    text = lire.sub('<li>\g<line></li>',text) # wrap bulleted lines with <li>
    text = culre.sub('</li></ul>',text) # append closing </ul>
    text = oulre.sub('<ul><li>',text) # prepend opening <ul>
    text = qre.sub('<i> \g<quote> </i>',text) # wrap quotes with <i>
    return text.replace('\n','<br/>')  # nl to html line breaks

@register.filter
def times(count):
    return range(int(count))

def __parse_geometry(image,size):

    m = re.match('([0-9]+)x([0-9]+)',size)
    if m: # exact size
        return (int(m.group(1)),int(m.group(2)))
        
    m = re.match('([0-9]+)w',size)
    if m: #  width
        return (int(m.group(1)),image.height)

    m = re.match('([0-9]+)h',size)
    if m: #  height
        return (image.width,int(m.group(1)))

    m = re.match('([0-9]+)',size)
    if m: # maximum dimension
        return (int(m.group(0)),int(m.group(0)))

    raise Exception('invalid geometry "%s"' % size)


@register.filter
def downscale(image, size="70"):

    # figure out how to scale the message
    (x,y) = __parse_geometry(image,size)
    if x >= image.width and y >= image.height:
        return image.url

    # defining the filename and the scaled filename
    filehead, filetail = os.path.split(image.path)
    basename, format = os.path.splitext(filetail)
    scaled = basename + '_scale' + size + format
    filename = image.path
    scaled_filename = os.path.join(filehead,scaled)
    filehead, filetail = os.path.split(image.url)
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
