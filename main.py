# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow

import sys, os, numpy
import math
#import matplotlib.pyplot as plt

try: # Pillow
    from PIL import Image
except:
    print 'Error: Pillow has not been installed.'
    sys.exit(0)

try: # PyOpenGL
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print 'Error: PyOpenGL has not been installed.'
    sys.exit(0)

# Constants
maxIntensity = 235
intensities = 256
# Globals

windowWidth  = 600 # window dimensions
windowHeight =  600

factor = 1 # factor by which luminance is scaled
term = 0 # term by which luminance is transformed

#filter variables
scaleFactor = 0
myFilter = []

# Image directory and path to image file

imgDir = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join(imgDir, imgFilename)

filterDir = 'filters'
filterFilename = 'gaussian7x'

filterPath = os.path.join(filterDir, filterFilename)

currentImage = Image.open(imgPath).convert( 'YCbCr' )
temporaryImage = Image.open(imgPath).convert( 'YCbCr' )

filterRadius = 15

buildTemporaryImageFlag = False

# File dialog

import Tkinter, tkFileDialog

root = Tkinter.Tk()
root.withdraw()

# Build appropriate (temporary or current) image.

def buildImage():

  # Read image

  print imgPath
  if (buildTemporaryImageFlag) :
    src = temporaryImage
  else :
    src = currentImage
    
  srcPixels = src.load()

  width  = src.size[0]
  height = src.size[1]

  # Set up a new, blank image of the same size

  dst = Image.new( 'YCbCr', (width,height) )
  dstPixels = dst.load()

  # Build destination image from source image

  for i in range(width):
    for j in range(height):
      
      dstPixels[i,height-j-1] = srcPixels[i,j];

  # Done

  return dst.convert( 'RGB' )

# Copy temporary image to current image

def copyTemporaryImageToCurrentImage():

  global currentImage
  
  if(currentImage.size[0] != temporaryImage.size[0] or currentImage.size[1] != temporaryImage.size[1]):
    print 'Image dimensions to do not match!'
    return
    
  width  = currentImage.size[0]
  height = currentImage.size[1]  
  tmpPixels = temporaryImage.load()
  crtPixels = currentImage.load()
  
  for i in range(width):
    for j in range(height):

      # read pixel in temporary image
  
      crtPixels[i,j] = tmpPixels[i,j]

  # Done

# Modify the current image and write to temporary image

def modifyBrightnessAndContrastOfTemporaryImage():

  print imgPath
  global temporaryImage
  
  if(currentImage.size[0] != temporaryImage.size[0] or currentImage.size[1] != temporaryImage.size[1]):
    print 'Image dimensions to do not match!'
    return
    
  # Read image and convert to YCbCr
    
  src = currentImage
  srcPixels = src.load()
  temporaryImage = temporaryImage
  dstPixels = temporaryImage.load()

  width  = src.size[0]
  height = src.size[1]

  # Build destination image from source image

  for i in range(width):
    for j in range(height):

      # read source pixel
      
      y,cb,cr = srcPixels[i,j]

      # ---- MODIFY PIXEL ----

      y = int(factor * y + term)
      
      # write destination pixel
      
      dstPixels[i,j] = (y,cb,cr)

  # Done

  print 'modifying temporary image'
  #temporaryImage = temporaryImage.convert( 'RGB' )

def buildCurrentImageWithHistogramEqualization():
    #Read image and convert to YCbCr
    print imgPath
    global temporaryImage
    if(currentImage.size[0] != temporaryImage.size[0] or currentImage.size[1] != temporaryImage.size[1]):
        print 'Image dimensions do not match..'
        return
    srcImg = currentImage
    srcImgPixels = srcImg.load()
    temporaryImage = temporaryImage
    dstImgPixels = temporaryImage.load()

    width = srcImg.size[0]
    height = srcImg.size[1]

    #create the histogram array
    histArray = numpy.zeros(intensities)

    for i in range(width):
        for j in range(height):
            #get source pixel
            y, cb, cr = srcImgPixels[i,j]
            #add 1 to its intensity bin
            histArray[y] += 1

    #normalize the histogram array
    normHistArray = histArray/(width*height)
    #get our cumulative sum density function
    cumSumArr = numpy.array(cumSum(normHistArray))
    #create the look up table by multiplying by (256-1)
    lookUpTable = numpy.round(cumSumArr*(intensities - 1))
    #plt.figure(1)
    #plt.bar(numpy.arange(len(normHistArray)), normHistArray)
    #print len(lookUpTable)

    # create new histogram array for visualization
    newHistArray = numpy.zeros(intensities)
    #create new picture
    for i in range(width):
        for j in range(height):
            #get source pixel
            y, cb, cr = srcImgPixels[i,j]
            #change using look up table
            y = int(lookUpTable[y])
            #add to new histogram array
            newHistArray[y] += 1
            #add to destination pixels
            dstImgPixels[i,j] = (y, cb, cr)

    # normalize the histogram array
    normNewHistArray = newHistArray / (width * height)
    #plt.figure(2)
    #plt.bar(numpy.arange(len(normNewHistArray)), normNewHistArray)
    #plt.show()
    #temporaryImage = temporaryImage.convert('RGB')
    copyTemporaryImageToCurrentImage()

def cumSum(array):
    # finds cumulative sum of a numpy array, list
    return [sum(array[:i+1]) for i in range(len(array))]

def loadFilter( path ):
    global scaleFactor, myFilter, filterPath
    
    filterPath = path
    filter = open( filterPath )
    ##dimensions = filter.readline()
    xDim, yDim = [int(s) for s in filter.readline() if s.isdigit()]
    scaleFactor = float(filter.readline())
    myFilter = numpy.zeros((yDim, xDim))
    for i in range(yDim):
         myFilter[i] = [int(s) for s in filter.readline() if s.isdigit()]
    print('Loaded: ' + path)
    print(scaleFactor)
    print(myFilter)

def buildCurrentImageWithFilter():
    global temporaryImage

    if (currentImage.size[0] != temporaryImage.size[0] or currentImage.size[1] != temporaryImage.size[1]):
        print 'Image dimensions do not match..'
        return

    srcImg = currentImage
    srcImgPixels = srcImg.load()
    temporaryImage = temporaryImage
    dstImgPixels = temporaryImage.load()

    width = srcImg.size[0]
    height = srcImg.size[1]

    #tempFilter = numpy.flip(myFilter, 2)
    #apply convolution for all image
    xFilterDim = len(myFilter[0])
    yFilterDim = len(myFilter)
    xFilterCenter = int(math.floor(xFilterDim/2))
    yFilterCenter = int(math.floor(yFilterDim/2))

    for m in range(width):
        for n in range(height):
            result = 0
            y_pixel, cb_pixel, cr_pixel = srcImgPixels[m,n]

            for i in range(yFilterDim):
                yFilterIndex = yFilterDim - 1 - i
                for j in range(xFilterDim):
                    xFilterIndex = xFilterDim - 1 - j
                    pixelYIndex = n + (i - yFilterCenter)
                    pixelXIndex = m + (j - xFilterCenter)
                    if(pixelXIndex >= 0 and pixelXIndex < width and pixelYIndex >= 0 and pixelYIndex < height):
                        y_new, cb, cr = srcImgPixels[pixelXIndex, pixelYIndex]
                        result += y_new*myFilter[yFilterIndex, xFilterIndex]*scaleFactor

            dstImgPixels[m, n] = (result, cb_pixel, cr_pixel)

    #temporaryImage = temporaryImage.convert('RGB')
    copyTemporaryImageToCurrentImage()
    
    

def buildCurrentImageWithFilterRadiusR( x, y ):

    global temporaryImage, currentImage
    

    if (currentImage.size[0] != temporaryImage.size[0] or currentImage.size[1] != temporaryImage.size[1]):
        print 'Image dimensions do not match..'
        return

    srcImg = currentImage
    srcImgPixels = srcImg.load()
    temporaryImage = temporaryImage
    dstImgPixels = temporaryImage.load()

    width = srcImg.size[0]
    height = srcImg.size[1]   

    #tempFilter = numpy.flip(myFilter, 2)
    #apply convolution for all image
    xFilterDim = len(myFilter[0])
    yFilterDim = len(myFilter)
    xFilterCenter = int(math.floor(xFilterDim/2))
    yFilterCenter = int(math.floor(yFilterDim/2))
    
    imgX = x - (windowWidth - width)/2
    imgY = y - (windowHeight - height)/2
    
    #print 'y dim %d, x dim %d' %(yFilterDim, xFilterDim)

    for m in range(imgX - filterRadius, imgX + filterRadius):
        for n in range(imgY - filterRadius, imgY + filterRadius):
            #print ('%d %d' %(m,n))
            if( (m - imgX)**2 + (n - imgY)**2 <= filterRadius**2):
                result = 0
                if(m >= 0 and m < width and n >= 0 and n < height):
                    y_pixel, cb_pixel, cr_pixel = srcImgPixels[m,n]

                    for i in range(yFilterDim):
                        yFilterIndex = yFilterDim - 1 - i
                        for j in range(xFilterDim):
                            xFilterIndex = xFilterDim - 1 - j
                            pixelYIndex = n + (i - yFilterCenter)
                            pixelXIndex = m + (j - xFilterCenter)
                            if(pixelXIndex >= 0 and pixelXIndex < width and pixelYIndex >= 0 and pixelYIndex < height):
                                y_new, cb, cr = srcImgPixels[pixelXIndex, pixelYIndex]
                                result += y_new*myFilter[yFilterIndex, xFilterIndex]*scaleFactor

                    dstImgPixels[m, n] = (result, cb_pixel, cr_pixel)

    #temporaryImage = temporaryImage.convert('RGB')
    copyTemporaryImageToCurrentImage()    

    

# Set up the display and draw the current image

def display():

    # Clear window

    glClearColor ( 1, 1, 1, 0 )
    glClear( GL_COLOR_BUFFER_BIT )

    # get the output image

    img = buildImage()

    width  = img.size[0]
    height = img.size[1]

    # Find where to position lower-left corner of image

    baseX = (windowWidth-width)/2
    baseY = (windowHeight-height)/2

    glWindowPos2i( baseX, baseY )

    # Get pixels and draw

    imageData = numpy.array( list( img.getdata() ), numpy.uint8 )

    glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

    glutSwapBuffers()

def changeFilterRadiusBy( dR ) :
    global filterRadius
    filterRadius = filterRadius + dR

# Handle keyboard input

def keyboard( key, x, y ):

    if key == '\033': # ESC = exit
        sys.exit(0)

    elif key == 'l':
        path = tkFileDialog.askopenfilename( initialdir = imgDir )
        if path:
            loadImage( path )

    elif key == 's':
        outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
        if outputPath:
            saveImage( outputPath )

    elif key == 'h':
        buildCurrentImageWithHistogramEqualization()

    elif key == 'f':
        path = tkFileDialog.askopenfilename( initialdir = filterDir )
        if path:
          loadFilter( path )

    elif key == 'a':
        buildCurrentImageWithFilter()       
        
    elif key == '+' or key == '=':
        changeFilterRadiusBy(1)
        print 'filter radius %d' %filterRadius
       
    elif key == '-' or key == '_':
        changeFilterRadiusBy(-1)
        print 'filter radius %d' %filterRadius
        
    else:
        print 'key =', key    # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

    glutPostRedisplay()

    

# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.

def loadImage( path ):

    global imgPath, currentImage, temporaryImage

    imgPath = path
    currentImage = Image.open(imgPath).convert( 'YCbCr' )
    width = currentImage.size[0]
    height = currentImage.size[1]
    temporaryImage = Image.open(imgPath).convert( 'YCbCr' )
    
    #print imgPath

def saveImage( path ):

    currentImage.save( path )



# Handle window reshape

def reshape( newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth  = newWidth
    windowHeight = newHeight

    glutPostRedisplay()



# Mouse state on initial click

button = None
initX = 0
initY = 0
initFactor = 1
initTerm = 0



# Handle mouse click/unclick

def mouse( btn, state, x, y ):

    global button, initX, initY, initFactor, buildTemporaryImageFlag

    if state == GLUT_DOWN:
        button = btn
        initX = x
        initY = y
        if(button == GLUT_LEFT_BUTTON):
          buildTemporaryImageFlag = True

    elif state == GLUT_UP:

        if(button == GLUT_LEFT_BUTTON):
          copyTemporaryImageToCurrentImage()
          buildTemporaryImageFlag = False
        button = None     


# Handle mouse motion

def motion( x, y ):

    diffX = x - initX
    diffY = y - initY

    global factor, term

    if (button == GLUT_LEFT_BUTTON) :
      factor = initFactor - diffY / float(windowHeight)
      term = initTerm + diffX / float(windowWidth) *  maxIntensity
      #print "initFactor => %f  diffY => %f  height => %f  factor => %f  term => %f" %(initFactor, diffY, windowHeight, factor, term)

      if factor < 0:
        factor = 0

      modifyBrightnessAndContrastOfTemporaryImage()
      
    elif (button == GLUT_RIGHT_BUTTON) :
        #print 'apply radius filter R = %d x,y = %d,%d' %(filterRadius, x,y)
        buildCurrentImageWithFilterRadiusR(x,y)
        
    glutPostRedisplay()



# Run OpenGL
loadImage(imgPath)
loadFilter (filterPath) 

glutInit()
glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
glutInitWindowSize( windowWidth, windowHeight )
glutInitWindowPosition( 50, 50 )

glutCreateWindow( 'imaging' )

glutDisplayFunc( display )
glutKeyboardFunc( keyboard )
glutReshapeFunc( reshape )
glutMouseFunc( mouse )
glutMotionFunc( motion )

glutMainLoop()
