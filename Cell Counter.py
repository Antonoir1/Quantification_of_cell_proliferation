# This Python file uses the following encoding: utf-8
import sys
import os
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg
import numpy as np

import time, random


#CLASS TO HANDLE THE IUTPUT PATH FIELD AND BROWSE BUTTON
class InputData(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        font = QtGui.QFont()
        font.setPointSize(10)
        open = QtWidgets.QPushButton("Browse")
        open.setFont(font)
        open.setFixedSize(80,35)
        label2 = QtWidgets.QLabel("Path:")
        font.setPointSize(14)
        label2.setFont(font)
        label2.setFixedWidth(60)
        font.setPointSize(10)
        self.label3 = QtWidgets.QLineEdit()
        self.label3.setFont(font)
        self.label3.setMinimumWidth(300)

        open.clicked.connect(self.open_new_dialog)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(label2)
        layout.addWidget(self.label3)
        layout.addWidget(open)
        self.setLayout(layout)

    #OPEN THE FILE EXPLORER AND MODIFY THE VALUE OF THE INPUT PATH FIELD
    def open_new_dialog(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(parent=self,caption='Select directory')
        self.label3.setText(str(path))
        self.repaint()

    #RETURN THE INPUT PATH FIELD
    def get_path(self):
        return str(self.label3.text())


#CLASS TO HANDLE THE POPULATION GRAPH
class PopulationCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_figure(self,X,Y):
        self.axes.cla()
        self.axes.plot(X, Y, 'r')
        self.draw()

class PopulationImage(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_figure(self,path):
        img = mpimg.imread(path)
        self.axes.cla()
        self.axes.imshow(img)
        self.draw()


#CLASS TO HANDLE THE WINDOW
class Window(QtWidgets.QWidget):
    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent)

        #TITLE
        Title = QtWidgets.QLabel("Cell Counter")
        Title.setAlignment(QtCore.Qt.AlignTop)
        font = QtGui.QFont()
        font.setPointSize(28)
        font.setBold(True)
        Title.setFont(font)
        font.setBold(False)

        #PROGRESS BUTTON
        font.setPointSize(16)
        process = QtWidgets.QPushButton("Process Data")
        process.setFont(font)
        process.clicked.connect(self.Process)

        #PROGRESS BAR
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setMinimumHeight(40)

        #QUIT BUTTON
        quit = QtWidgets.QPushButton("Quit")
        quit.setFont(font)
        self.connect(quit, QtCore.SIGNAL("clicked()"),
                             QtWidgets.qApp, QtCore.SLOT("quit()"))

        #LAYOUTS (GLOBAL LAYOUT, INPUT LAYOUT, OUTPUT LAYOUT)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(15,0,15,15)
        layoutin = QtWidgets.QVBoxLayout()
        layoutin.setContentsMargins(0,0,0,0)
        layoutin.setSpacing(0)
        layoutou = QtWidgets.QVBoxLayout()
        layoutou.setContentsMargins(0,0,0,0)
        layoutou.setSpacing(0)

        #INPUT WIDGETS
        self.ind = InputData()
        labelin = QtWidgets.QLabel("Input Folder:")
        labelin.setAlignment(QtCore.Qt.AlignBottom)
        labelin.setFont(font)
        labelin.setMinimumWidth(175)
        labelin.setMaximumWidth(175)
        labelin.setContentsMargins(0,50,0,15)

        #INPUT FORMAT
        labelpref = QtWidgets.QLabel("Images Prefix (ex: time => time01.tiff, time02.tiff...):")
        labelpref.setAlignment(QtCore.Qt.AlignBottom)
        font.setPointSize(12)
        labelpref.setFont(font)
        self.inputpref = QtWidgets.QLineEdit()
        self.inputpref.setFont(font)
        self.inputpref.setMinimumWidth(300)
        font.setPointSize(16)

        #GRAPH WIDGETS
        labelgraph = QtWidgets.QLabel("Cell population:")
        labelgraph.setAlignment(QtCore.Qt.AlignBottom)
        labelgraph.setFont(font)
        labelgraph.setMinimumWidth(175)
        labelgraph.setMaximumWidth(200)
        labelgraph.setContentsMargins(0,50,0,15)
        self.Graph = PopulationCanvas(self, width=5, height=4, dpi=100)
        self.Graph.setMinimumHeight(300)

        #GLOBAL VARIABLES FOR PROCESSING IMAGES
        self.imgs = []
        self.prefix = ""
        self.path = ""
        self.position = -1
        self.result = []
        self.X = []  #NUMBER OF THE IMAGE IN THE TIME (0,1,3...)
        self.Y = []  #NUMBER OF THE CELL POPULATION IN THE IMAGE

        #POPULATION IMAGE
        layoutimg = QtWidgets.QHBoxLayout()
        layoutimg.setContentsMargins(0,0,0,0)
        layoutimg.setSpacing(0)
        self.output_imgs = PopulationImage(self, width=5, height=4, dpi=100)
        self.output_imgs.setMinimumHeight(300)
        self.labelimg = QtWidgets.QLabel("Population image:")
        self.labelimg.setAlignment(QtCore.Qt.AlignBottom)
        self.labelimg.setFont(font)
        self.labelimg.setMinimumWidth(175)
        self.labelimg.setContentsMargins(0,50,0,15)
        font.setPointSize(12)
        nextbutton = QtWidgets.QPushButton("Next")
        nextbutton.setFont(font)
        nextbutton.clicked.connect(self.Next)
        backbutton = QtWidgets.QPushButton("Back")
        backbutton.setFont(font)
        backbutton.clicked.connect(self.Back)
        layoutimg.addWidget(backbutton)
        layoutimg.addWidget(self.output_imgs)
        layoutimg.addWidget(nextbutton)

        #SET THE LAYOUTS (GLOBAL LAYOUT, INPUT LAYOUT, OUTPUT LAYOUT)
        self.layout.addWidget(Title)
        layoutin.addWidget(labelin)
        layoutin.addWidget(self.ind)
        self.layout.addLayout(layoutin)
        self.layout.addWidget(labelpref)
        self.layout.addWidget(self.inputpref)
        self.layout.addWidget(process)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(labelgraph)
        self.layout.addWidget(self.Graph)
        self.layout.addWidget(self.labelimg)
        self.layout.addLayout(layoutimg)
        self.layout.addWidget(quit)

        #SCROLLING BAR WIDGETS
        Container = QtWidgets.QWidget()
        Container.setLayout(self.layout)
        Scroll = QtWidgets.QScrollArea()
        Scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        Scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        Scroll.setWidgetResizable(True)
        Scroll.setMinimumSize(600,600)
        Scroll.setWidget(Container)

        #SCROLLING BAR LAYOUT
        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.addWidget(Scroll)
        self.setLayout(vlayout)

    #GO TO THE NEXT IMAGE
    def Next(self):
        if(len(self.result)):
            if(self.position < (len(self.result)-1)):
                self.position += 1
                self.output_imgs.update_figure(self.path+"/"+self.result[self.position])

    #GO BACK TO THE LAST IMAGE
    def Back(self):
        if(self.position > 0):
                self.position -= 1
                self.output_imgs.update_figure(self.path+"/"+self.result[self.position])

    #CHECK THE PATHS OF THE INPUT/PREFIX FIELD AND LAUNCH THE PROCESS OF COUNTING
    def Process(self):
        if(self.ind.get_path() == "" or os.path.exists(self.ind.get_path()) == False or str(self.inputpref.text()) == "" ):
            msg = QtWidgets.QMessageBox()
            msg.setText( u"ERROR:\nNo folder was selected for input data and/or no prefix was entred" )
            msg.exec()
        else:
            files = os.listdir(self.ind.get_path())
            if len(files) == 0:
                msg = QtWidgets.QMessageBox()
                msg.setText( u"ERROR:\nNo image .tif/.tiff found in the input folder" )
                msg.exec()
            else:
                have_images = False
                have_prefix = True
                imgs = []
                for i in range(0,len(files)):
                    if(len(files[i]) > 4 ):
                        if(files[i][len(files[i])-3:len(files[i])] == "tif"):
                            have_images = True
                            imgs.append(files[i])
                            if(str(self.inputpref.text()) not in files[i]):
                                have_prefix = False
                    if(len(files[i]) > 5):
                        if(files[i][len(files[i])-4:len(files[i])] == "tiff"):
                            have_images = True
                            imgs.append(files[i])
                            if(str(self.inputpref.text()) not in files[i]):
                                have_prefix = False
                if(have_images == False or have_prefix == False):
                    msg = QtWidgets.QMessageBox()
                    msg.setText( u"ERROR:\nNo image .tif/.tiff found in the input folder and/or the prefix value is uncorrect" )
                    msg.exec()
                else:
                    unordered = []
                    ordering = []
                    w = 0
                    for i in imgs:
                        if(".tiff" in i):
                            #TODO TRY EXCEPT
                            unordered.append(int(i[len(str(self.inputpref.text())):len(i)-5]))
                            ordering.append([int(i[len(str(self.inputpref.text())):len(i)-5]), i])
                        else:
                            unordered.append(int(i[len(str(self.inputpref.text())):len(i)-4]))
                            ordering.append([int(i[len(str(self.inputpref.text())):len(i)-4]), i])
                        w += 1
                    unordered.sort()

                    self.imgs = []
                    for i in range(0,len(unordered)):
                        k = 0
                        #TODO RAJOUTER UNE SECURITE
                        while(unordered[i] != ordering[k][0]):
                            k += 1
                        self.imgs.append(ordering[k][1])
                    work = 0
                    self.X = []
                    self.Y = []
                    self.result = []

                    for i in range(0,len(self.imgs)):
                        time.sleep(0.005) #TODO METTRE LE CODE D'ANALYSE ICI
                        self.result.append(self.imgs[i])

                        self.X.append(i)
                        self.Y.append(i+random.randint(0,25))
                        work += (1/(len(imgs)-1))*100
                        self.progress.setValue(work)
                        
                    self.Graph.update_figure(self.X,self.Y)
                    self.output_imgs.update_figure(self.ind.get_path()+"/"+self.result[0])
                    self.position = 0
                    self.path = self.ind.get_path()
                    self.prefix = str(self.inputpref.text())
                        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
