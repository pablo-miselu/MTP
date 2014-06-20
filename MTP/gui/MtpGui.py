# Copyright 2013 Pablo De La Garza, Miselu Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

from MTP.core.SequencerThread import SequencerThread

from PySide import QtGui, QtCore

import Queue
import os


class MtpGui(QtGui.QWidget):
    """
    | Takes care of providing a simple graphical user interface.
    """
    def __init__(self, parent=None):
        super(MtpGui, self).__init__(parent)
        
        self.inBoundQueue = Queue.Queue() #main inbound queue
        self.outBoundQueue = Queue.Queue() #main outbound queue, currently only for Dlg returns
        self.guiApi = MtpGuiApi(self.inBoundQueue,self.outBoundQueue)
        
        self.resize(705,628)
        self.move(400,100)
        
        self.setWindowTitle('Miselu Test Platform')
        
        ###   Sets a timer to poll the incoming queue   ###
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkQueue)
        self.timer.start(500)
        
        self.initLayout()
    
    
    def initLayout(self):
        """
        Initializes the layout of the window.
        """

        self.stackedLayout = QtGui.QStackedLayout()
        
        ###   Index 0   ###
        button = QtGui.QPushButton('Start Test')
        button.clicked.connect(self.startTestRun)
        l = QtGui.QVBoxLayout()
        l.setAlignment(QtCore.Qt.AlignTop)
        l.addWidget(button)
        w = QtGui.QWidget()
        w.setLayout(l)
        self.stackedLayout.addWidget(w)
        
        ###   Index 1 ###
        self.tabWidget = QtGui.QTabWidget() 
        self.stackedLayout.addWidget(self.tabWidget)
        
        self.setLayout(self.stackedLayout)
        
    def reInitLayout(self):
        self.stackedLayout.setCurrentIndex(0)
        self.stackedLayout.takeAt(1).widget().deleteLater()
        self.tabWidget = QtGui.QTabWidget() 
        self.stackedLayout.addWidget(self.tabWidget)

    def startTestRun(self):
        """
        | Sets the window layout to a test layout.
        | Launches a thread that will instantiate a *Sequencer*
        | (see :ref:`label_Sequencer` and :ref:`label_SequencerThread`).
        | Sets a timer to periodically check the incoming queue.
        """
        
        self.consoleDict = {}
        self.stackedLayout.setCurrentIndex(1)
        
        ###   Launches the *SequencerThread*   ###
        self.sequencerThread = SequencerThread(self.guiApi)
        self.sequencerThread.start()


    def addConsole(self,consoleID,consoleTitle):
        """
        Adds a new console to the tabWidget on the gui.
        
        Args:
        
        * consoleID (str): Unique identifier for console
        * consoleTitle (str): This is what is displayed on the tab
        
        Returns:
            None
        """
        self.consoleDict[consoleID] = consoleWidget(self.tabWidget)
        self.tabWidget.addTab(self.consoleDict[consoleID],consoleTitle)
       
       
    def consoleWrite(self,consoleID,s):
        """
        Writes (appends) into a console.
        
        Args:
        
        * consoleID (str): Unique identifier for the console
        * s (str): String to write
        
        Returns:
            None
        """
        
        
        ss = ''
        for i in range(len(s)):
            if ord(s[i])&0x80:
                c = '[ %0.2X ]' % ord(s[i])
                print c
            else:
                c = s[i]
            ss += c

        t = self.consoleDict[consoleID].consoleLabel
        t.setText((str(t.text())+str(ss))[-5000:])
        t.adjustSize()
        
        t = self.consoleDict[consoleID]
        t.scrollArea.verticalScrollBar().setValue(t.scrollArea.verticalScrollBar().maximum())


    def checkQueue(self):
        """
        Reads and processes any and all messages in the incomming queue.
        """
        stop = False
        while not stop:
            try:
                entry = self.inBoundQueue.get_nowait()
                self.processQueueEntry(entry)
            except Queue.Empty:
                stop = True

                
    def processQueueEntry(self,entry):
        """
        Processes the entry. That is executes the command requested.
        
        Args:
        
        * entry (dict): A dictionary with the data required to process such message
            * It always should contain at least the key *command*
            * The other contents of entry depend on the command itself
        
        Returns:
            None
        """
        if entry['command']=='addConsole':
            self.addConsole(entry['consoleID'],entry['title'])
        
        elif entry['command']=='consoleWrite':
            self.consoleWrite(entry['consoleID'],entry['text'])
      
        elif entry['command']=='pDialog':
            entry.pop('command')
            entry['queue']=self.outBoundQueue
            entry['parent'] = self
            self.dialogWindow = Window_pDialog(**entry)
            self.dialogWindow.show()
        
        elif entry['command']=='closeDialogBox':
            self.dialogWindow.close()            
        
        elif entry['command']=='reInitLayout':
            self.reInitLayout()
        
        elif entry['command']=='processEvents':
            QtGui.QApplication.processEvents()
        else:
            raise Exception('Invalid command:'+entry['command'])  
    
class MtpGuiApi:
    """
    | The central and only way for any other module to interact with *MtpGui*.
    | It takes care of relaying messages so that it can be processed as well as
    | providing functions to get the results from dialog windows.
    """
    def __init__(self,inboundQueue,outboundQueue):
        self.sendQueue = inboundQueue
        self.receiveQueue = outboundQueue
        
    def sendMessage(self, msg):
        """
        Puts a message into the incoming queue of *MtpGui*.
        
        Args:
        
        * msg (dict): A dictionary with the data required to process such message
            * It always should contain at least the key *command*
            * The other contents of entry depend on the command itself
        
        Returns:
            None
        """
        self.sendQueue.put(msg)
    
    def getDialogReturn(self):
        """
        | Gets the data describing the interactions of the user with the dialog.
        
        Args:
            None
            
        Returns:
        
        * *None*, if the dialog has not closed yet
        * The data otherwise   
            * For the format see MTP.gui.MtpGui.Window_pDialog.closing
        """
        try:
            t = self.receiveQueue.get_nowait()
        except Queue.Empty:
            t = None
        return t
    
    def waitForDialogReturn(self):
        """
        | Waits untile the dialog has been answered/closed.
        | Retrieves the data describing the interactions of the user with the dialog.
        
        Args:
            None
            
        Returns:

        * The data, for the format see MTP.gui.MtpGui.Window_pDialog.closing
        """
        t = None
        while (t==None):
            t = self.getDialogReturn()
        return t
    
    
class consoleWidget (QtGui.QWidget):
    """
    A custom widget to look and behave as a console/terminal display
    """
    def __init__(self, parent=None):
        super(consoleWidget, self).__init__(parent)
        self.layout = QtGui.QVBoxLayout()
        self.consoleLabel = QtGui.QLabel()
        self.consoleLabel.setStyleSheet('background-color : black; \
                                         color : lightgreen; \
                                         qproperty-alignment: "AlignLeft | AlignTop"; \
                                         qproperty-wordWrap: True;\
                                        ')
        
        
        ###   Size   ###   
        g = parent.geometry()
        self.consoleLabel.setMinimumSize(QtCore.QSize(g.width()-42,g.height()-56))
            
        #self.consoleLabel.setMinimumSize(QtCore.QSize(640, 480))
        
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.consoleLabel)
        self.layout.addWidget(self.scrollArea)
        
        self.setLayout(self.layout)
        self.show()


class OneLineEdit(QtGui.QTextEdit):
    """
    A custom widget for a one line text box.
    """
    def __init__(self,inputHeight=30,parent=None):
            super(OneLineEdit, self).__init__(parent=None)
        
            self.setFixedHeight(inputHeight) 
            self.setTabChangesFocus(True)
            self.setWordWrapMode(QtGui.QTextOption.NoWrap)
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    
    def keyPressEvent(self, event):
        """
        Intercepts the return key and sends it as a signal
        """
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            event.ignore()
            self.emit(QtCore.SIGNAL('ENTER'))
        else:
            super(OneLineEdit, self).keyPressEvent(event)
        
    
class Window_pDialog(QtGui.QDialog):
    """
    A custom dialog window to handle most common needs.
    
    Args:
    
    * queue (queue): The queue were the data input by the user will be placed
    * parent (obj): The paren of the dialog window
    * msg (str) : The message for the dialog window
    * title (str): The title for the dialog window
    * inputHeight (int): Height in pixels for the input field
        * if inputHeight is None, no input field will be created
    * buttonTextList (list): List of strings to be the text for the buttons
    * defaultButtonText (str): The button to be used as default when pressing *ENTER* inside the input field
    * sizeX (int): Window size in x-coordinate
    * sizeY (int): Window size in y-coordinate
    * imageFileName (str): File name of the image to load (if None no image is loaded)
    * language (str): The language to use for images with words (see the img directory)
    
    Returns:
        None, data retrieval is done through the *guiApi*
    """
    
    def __init__(self,queue,parent,msg=None,title=' ',inputHeight=None,buttonTextList = ['OK'],defaultButtonText=None,sizeX=300,sizeY=200,imageFileName=None,language=None):
        super(Window_pDialog, self).__init__(parent=None)

        ###   Object variables   ###
        if defaultButtonText==None:
            defaultButtonText = buttonTextList[0]    
        self.queue = queue
        self.buttonTextList = buttonTextList
        self.defaultTextButton = defaultButtonText
        self.inputHeight = inputHeight 
        
        ###   Size and Position   ###   
        g = parent.geometry()
        posX = g.x()+(g.width()-sizeX)/2
        posY = g.y()+(g.height()-sizeY)/2
        self.resize(sizeX,sizeY)
        self.move(posX,posY)
        
        ###   Title   ###
        self.setWindowTitle(title)
        layout = QtGui.QVBoxLayout()
        
        ###   Image   ###
        if imageFileName:
            try:
                pixmap = QtGui.QPixmap(os.path.join(os.environ['MTP_TESTSTATION'],'MTP','img',language,imageFileName))
            except:
                pixmap = QtGui.QPixmap(os.path.join(os.environ['MTP_TESTSTATION'],'MTP','img','default',imageFileName))
            
            imageLabel = QtGui.QLabel()
            imageLabel.setPixmap(pixmap)
            layout.addWidget(imageLabel)

        ###   Msg   ###
        if msg:
            self.label = QtGui.QLabel(msg)
            layout.addWidget(self.label)

            
        ###   TextInput   ###
        if inputHeight:
            self.textInput = OneLineEdit(inputHeight)
            layout.addWidget(self.textInput)
            self.connect(self.textInput,QtCore.SIGNAL('ENTER'),lambda : self.closing('ENTER') )
            
        ###   Buttons   ###
        buttonLayout = QtGui.QHBoxLayout()
        for i in range (len(buttonTextList)):
            button = QtGui.QPushButton(buttonTextList[i])
            buttonLayout.addWidget(button)
            
            # This block is required to make constant the index 'i'.
            # If you were to pass buttonTextList[i] instead for the lambda function
            # all would be connected to the last element of buttonTextList.
            if   i==0: button.clicked.connect(lambda : self.closing(buttonTextList[0]) )
            elif i==1: button.clicked.connect(lambda : self.closing(buttonTextList[1]) )
            elif i==2: button.clicked.connect(lambda : self.closing(buttonTextList[2]) )
            elif i==3: button.clicked.connect(lambda : self.closing(buttonTextList[3]) )
            elif i==4: button.clicked.connect(lambda : self.closing(buttonTextList[4]) )
            elif i==5: button.clicked.connect(lambda : self.closing(buttonTextList[5]) )
            elif i==6: button.clicked.connect(lambda : self.closing(buttonTextList[6]) )
            elif i==7: button.clicked.connect(lambda : self.closing(buttonTextList[7]) )
            elif i==8: button.clicked.connect(lambda : self.closing(buttonTextList[8]) )
            elif i==9: button.clicked.connect(lambda : self.closing(buttonTextList[9]) )
        
        layout.addLayout(buttonLayout)
     
        ###   Add Layout   ###
        self.setLayout(layout)
        
    
    def closing(self,triggerSrc):
        """
        Puts button-pressed-text and textInput string into the assigned queue.
        Closes the window.
        
        *Typically used to be connected to button pressed events and such.*
        
        Args:
    
        * triggerSrc (str): An ID of the trigger source
    
        Returns:
            None
        """
        
        if triggerSrc=='ENTER': triggerSrc = self.defaultTextButton
        if self.inputHeight:
            self.queue.put((triggerSrc,str(self.textInput.toPlainText())))
        else:
            self.queue.put( (triggerSrc,None) )
        self.close()
    
    
if __name__ == '__main__':   
    app = QtGui.QApplication([])
    w = MtpGui()
    w.show()
    app.exec_()
    
