# This Python file uses the following encoding: utf-8
import sys
import os
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtCore, QtGui, QtWidgets
import time, random

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#Class to handle the Output path field and browse button
class OutputData(QtWidgets.QWidget):
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

    #Open the file explorer and modify the value of the Output path field
    def open_new_dialog(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(parent=self,caption='Select directory containing SunVox app')
        self.label3.setText(str(path))
        self.repaint()

    #Return the path in the Output path field
    def get_path(self):
        return str(self.label3.text())

#Class to handle the Iutput path field and browse button
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

    #Open the file explorer and modify the value of the Input path field
    def open_new_dialog(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(parent=self,caption='Select directory')
        self.label3.setText(str(path))
        self.repaint()

    #Return the path in the Input path field
    def get_path(self):
        return str(self.label3.text())


#Class to handle the population Graph
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



#Class to handle the Window
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
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(15,0,15,15)
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

        #OUTPUT WIDGETS
        self.oud = OutputData()
        labelou = QtWidgets.QLabel("Output Folder:")
        labelou.setAlignment(QtCore.Qt.AlignBottom)
        labelou.setFont(font)
        labelou.setMinimumWidth(175)
        labelou.setMaximumWidth(175)
        labelou.setContentsMargins(0,50,0,15)

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
        self.X = []  #NUMBER OF THE IMAGE IN THE TIME (0,1,3...)
        self.Y = []  #NUMBER OF THE CELL POPULATION IN THE IMAGE

        #SET THE LAYOUTS (GLOBAL LAYOUT, INPUT LAYOUT, OUTPUT LAYOUT)
        layout.addWidget(Title)
        layoutin.addWidget(labelin)
        layoutin.addWidget(self.ind)
        layout.addLayout(layoutin)
        layoutou.addWidget(labelou)
        layoutou.addWidget(self.oud)
        layout.addLayout(layoutou)
        layout.addWidget(process)
        layout.addWidget(self.progress)
        layout.addWidget(labelgraph)
        layout.addWidget(self.Graph)
        layout.addWidget(quit)

        #SCROLLING BAR WIDGETS
        Container = QtWidgets.QWidget()
        Container.setLayout(layout)
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

    #Check the paths of the input and output field and launch the process of counting
    def Process(self):
        if(self.ind.get_path() == "" or os.path.exists(self.ind.get_path()) == False):
            msg = QtWidgets.QMessageBox()
            msg.setText( u"ERROR:\nNo folder was selected for input data and/or ouput data" )
            msg.exec()
        else:
            if(self.oud.get_path() == "" or os.path.exists(self.ind.get_path()) == False):
                msg = QtWidgets.QMessageBox()
                msg.setText( u"ERROR:\nNo folder was selected for input data and/or ouput data" )
                msg.exec()
            else:
                files = os.listdir(self.ind.get_path())
                if len(files) == 0:
                    msg = QtWidgets.QMessageBox()
                    msg.setText( u"ERROR:\nNo image .tif or .tiff found in the input folder" )
                    msg.exec()
                else:
                    have_images = False
                    imgs = []
                    for i in range(0,len(files)):
                        if(len(files[i]) > 4 ):
                            if(files[i][len(files[i])-3:len(files[i])] == "tif"):
                                have_images = True
                                imgs.append(files[i])
                        if(len(files[i]) > 5):
                            if(files[i][len(files[i])-4:len(files[i])] == "tiff"):
                                have_images = True
                                imgs.append(files[i])
                    if(have_images == False):
                        msg = QtWidgets.QMessageBox()
                        msg.setText( u"Error:\nNo image .tif or .tiff found in the input folder" )
                        msg.exec()
                    else:
                        work = 0
                        self.imgs = imgs
                        self.X = []
                        self.Y = []

                        for i in range(0,len(imgs)):
                            work += (1/(len(imgs)-1))*100
                            self.progress.setValue(work)

                            time.sleep(0.005)
                            self.X.append(i)
                            self.Y.append(i+random.randint(0,25))
                            #TODO METTRE LE CODE D'ANALYSE ICI
                        self.Graph.update_figure(self.X,self.Y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
