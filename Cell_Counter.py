import sys, os, math
from PySide2 import QtCore, QtGui, QtWidgets, QtCharts
import numpy as np

from internal_process import act

#CLASS HANDLING THE PROCESSING THREAD WORKER
class Woker(QtCore.QObject):
    finished = QtCore.Signal()
    working = QtCore.Signal(int)

    def __init__(self, window):
        QtCore.QObject.__init__(self)
        self.window = window

    def process(self):
        #PROCESS THE IMAGES
        work_prog = 0
        for i in range(0,len(self.window.imgs)):
            try:
                CellCount = act(self.window.path+"/"+self.window.imgs[i], i)
                self.window.result.append("tmp"+str(i)+".tiff")
                self.window.X.append(i)
                self.window.Y.append(CellCount)
            except:
                continue

            work_prog += (1/(len(self.window.imgs)-1))*100
            self.working.emit(work_prog)
        self.finished.emit()

#CLASS TO HANDLE THE IUTPUT PATH FIELD AND BROWSE BUTTON
class InputData(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        font = QtGui.QFont()
        font.setPointSize(10)
        opening = QtWidgets.QPushButton("Browse")
        opening.setObjectName("browse")
        opening.setFont(font)
        opening.setFixedSize(80,40)
        label2 = QtWidgets.QLabel("Path:")
        label2.setObjectName("path")
        font.setPointSize(14)
        label2.setFont(font)
        label2.setFixedWidth(60)
        font.setPointSize(10)
        self.label3 = QtWidgets.QLineEdit()
        self.label3.setObjectName("path_input")
        self.label3.setFont(font)
        self.label3.setMinimumWidth(300)
        self.label3.setFixedHeight(35)

        opening.clicked.connect(self.open_new_dialog)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(label2)
        layout.addWidget(self.label3)
        layout.addWidget(opening)
        self.setLayout(layout)

    #OPEN THE FILE EXPLORER AND MODIFY THE VALUE OF THE INPUT PATH FIELD
    def open_new_dialog(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(parent=self,caption='Select directory')
        self.label3.setText(str(path))
        self.repaint()
    
    def set_path(self,path):
        self.label3.setText(str(path))
        self.repaint()

    #RETURN THE INPUT PATH FIELD
    def get_path(self):
        return str(self.label3.text())

#CALL TO HANDLE THE CALLOUTS ON THE GRAPH
class Callout(QtWidgets.QGraphicsItem):
    def __init__(self, chart):
        QtWidgets.QGraphicsItem.__init__(self, chart)
        self._chart = chart
        self._text = ""
        self._textRect = QtCore.QRectF()
        self._anchor = QtCore.QPointF()
        self._font = QtGui.QFont()
        self._rect = QtCore.QRectF()

    #Rect for the callout
    def boundingRect(self):
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        rect = QtCore.QRectF()
        rect.setLeft(min(self._rect.left(), anchor.x()))
        rect.setRight(max(self._rect.right(), anchor.x()))
        rect.setTop(min(self._rect.top(), anchor.y()))
        rect.setBottom(max(self._rect.bottom(), anchor.y()))

        return rect

    #Draw the callout
    def paint(self, painter, option, widget):
        path = QtGui.QPainterPath()
        path.addRoundedRect(self._rect, 5, 5)
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        if not self._rect.contains(anchor) and not self._anchor.isNull():
            point1 = QtCore.QPointF()
            point2 = QtCore.QPointF()

            # establish the position of the anchor point in relation to _rect
            above = anchor.y() <= self._rect.top()
            aboveCenter = (anchor.y() > self._rect.top() and
                anchor.y() <= self._rect.center().y())
            belowCenter = (anchor.y() > self._rect.center().y() and
                anchor.y() <= self._rect.bottom())
            below = anchor.y() > self._rect.bottom()

            onLeft = anchor.x() <= self._rect.left()
            leftOfCenter = (anchor.x() > self._rect.left() and
                anchor.x() <= self._rect.center().x())
            rightOfCenter = (anchor.x() > self._rect.center().x() and
                anchor.x() <= self._rect.right())
            onRight = anchor.x() > self._rect.right()

            # get the nearest _rect corner.
            x = (onRight + rightOfCenter) * self._rect.width()
            y = (below + belowCenter) * self._rect.height()
            cornerCase = ((above and onLeft) or (above and onRight) or
                (below and onLeft) or (below and onRight))
            vertical = abs(anchor.x() - x) > abs(anchor.y() - y)

            x1 = (x + leftOfCenter * 10 - rightOfCenter * 20 + cornerCase *
                int(not vertical) * (onLeft * 10 - onRight * 20))
            y1 = (y + aboveCenter * 10 - belowCenter * 20 + cornerCase *
                vertical * (above * 10 - below * 20))
            point1.setX(x1)
            point1.setY(y1)

            x2 = (x + leftOfCenter * 20 - rightOfCenter * 10 + cornerCase *
                int(not vertical) * (onLeft * 20 - onRight * 10))
            y2 = (y + aboveCenter * 20 - belowCenter * 10 + cornerCase *
                vertical * (above * 20 - below * 10))
            point2.setX(x2)
            point2.setY(y2)

            path.moveTo(point1)
            path.lineTo(anchor)
            path.lineTo(point2)
            path = path.simplified()

        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.drawPath(path)
        painter.drawText(self._textRect, self._text)

    #Click event
    def mousePressEvent(self, event):
        event.setAccepted(True)

    #Hovering event
    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.setPos(self.mapToParent(
                event.pos() - event.buttonDownPos(QtCore.Qt.LeftButton)))
            event.setAccepted(True)
        else:
            event.setAccepted(False)

    #Set the text
    def setText(self, text):
        self._text = text
        metrics = QtGui.QFontMetrics(self._font)
        self._textRect = QtCore.QRectF(metrics.boundingRect(
            QtCore.QRect(0.0, 0.0, 150.0, 150.0),QtCore.Qt.AlignLeft, self._text))
        self._textRect.translate(5, 5)
        self.prepareGeometryChange()
        self._rect = self._textRect.adjusted(-5, -5, 5, 5)

    #Set the anchor
    def setAnchor(self, pointX, pointY):
        self._anchor = QtCore.QPointF(pointX, pointY)

    #Update the geometry
    def updateGeometry(self):
        self.prepareGeometryChange()
        self.setPos(self._chart.mapToPosition(
            self._anchor) + QtCore.QPointF(10, -50))


#CLASS TO HANDLE THE POPULATION GRAPH
class PopulationGraph(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)

        self.View = QtCharts.QtCharts.QChartView()
        self.View.setRubberBand(QtCharts.QtCharts.QChartView.HorizontalRubberBand)
        self.View.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.line = QtCharts.QtCharts.QLineSeries()
        self.zeros = QtCharts.QtCharts.QLineSeries()
        self.area = QtCharts.QtCharts.QAreaSeries(self.line,self.zeros)
        self.area.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.area.setBorderColor(QtCore.Qt.gray)
        self.area.setName("Cells")
        self.chart = QtCharts.QtCharts.QChart()
        self.chart.setTheme(self.chart.ChartThemeBlueIcy)
        self.chart.addSeries(self.area)
        self.chart.createDefaultAxes()
        self.chart.setContentsMargins(30,30,30,30)
        self.View.setChart(self.chart)

        layout.addWidget(self.View)
        self.setLayout(layout)
        self._tooltip = Callout(self.chart)
        self.area.hovered.connect(self.tooltip)
        self.setMouseTracking(True)
        self.X = []
        self.Y = []

    #Handle the Callouts on the graph
    def tooltip(self, point, state):
        if self._tooltip == 0:
            self._tooltip = Callout(self._chart)
        if state:
            for i in range(0,len(self.X)):
                if(i == 0):
                    if point.x() < (self.X[i]+0.5):
                        self._tooltip.setText("X: {0:.2f} \nY: {1:.2f} ".format(self.X[i],self.Y[i]))
                        self._tooltip.setAnchor(self.X[i],self.Y[i])
                        self._tooltip.setZValue(11)
                        self._tooltip.updateGeometry()
                        self._tooltip.show()
                        break
                elif(i == len(self.X)-1):
                    if point.x() >= self.X[i] - 0.5:
                        self._tooltip.setText("X: {0:.2f} \nY: {1:.2f} ".format(self.X[i],self.Y[i]))
                        self._tooltip.setAnchor(self.X[i],self.Y[i])
                        self._tooltip.setZValue(11)
                        self._tooltip.updateGeometry()
                        self._tooltip.show()
                        break
                else:
                    if point.x() >= self.X[i] - 0.5 and point.x() < (self.X[i]+0.5):
                        self._tooltip.setText("X: {0:.2f} \nY: {1:.2f} ".format(self.X[i],self.Y[i]))
                        self._tooltip.setAnchor(self.X[i],self.Y[i])
                        self._tooltip.setZValue(11)
                        self._tooltip.updateGeometry()
                        self._tooltip.show()
                        break
        else:
            self._tooltip.hide()
    
    #Modify the graph
    def setPopulation(self,X,Y):
        self.X = X
        self.Y = Y
        self.line.clear()
        self.zeros.clear()
        for i in range(0,len(X)):
            self.line.append(X[i],Y[i])
            self.zeros.append(X[i],0)
        self.chart.removeSeries(self.area)
        self.chart.addSeries(self.area)
        self.chart.createDefaultAxes()

#CLASS TO HANDLE THE IMAGES OF THE POPULATION
class PopulationImages(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(PopulationImages, self).__init__(parent)
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                QtGui.QPainter.HighQualityAntialiasing)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.home = self.matrix()
        self.viewstyle = 'background-color: white;'
        self.setStyleSheet(self.viewstyle)

        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.zoom = 0

    #Change the image displayed
    def Display(self, img):
        self.zoom = 0
        pixmap = QtGui.QPixmap(img)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self._photo.setPixmap(pixmap)
        self.fitInView(self._photo,QtCore.Qt.KeepAspectRatio)
    
    #Adjut the image if the window has been resized
    def Adjust(self):
        self.fitInView(self._photo,QtCore.Qt.KeepAspectRatio)

    #Scroll event
    def wheelEvent(self, event):
        if event.type() == QtCore.QEvent.Wheel and event.delta() < 0:
            self.zoom += 1
            self.scaleView(math.pow(2.0, -event.delta() / 500.0))
            super(PopulationImages, self).wheelEvent(event)
        elif event.type() == QtCore.QEvent.Wheel and event.delta() > 0:
            if(self.zoom > 0):
                self.zoom -= 1
                self.scaleView(math.pow(2.0, -event.delta() / 500.0))
                super(PopulationImages, self).wheelEvent(event)
        else:
            event.ignore()

    #Rescale the image  with a factor
    def scaleView(self, factor):
        f = self.matrix().scale(factor, factor). \
                    mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if f < 0.05 or f > 50:
            return
        self.scale(factor, factor)

#Main window Scroll
class Scroll(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super(Scroll, self).__init__(parent)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setMinimumSize(600,600)
    
    #Scroll event
    def wheelEvent(self, event):
        if(event.type() == QtCore.QEvent.Wheel):
            super(Scroll, self).wheelEvent(event)
        else:
            event.ignore()


#CLASS TO HANDLE THE WINDOW
class Window(QtWidgets.QWidget):
    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent)

        #PROCESS THREAD
        self.worker1 = Woker(self)
        self.thread = QtCore.QThread()
        self.worker1.moveToThread(self.thread)
        self.processing = QtCore.Signal()
        self.connect(self, QtCore.SIGNAL("processing()"), self.worker1, QtCore.SLOT("process()"))
        self.thread.start()

        self.worker1.finished.connect(self.End_Process)

        #MENU BARS
        bar = QtWidgets.QMenuBar()
        filemenu = QtWidgets.QMenu()
        filemenu.setTitle("File")
        opendir = QtWidgets.QAction("Open Directory",self)
        opendir.setShortcut("Ctrl+O")
        filemenu.addAction(opendir)
        self.connect(opendir, QtCore.SIGNAL("triggered()"), self, QtCore.SLOT("Open_Dir()"))
        saving = QtWidgets.QAction("Save",self)
        saving.setShortcut("Ctrl+S")
        filemenu.addAction(saving)
        self.connect(saving, QtCore.SIGNAL("triggered()"), self, QtCore.SLOT("Save()"))
        escape = QtWidgets.QAction("Quit",self)
        escape.setShortcut("Escape")
        filemenu.addAction(escape)
        self.connect(escape, QtCore.SIGNAL("triggered()"),self, QtCore.SLOT("Delete()"))
        helpmenu = QtWidgets.QMenu()
        helpmenu.setTitle("Help")
        manual = QtWidgets.QAction("Quick Start Guide...",self)
        helpmenu.addAction(manual)
        self.connect(manual, QtCore.SIGNAL("triggered()"), self, QtCore.SLOT("get_Help()"))
        bar.addMenu(filemenu)
        bar.addMenu(helpmenu)

        #TITLE
        Title = QtWidgets.QLabel("Cell Counter")
        Title.setObjectName("title")
        Title.setAlignment(QtCore.Qt.AlignTop)
        font = QtGui.QFont()
        font.setPointSize(28)
        font.setBold(True)
        Title.setFont(font)
        font.setBold(False)

        #PROGRESS BUTTON
        font.setPointSize(16)
        self.processB = QtWidgets.QPushButton("Process Data")
        self.processB.setObjectName("process")
        self.processB.setFixedHeight(50)
        self.processB.setFont(font)
        self.processB.clicked.connect(self.Process)

        #PROGRESS BAR
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setObjectName("progress")
        font.setPointSize(11)
        self.progress.setFont(font)
        self.progress.setMinimumHeight(40)
        self.labelprogress = QtWidgets.QLabel("")
        self.labelprogress.setObjectName("progression")
        self.labelprogress.setAlignment(QtCore.Qt.AlignTop)
        self.labelprogress.setFont(font)
        font.setPointSize(16)
        self.worker1.working.connect(self.progress.setValue)

        #QUIT BUTTON
        quitting = QtWidgets.QPushButton("QUIT")
        quitting.setFont(font)
        quitting.setObjectName("quit")
        quitting.setFixedHeight(50)
        self.connect(quitting, QtCore.SIGNAL("clicked()"),
                             self, QtCore.SLOT("Delete()"))

        #LAYOUTS (GLOBAL LAYOUT, INPUT LAYOUT, OUTPUT LAYOUT)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(15,0,15,15)
        self.layout.setSpacing(15)
        layoutin = QtWidgets.QVBoxLayout()
        layoutin.setContentsMargins(0,0,0,0)
        layoutin.setSpacing(0)
        layoutou = QtWidgets.QVBoxLayout()
        layoutou.setContentsMargins(0,0,0,0)
        layoutou.setSpacing(0)

        #INPUT WIDGETS
        self.ind = InputData()
        labelin = QtWidgets.QLabel("Input Folder:")
        labelin.setObjectName("input")
        labelin.setAlignment(QtCore.Qt.AlignBottom)
        labelin.setFont(font)
        labelin.setMinimumWidth(175)
        labelin.setMaximumWidth(175)
        labelin.setContentsMargins(0,50,0,15)

        #INPUT FORMAT
        labelpref = QtWidgets.QLabel("Images Prefix (ex: time => time1.tiff, time2.tiff...):")
        labelpref.setObjectName("prefix")
        labelpref.setAlignment(QtCore.Qt.AlignBottom)
        font.setPointSize(12)
        labelpref.setFont(font)
        self.inputpref = QtWidgets.QLineEdit()
        self.inputpref.setObjectName("prefix_input")
        self.inputpref.setFont(font)
        self.inputpref.setMinimumWidth(300)
        self.inputpref.setFixedHeight(35)
        font.setPointSize(16)

        #GRAPH WIDGETS
        labelgraph = QtWidgets.QLabel("Cell population:")
        labelgraph.setObjectName("population")
        labelgraph.setAlignment(QtCore.Qt.AlignBottom)
        labelgraph.setFont(font)
        labelgraph.setMinimumWidth(175)
        labelgraph.setMaximumWidth(200)
        labelgraph.setContentsMargins(0,50,0,15)
        self.Graph = PopulationGraph()
        self.Graph.setMinimumHeight(304)

        #GLOBAL VARIABLES FOR PROCESSING IMAGES
        self.has_finished = True
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
        self.View = PopulationImages(self)
        self.View.setMinimumHeight(357)
        self.labelimg = QtWidgets.QLabel("Population image:")
        self.labelimg.setObjectName("population_img")
        self.labelimg.setAlignment(QtCore.Qt.AlignBottom)
        self.labelimg.setFont(font)
        self.labelimg.setMinimumWidth(175)
        self.labelimg.setContentsMargins(0,50,0,15)
        font.setPointSize(18)
        nextbutton = QtWidgets.QPushButton(">")
        nextbutton.setObjectName("next")
        nextbutton.setFont(font)
        nextbutton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        nextbutton.clicked.connect(self.Next)
        backbutton = QtWidgets.QPushButton("<")
        backbutton.setObjectName("back")
        backbutton.setFont(font)
        backbutton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        backbutton.clicked.connect(self.Back)
        layoutimg.addWidget(backbutton)
        layoutimg.addWidget(self.View)
        layoutimg.addWidget(nextbutton)

        #SET THE LAYOUTS (GLOBAL LAYOUT, INPUT LAYOUT, OUTPUT LAYOUT)
        self.layout.addWidget(Title)
        layoutin.addWidget(labelin)
        layoutin.addWidget(self.ind)
        self.layout.addLayout(layoutin)
        self.layout.addWidget(labelpref)
        self.layout.addWidget(self.inputpref)
        self.layout.addWidget(self.processB)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.labelprogress)
        self.layout.addWidget(labelgraph)
        self.layout.addWidget(self.Graph)
        self.layout.addWidget(self.labelimg)
        self.layout.addLayout(layoutimg)
        self.layout.addWidget(quitting)

        #SCROLLING BAR WIDGETS
        Container = QtWidgets.QWidget()
        Container.setLayout(self.layout)
        Container.setObjectName("body")

        self.scroll = Scroll()
        self.scroll.setWidget(Container)

        #SCROLLING BAR LAYOUT
        vlayout = QtWidgets.QVBoxLayout(self)
        vlayout.setContentsMargins(0,0,0,0)
        vlayout.setSpacing(0)
        vlayout.addWidget(bar)
        vlayout.addWidget(self.scroll)
        self.setLayout(vlayout)

    #DETECT CLOSING EVENT
    def closeEvent(self, event):
        if(self.has_finished == True):
            self.thread.quit()
            self.deleteLater()
            event.accept()
        else:
            event.ignore()

    #SAVE THE X AND Y VALUES IN A CSV FILE
    def Save(self):
        arr = np.array([self.X,self.Y])
        np.savetxt("XY.csv",arr,delimiter=",")

    #DELETE THE THREAD BEFORE EXITING
    def Delete(self):
        if(self.has_finished == True):
            self.thread.quit()
            QtWidgets.qApp.quit()

    #SELECT DIRECTORY (SHORTCUT CTRL+O)
    def Open_Dir(self):
        self.ind.set_path(QtWidgets.QFileDialog.getExistingDirectory(parent=self,caption='Select directory'))

    #DISPLAY THE USER GUIDE
    def get_Help(self):
        msg = QtWidgets.QMessageBox()
        font = QtGui.QFont()
        font.setPointSize(12)
        msg.setFont(font)
        msg.setText("<html><h1>Manual</h1>"+
        "<h2>Prerequisites</h2>"+
        "<ul><li>A folder containing .tiff or .tif images of your cell population</li>"+
        "<li>Every images must have the same prefix followed by an integer superior or equal to 0 (ex: prefix = population, images = population0, population1...)</li></ul>"+
        "<h2>=================================</h2>"+
        "<h2>Step 1: Add the path of your images folder</h2><p>Click on the 'Browse' button and select the folder containing your image (Shortcuts: CTRL+O)</p>"+
        "<h2>Step 2: Add the images prefix</h2><p>Type your images's prefix in the prefix input field</p>"+
        "<h2>Step 3: Launch the processing of the images</h2><p>Click on the 'Process Data' button to process your images</p>"+
        "<h2>Step 4: Observe the results</h2><p>You can observe on the 'Cell population' graph the evolution of this cell population over time. By hovering your mouse on the graph you will see the points's values, and by selecting a part of the graph with the Left click you can zoom in (Left click to zoom out)</p><p>You can also observe on the 'Population image' displayer, on each timepoint the number of cells in your population with the buttons on both sides of the image (Shortcuts: CTRL+B = Last image, CTRL+N = Next image)</p>"+
        "<h3>Github:</h3><a href=\"https://github.com/Antonoir1/Quantification_of_cell_proliferation\">Quantification_of_cell_proliferation</a>"+
        "</html>")

        scroll = QtWidgets.QScrollArea()
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(750)
        scroll.setFixedHeight(525)
        scroll.setWidget(msg)
        scroll.setWindowTitle("Quick Start Guide")
        scroll.show()
        msg.exec()

    #GO TO THE NEXT IMAGE
    def Next(self):
        if(len(self.result)):
            if(self.position < (len(self.result)-1)):
                self.position += 1
                self.View.Display("./tmp/"+self.result[self.position])
                self.labelimg.setText("Population image: "+str(self.position+1)+"/"+str(len(self.result))+" Cells: "+str(self.Y[self.position]))

    #GO BACK TO THE LAST IMAGE
    def Back(self):
        if(len(self.result)):
            if(self.position > 0):
                self.position -= 1
                self.View.Display("./tmp/"+self.result[self.position])
                self.labelimg.setText("Population image: "+str(self.position+1)+"/"+str(len(self.result))+" Cells: "+str(self.Y[self.position]))

    #SHORTCUTS: NEXT IMAGE (CTRL + N)  LAST IMAGE(CTRL + B) 
    def keyPressEvent(self, event):
            k = event.key()
            m = int(event.modifiers())
            
            if QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+N'):
                self.Next()
            elif QtGui.QKeySequence(m+k) == QtGui.QKeySequence('Ctrl+B'):
                self.Back()
            else:
                event.ignore()
    
    #DYNAMIC HEIGHT FOR THE GRAPH AND THE IMAGE OF THE POPULATION
    def resizeEvent(self, event):
        if(self.View.width() <= 1100):
            self.View.setFixedHeight(int(self.View.width()*0.75))
        else:
            self.View.setFixedHeight(int(1100*0.75))
        self.View.Adjust()
        
        if(self.Graph.width() <= 1470):
            self.Graph.setFixedHeight(int(0.5*self.Graph.width()))
        else:
            self.Graph.setFixedHeight(int(0.5*1470))

    #EXECUTED AT THE END OF THE PROCESS
    def End_Process(self):
        if(len(self.result) != 0):
            self.labelprogress.setText("done.")
            self.Graph.setPopulation(self.X,self.Y)
            self.View.Display("./tmp/"+self.result[0])
            self.position = 0
            self.labelimg.setText("Population image: 1/"+str(len(self.result))+" Cells: "+str(self.Y[0]))
            self.processB.setEnabled(True)
        else:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText( u"ERROR:\nNo images could be processed, please check your files" )
            msg.exec()
        self.has_finished = True

        

    #CHECK THE PATHS OF THE INPUT/PREFIX FIELD AND LAUNCH THE PROCESS OF COUNTING
    def Process(self):
        #CHECK IF THE IMAGES HAVE THE RIGHT FORMAT
        if(self.ind.get_path() == "" or os.path.exists(self.ind.get_path()) == False or str(self.inputpref.text()) == "" or os.path.isdir(self.ind.get_path()) == False ):
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText( u"ERROR:\nNo folder was selected for input data and/or no prefix was entred" )
            msg.exec()
        else:
            files = os.listdir(self.ind.get_path())
            if len(files) == 0:
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle("Warning")
                msg.setText( u"ERROR:\nNo image .tif/.tiff found in the input folder" )
                msg.exec()
            else:
                have_images = False
                imgs = []
                for i in range(0,len(files)):
                    if(len(files[i]) > 4 ):
                        if(files[i][len(files[i])-3:len(files[i])] == "tif"):
                            if(len(str(self.inputpref.text()))+4 < len(files[i]) and str(self.inputpref.text()) in files[i] and str.isdecimal(files[i][len(str(self.inputpref.text())):len(files[i])-4]) == True):
                                if(int(files[i][len(str(self.inputpref.text())):len(files[i])-4]) >= 0):
                                    have_images = True
                                    imgs.append(files[i])
                    if(len(files[i]) > 5):
                        if(files[i][len(files[i])-4:len(files[i])] == "tiff"):
                            if(len(str(self.inputpref.text()))+5 < len(files[i]) and str(self.inputpref.text()) in files[i] and str.isdecimal(files[i][len(str(self.inputpref.text())):len(files[i])-5]) == True):
                                if(int(files[i][len(str(self.inputpref.text())):len(files[i])-5]) >= 0):
                                    have_images = True
                                    imgs.append(files[i])
                if(have_images == False):
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowTitle("Warning")
                    msg.setText( u"ERROR:\nNo image .tif/.tiff found in the input folder and/or the prefix value is uncorrect" )
                    msg.exec()
                else:
                    unordered = []
                    ordering = []
                    w = 0
                    for i in imgs:
                        if(".tiff" in i):
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
                        while(unordered[i] != ordering[k][0] and k < len(ordering)):
                            k += 1
                        self.imgs.append(ordering[k][1])
                    
                    if(os.path.isdir("./tmp") == False):
                        os.mkdir("tmp")

                    for filename in os.listdir("./tmp"):
                        os.remove("./tmp/"+filename)
                        QtCore.QCoreApplication.processEvents()

                    self.X = []
                    self.Y = []
                    self.result = []
                    self.path = self.ind.get_path()
                    self.prefix = str(self.inputpref.text())
                    self.labelprogress.setText("in progress...")
                    self.has_finished = False
                    self.emit(QtCore.SIGNAL("processing()"))
                    self.processB.setEnabled(False)
                    
                        



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    try:
        css = open("./style.txt","r")
        css = css.read()
        app.setStyleSheet(css)
    except:
        print("ERROR: File "+str(os.getcwd())+"\\style.txt not found")
        print("The app will use the default style")

    window = Window()
    window.setWindowTitle("Cell Counter")
    window.show()
    sys.exit(app.exec_())
