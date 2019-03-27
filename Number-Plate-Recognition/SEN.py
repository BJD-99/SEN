import Main
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

filename = "/home/practice/Number-Plate-Recognition/a4.jpg"

class QExampleLabel (QLabel):
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
        Main.running('output.jpg')

class Task(QMainWindow):

    def __init__(self):
        super(QMainWindow,self).__init__()
        self.title = "Demo"
        self.width = 1280
        self.height = 720
        self.top = 0
        self.left = 0

        vbox = QVBoxLayout()

        frame_1 = QFrame(self)
        frame_1.setLineWidth(1)
        frame_1.setFrameStyle(QFrame.StyledPanel)
        frame_1.resize(200, 720)

        frame_2 = QFrame(self)
        frame_2.setLineWidth(1)
        frame_2.move(201, 0)
        frame_2.resize(1200, 720)
        frame_2.setFrameStyle(QFrame.StyledPanel)


        vbox.addWidget(frame_1)
        vbox.addWidget(frame_2)

        self.setLayout(vbox)

        abc=QExampleLabel(frame_2)

        line_edit_1=QLineEdit(frame_1)
        line_edit_1.move(0,100)

        line_edit_2=QLineEdit(frame_1)
        line_edit_2.move(0,150)
        line_edit_3=QLineEdit(frame_1)
        line_edit_3.move(0,200)

        line_edit_4=QLineEdit(frame_1)
        line_edit_4.move(0,20)


        self.initUI()



    def initUI(self):

        self.setWindowTitle(self.title)
        self.setAcceptDrops(True)
        #self.setFixedSize(self.width, self.height)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def closeEvent(self):
        exit()


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