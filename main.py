# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import face_recognition
from PyQt5.QtCore import QThread, pyqtSignal
import threading
import os
import shutil
import glob
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

class Thread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(Thread, self).__init__()

    def run(self):
        while ui.progressValue != ui.numberOfUnknownImages:
            time.sleep(0.1)
            progressValue = int((ui.progressValue/ui.numberOfUnknownImages)*100)
            self._signal.emit(progressValue)

class Ui_MainWindow(object):
    
    def __init__(self):
        self.dir_ = None
        self.file_ = None
    
    def recognition(self,unknown_face_encoding):
        match = face_recognition.compare_faces([self.known_face_encoding],unknown_face_encoding,tolerance=0.48)
        return match[0]
        
    def preprocessing(self,unknown_image):
        try:
            unknown_picture = face_recognition.load_image_file(unknown_image)
        except:
            pass
        unknown_face_locations = face_recognition.face_locations(unknown_picture)
        if len(unknown_face_locations) != 0:
            unknown_face_encodings = face_recognition.face_encodings(unknown_picture,unknown_face_locations)
            with ThreadPoolExecutor() as executor:
                hasKnownFace = executor.map(self.recognition,unknown_face_encodings)
            executor.shutdown(wait=True)
            if True in hasKnownFace:
                try:
                    shutil.move(unknown_image,self.destinationFolder)
                except:
                    pass
            self.progressValue += 1
    
    def process(self,unknown_images):
        batch_size = 50
        batches = [unknown_images[i:i+batch_size] for i in range(0,len(unknown_images),batch_size)]
        for batch in batches:
            with ThreadPoolExecutor() as executor:
                executor.map(self.preprocessing,batch)            
            
    def startProcess(self):
        if self.dir_ and self.file_:
            self.progressBar.setVisible(True)
            self.progressValue = 0
            imageFileName = self.file_[0]
            srcFolder = self.dir_
            try:
                os.mkdir(path=srcFolder+f"/{imageFileName.split('/')[-1][:-4]}")
            except:
                pass
            self.btn4.setEnabled(True)
            self.destinationFolder = srcFolder+f"/{imageFileName.split('/')[-1][:-4]}"
            try:
                known_image = face_recognition.load_image_file(imageFileName)
                self.known_face_encoding = face_recognition.face_encodings(known_image)[0]
            except:
                self.msg = QtWidgets.QMessageBox()
                self.msg.setIcon(QtWidgets.QMessageBox.Critical)
                self.msg.setText("Error")
                self.msg.setInformativeText("Please select another image")
                self.msg.setWindowTitle("Error")
                self.msg.exec_()
                sys.exit(-1)
                
            unknown_images = glob.glob(srcFolder+"/*.jpg")
            self.numberOfUnknownImages = len(unknown_images)
            
            self.thread = Thread()
            self.thread._signal.connect(self.signal_accept)
            self.thread.start()
            
            self.t1 = threading.Thread(target=self.process,args=[unknown_images])
            self.t1.start()
            
    def signal_accept(self, msg):
        self.progressBar.setValue(int(msg))
        self.startBtn.setEnabled(False)
        if self.progressBar.value() >= 100:
            self.progressBar.setVisible(False)
            self.startBtn.setEnabled(True)
            
    def openFolder(self):
        self.dir_ = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select project folder:', 'F:\\', QtWidgets.QFileDialog.ShowDirsOnly)
        self.textEdit.setPlaceholderText(self.dir_)
    
    def selectFile(self):
        self.file_ = QtWidgets.QFileDialog.getOpenFileName(None,"Select an image","F:\\","*.jpg *.png")
        if len(self.file_[0]) != 0:
            self.textEdit_2.setPlaceholderText(self.file_[0])
        else:
            self.file_ = None
    
    def openExplorer(self):
        path = self.destinationFolder.replace("/","\\")
        subprocess.call(f"explorer {path}", shell=True)
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(622, 319)
        MainWindow.setMinimumSize(QtCore.QSize(622, 319))
        MainWindow.setMaximumSize(QtCore.QSize(622, 319))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startBtn = QtWidgets.QPushButton(self.centralwidget)
        self.startBtn.setGeometry(QtCore.QRect(270, 220, 81, 31))
        self.startBtn.setObjectName("startBtn")
        self.startBtn.clicked.connect(self.startProcess)
        
        self.btn1 = QtWidgets.QPushButton(self.centralwidget)
        self.btn1.setGeometry(QtCore.QRect(10, 20, 91, 31))
        self.btn1.setObjectName("btn1")
        self.btn1.clicked.connect(self.openFolder)
        
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(110, 20, 501, 31))
        self.textEdit.setReadOnly(True)
        self.textEdit.setPlaceholderText("No folder chosen")
        self.textEdit.setObjectName("textEdit")
        
        self.btn2 = QtWidgets.QPushButton(self.centralwidget)
        self.btn2.setGeometry(QtCore.QRect(10, 70, 91, 31))
        self.btn2.setFlat(False)
        self.btn2.setObjectName("btn2")
        self.btn2.clicked.connect(self.selectFile)
        
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(110, 70, 501, 31))
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setPlaceholderText("No file chosen")
        self.textEdit_2.setObjectName("textEdit_2")
        
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setGeometry(QtCore.QRect(120, 170, 411, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setVisible(False)
        
        self.btn4 = QtWidgets.QPushButton(self.centralwidget)
        self.btn4.setEnabled(False)
        self.btn4.setGeometry(QtCore.QRect(10, 120, 91, 31))
        self.btn4.setCheckable(False)
        self.btn4.setObjectName("btn4")
        self.btn4.clicked.connect(self.openExplorer)
        
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(16, 269, 601, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Image Categorizer"))
        self.startBtn.setText(_translate("MainWindow", "Start"))
        self.btn1.setToolTip(_translate("MainWindow", "<html><head/><body><p>Select a folder which contains images</p></body></html>"))
        self.btn1.setText(_translate("MainWindow", "Choose a folder"))
        self.btn2.setToolTip(_translate("MainWindow", "<html><head/><body><p>Select an image from the folder</p></body></html>"))
        self.btn2.setText(_translate("MainWindow", "Choose an image"))
        self.btn4.setToolTip(_translate("MainWindow", "<html><head/><body><p>Open Explorer</p></body></html>"))
        self.btn4.setText(_translate("MainWindow", "See Results"))
        self.label.setText(_translate("MainWindow", "Made with ❤️ by Ritwick"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())