import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import psycopg2
from PIL import Image
import sys
from PyQt5.QtWidgets import (QPushButton, QWidget,QLineEdit, QApplication)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2
import numpy as np
import os
import time
import DetectChars
import DetectPlates
import PossiblePlate

str12="null"

filename = "/home/practice/Number-Plate-Recognition/a4.jpg"

SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False

def main(image):

    CnnClassifier = DetectChars.loadCNNClassifier()         # attempt KNN training
    #response  = str(input('Do you want to see the Intermediate images: '))
    """
    if response == 'Y' or response == 'y':
        showSteps = True
    else:
        showSteps = False

    """

    if CnnClassifier == False:                               # if KNN training was not successful
        print("\nerror: CNN traning was not successful\n")               # show error message
        return                                                          # and exit program

    imgOriginalScene  = cv2.imread(image)               # open image
    h, w = imgOriginalScene.shape[:2]
    # As the image may be blurr so we sharpen the image.
    #kernel_shapening4 = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
    #imgOriginalScene = cv2.filter2D(imgOriginalScene,-1,kernel_shapening4)
    
    #imgOriginalScene = cv2.resize(imgOriginalScene,(1000,600),interpolation = cv2.INTER_LINEAR)
    
    imgOriginalScene = cv2.resize(imgOriginalScene, (0, 0), fx = 1.4, fy = 1.4,interpolation=cv2.INTER_LINEAR)
    
    #imgOriginalScene = cv2.fastNlMeansDenoisingColored(imgOriginalScene,None,10,10,7,21)
    
    #imgOriginal = imgOriginalScene.copy()
    
    if imgOriginalScene is None:                            # if image was not read successfully
        print("\nerror: image not read from file \n\n")      # print error message to std out
        os.system("pause")                                  # pause so user can see error message
        return                                              # and exit program

    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates. We get a list of
			
    
                                                                                        # combinations of contours that may be a plate.


    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates

    if showSteps == True:
        cv2.imshow("imgOriginalScene", imgOriginalScene)            # show scene image
    
    if len(listOfPossiblePlates) == 0:                          # if no plates were found
        print("\nno license plates were detected\n")             # inform user no plates were found
        response = ' '
        return response,imgOriginalScene
    else:                                                       # else
                # if we get in here list of possible plates has at leat one plate

                # sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)

        
        # suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate
        
        #    licPlate = listOfPossiblePlates[index]

        s1 = 'Not'
        s2 = 'Detected'

        dummy=len(listOfPossiblePlates)
        count=0
        while(count<dummy):
            licPlate=listOfPossiblePlates[count]
            print("\nlicense plate read from ", image," :",licPlate.strChars,"\n")
            if(count==0):
                s1=licPlate.strChars
            if(count==1):
                s2=licPlate.strChars
            count=count+1
        
        if(dummy==1):
            global str12
            str12 = s1

        if(dummy==2):
            global str12
            str12 = s2 + s1

        if showSteps == True:
            cv2.imshow("imgPlate", licPlate.imgPlate)           # show crop of plate and threshold of plate
            cv2.waitKey(0)
        if len(licPlate.strChars) == 0:                     # if no chars were found in the plate
            print("\nno characters were detected\n\n")       # show message
            return ' ',imgOriginalScene                                       # and exit program
        # end if

        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)             # draw red rectangle around plate

        #print("\nlicense plate read from ", image," :",licPlate.strChars,"\n")
        #print("----------------------------------------")

        if showSteps == True:
            writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)           # write license plate text on the image

            cv2.imshow("imgOriginalScene", imgOriginalScene)                # re-show scene image

            cv2.imwrite("imgOriginalScene.png", imgOriginalScene)           # write image out to file
            cv2.waitKey(0)                    # hold windows open until user presses a key

    return licPlate.strChars,licPlate.imgPlate
###################################################################################################
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect. Here, bounding rectangle is drawn with minimum area, so it considers the rotation also

    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)         # draw 4 red lines
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)
# end function

###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             # this will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      # choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0                    # base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize

            # unpack roatated rect into center point, width and height, and angle
    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):                                                  # if the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      # write the chars in below the plate
    else:                                                                                       # else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      # write the chars in above the plate
    # end if

    textSizeWidth, textSizeHeight = textSize                # unpack text size width and height

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           # calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          # based on the text area center, width, and height

            # write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)
# end function

###################################################################################################

def running(str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(str)
   # main(dir_path + '/Test_images/538E945.jpg')
   # main(dir_path + '/Test_images/BKF196.jpg')
   # main(dir_path + '/Test_images/489T051.jpg')
    main(str)




class QExampleLabel (QLabel):

    got_password = QtCore.pyqtSignal(str)

    def __init__(self, parentQWidget = None):
        super(QExampleLabel, self).__init__(parentQWidget)
        self.setAcceptDrops(True)
        #self.setScaledContents(True)
        #self.setDragEnabled(True)
        #self.resize(10000,10000)
        self.setAlignment(Qt.AlignCenter)
        self.initUI()

    def initUI (self):
        print("SETED")
        print(filename)
        self.setPixmap(QtGui.QPixmap(filename))

    def dragEnterEvent(self, e):
      print e
      e.acceptProposedAction()
      #if e.mimeData().hasImage():
       #  e.accept()
      #else:
       #  e.ignore()
			
    def dropEvent(self, e):
      m = e.mimeData()
      #self.setScaledContents(True)
      self.clear()
      filename = m.urls()[0].toLocalFile()
      im = Image.open(filename)
      width, height = im.size
      self.resize(width,height) 
      self.setPixmap(QPixmap(filename)) 
      QApplication.processEvents()
      QApplication.processEvents()
      QApplication.processEvents()
      QApplication.processEvents()

    def mousePressEvent (self, eventQMouseEvent):
        self.originQPoint = eventQMouseEvent.pos()
        self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, QtCore.QSize()))
        self.currentQRubberBand.show()

    def mouseMoveEvent (self, eventQMouseEvent):
        self.currentQRubberBand.setGeometry(QtCore.QRect(self.originQPoint, eventQMouseEvent.pos()).normalized())

    def mouseReleaseEvent (self, eventQMouseEvent):
        self.currentQRubberBand.hide()
        currentQRect = self.currentQRubberBand.geometry()
        self.currentQRubberBand.deleteLater()
        cropQPixmap = self.pixmap().copy(currentQRect)
        cropQPixmap.save('output.jpg')
        running('output.jpg')
        self.got_password.emit(str12)

class Task(QMainWindow):

    def __init__(self):
        super(QMainWindow,self).__init__()
        self.title = "Demo"
        self.width = 1280
        self.height = 720
        self.top = 0
        self.left = 0

        vbox = QVBoxLayout()
        self.count=0

        frame_1 = QFrame(self)
        frame_1.setLineWidth(1)
        frame_1.setFrameStyle(QFrame.StyledPanel)
        frame_1.resize(200, 720)

        frame_2 = QFrame(self)
        frame_2.setLineWidth(1)
        frame_2.move(201, 0)
        frame_2.resize(1200, 720)
        frame_2.setFrameStyle(QFrame.StyledPanel)

        self.l1 = []
        self.email= []

        vbox.addWidget(frame_1)
        vbox.addWidget(frame_2)

        self.setLayout(vbox)

        abc=QExampleLabel(frame_2)

        abc.got_password.connect(self.show_it)

        self.line_edit_1=QLineEdit(frame_1)
        self.line_edit_1.move(0,100)
        
        self.line_edit_2=QLineEdit(frame_1)
        self.line_edit_2.move(0,150)

        self.line_edit_3=QLineEdit(frame_1)
        self.line_edit_3.move(0,200)

        self.line_edit_4=QLineEdit(frame_1)
        self.line_edit_4.move(0,250)


        self.initUI()



    def initUI(self):

        self.setWindowTitle(self.title)
        self.setAcceptDrops(True)
        #self.setFixedSize(self.width, self.height)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def closeEvent():
        exit()

    def show_it(self, the_password):
        for x in range(4):
            if(self.line_edit_1.text()==''):
                self.line_edit_1.setText(the_password)
                self.count = self.count + 1
                break
            if(self.line_edit_2.text()==''):
                self.line_edit_2.setText(the_password)
                self.count = self.count + 1
                break
            if(self.line_edit_3.text()==''):
                self.line_edit_3.setText(the_password)
                self.count = self.count + 1
                break
            if(self.line_edit_4.text()==''):
                self.line_edit_4.setText(the_password)
                self.count = self.count + 1
                break


class App(QWidget):

    def __init__(self):
        super(QWidget,self).__init__()
        self.title = 'LOG IN'
        self.left = 100
        self.top = 100
        self.width = 600
        self.height = 300

        
        self.label_1 = QLabel(self)
        self.label_1.move(100, 100)
        self.label_1.setText("Username")

        self.label_2 = QLabel(self)
        self.label_2.move(100, 150)
        self.label_2.setText("Password")

        self.lineedit_1=QLineEdit(self)
        self.lineedit_1.move(200, 100)
        self.lineedit_1.resize(200,20)

        self.lineedit_2 = QLineEdit(self)
        self.lineedit_2.resize(200,20)
        self.lineedit_2.setEchoMode(QLineEdit.Password)
        self.lineedit_2.move(200, 150)

        self.button=QPushButton(self)
        self.button.move(220, 210)
        self.button.setText("Login")
        self.button.clicked.connect(self.checking)
        self.button.resize(100,30)
        self.initUI()

    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Return:
            self.checking()
        elif e.key() == QtCore.Qt.Key_Enter:
            print (' enter')

    def initUI(self):
        self.setWindowTitle(self.title)

        self.setFixedSize(self.width, self.height)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def checking(self):

        conn = psycopg2.connect(database="postgres", user="user_1", password="mynewpassword", host="127.0.0.1", port="5432")
        print ("Opened database successfully")
        cur = conn.cursor()

        cur.execute("select count(*) from police where username= %s and password=%s", (self.lineedit_1.text(),self.lineedit_2.text()))
        rows = cur.fetchall()

        print(rows[0][0])
        if(rows[0][0] == 1):
            print("Success")
            self.destroy()
            w_1.setVisible(True)
        else:
            QMessageBox.about(self,"Login Failed"," Username / Password is not valid")




app = QApplication(sys.argv)
ex = App()
w_1 = Task()
w_1.setVisible(False)
sys.exit(app.exec_())