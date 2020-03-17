#include <QTimer>
#include <QtXml/QDomDocument>
#include <QtXml/QDomNodeList>
#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "ui_AddSerialDialog.h"

//************************************************************************
MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow),
    addserialui(new Ui::AddSerialDialog),
    socket(this),
    _checkSocketTimer(this),
    _waitBoxTimer(this),
    _commandXML(""),
    _waitBox(NULL),
    _timoutMsg(""),
    _showErrBox(false),
    _initConnect(false)
{
  ui->setupUi(this);

  connect(ui->SetConfigPushButton, SIGNAL(released()), 
          this, SLOT(handleSetConfigButtonSlot()));
  connect(ui->GetConfigPushButton, SIGNAL(released()), 
          this, SLOT(handleGetConfigButtonSlot()));
  connect(ui->AddSerialPushButton, SIGNAL(released()), 
          this, SLOT(handleAddSerialButtonSlot()));
  connect(ui->DeleteSerialPushButton, SIGNAL(released()), 
          this, SLOT(handleDeleteSerialButtonSlot()));
  connect(&socket, SIGNAL(connected()), this, SLOT(SocketConnectedSlot()));
  connect(&socket, SIGNAL(disconnected()), 
          this, SLOT(SocketDisconnectedSlot()));
  connect(&socket, SIGNAL(readyRead()), this, SLOT(SocketReadyReadSlot()));
  connect(&socket, SIGNAL(error(QAbstractSocket::SocketError)),
          this, SLOT(SocketErrorSlot()));
  connect(&_checkSocketTimer, SIGNAL(timeout()), 
          this, SLOT(handleCheckSocketTimerSlot()));
  connect(&_waitBoxTimer, SIGNAL(timeout()), 
          this, SLOT(handleWaitBoxTimeOutSlot()));
  
  QTimer::singleShot(100, this, SLOT(StartAppSlot()));
}

//************************************************************************
MainWindow::~MainWindow()
{
  socket.disconnect();
  delete ui;
}

//************************************************************************
void MainWindow::StartAppSlot()
{
  ui->SerialDataTextEdit->append("POS App Gui version 0.7 (10-25-2014 13:00)");
  displayWaitBox("Please wait, Attempting connection to POS App", 2000,
                 "Connection failed, exiting");
  socket.connectToHost("127.0.0.1", 1800);
  if (!socket.waitForConnected(3000))
  {
    ClosePleaseWaitDialog();
    handleError("Cannot connect to POS App, please make sure it is running first", true);
    exit(0);
  }
  ClosePleaseWaitDialog();

  _checkSocketTimer.start(500);

  // Get config
  getConfig();
}

/////////////////////////////////////////////////////////////////////////
// SERIAL ///////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

//************************************************************************
void MainWindow::ProcessPOSAppSerialData(QDomNode cmdnode)
{
  //<?xml version="1.0" encoding="UTF-8"?>
  // <pos_serial_data>
  // <serial_data value=""/>
  // <pos_serial_data>

  if (cmdnode.firstChildElement("serial_data").isNull())
    return;
  
  QString datastr = 
       cmdnode.firstChildElement("serial_data").attribute("value", "");
  if (datastr.length() > 0)
    handleSerialData(datastr);
}

//************************************************************************
void MainWindow::handleSerialData(const QString &data)
{
  ui->SerialDataTextEdit->append(data);
}

//************************************************************************
void MainWindow::handleDeleteSerialButtonSlot()
{
  QList<QTreeWidgetItem *> itemlist = 
                      ui->SerialSetupTreeWidget->selectedItems();
  for (int i=0; i<itemlist.size(); i++)
  {
    if (itemlist.at(i)->parent() != NULL)
    {
      QTreeWidgetItem *item = itemlist.at(i)->parent();
      if (_serialPortLut.find(item->text(0).trimmed()) != _serialPortLut.end())
        _serialPortLut.erase(item->text(0).trimmed());
      delete item;
    }
    else
    {
      QTreeWidgetItem *item = itemlist.at(i);
      if (_serialPortLut.find(item->text(0).trimmed()) != _serialPortLut.end())
        _serialPortLut.erase(item->text(0).trimmed());
      delete item;
    }
  }
}

//************************************************************************
void MainWindow::handleAddSerialButtonSlot()
{
  QDialog addserialdialog(this);
  addserialui->setupUi(&addserialdialog);
  connect(addserialui->ASDAddSerialPushButton, SIGNAL(released()),
          this, SLOT(handleASDAddSerialButtonSlot()));
  connect(this, SIGNAL(CloseAddSerialDialog()),
          &addserialdialog, SLOT(accept()));
  connect(addserialui->ASDProtocolComboBox, 
          SIGNAL(currentTextChanged(const QString &)),
          this, SLOT(handleASDProtocolComboBoxSlot(const QString &)));
  int retcode = addserialdialog.exec();
  qDebug() << "Add Serial Dialog exitted with code " << retcode;

  if (retcode == 1)
  {
    QTreeWidgetItem *item = new QTreeWidgetItem(ui->SerialSetupTreeWidget);
    item->setText(0, "Name: "+addserialui->ASDSerialIDLineEdit->text());
    item->addChild(new QTreeWidgetItem(item, 
        QStringList("Port: "+addserialui->ASDCOMPortComboBox->currentText())));
    item->addChild(new QTreeWidgetItem(item, 
       QStringList("Baud Rate: "+addserialui->ASDBaudComboBox->currentText())));
    item->addChild(new QTreeWidgetItem(item, 
        QStringList("Parity: "+addserialui->ASDParityComboBox->currentText())));
    item->addChild(new QTreeWidgetItem(item, 
        QStringList("Flow Ctrl: "+addserialui->ASDFlowComboBox->currentText())));
    item->addChild(new QTreeWidgetItem(item, 
        QStringList("Stop Bits: "+addserialui->ASDStopBitsComboBox->currentText())));
    item->addChild(new QTreeWidgetItem(item, 
        QStringList("Char Size: "+addserialui->ASDCharSizeComboBox->currentText())));
    item->addChild(new QTreeWidgetItem(item, 
        QStringList("Timeout: "+ QString::number(addserialui->ASDTimeoutSpinBox->value()))));
    ui->SerialSetupTreeWidget->addTopLevelItem(item);
  }
}

//************************************************************************
void MainWindow::handleASDAddSerialButtonSlot()
{
  if (addserialui->ASDSerialIDLineEdit->text() == "")
  {
    handleError("Please enter a Serial ID", true);
    return;
  }

  if (_serialPortLut.find(addserialui->ASDSerialIDLineEdit->text().trimmed()) !=
      _serialPortLut.end())
  {
    handleError("Duplicate Serial ID found, please enter an unique Serial ID", 
                true);
    return;
  }

  // Save serial
  
  SerialPort serialport;
  serialport.name = addserialui->ASDSerialIDLineEdit->text().trimmed();
  serialport.port = addserialui->ASDCOMPortComboBox->currentText().trimmed();
  serialport.baud = 
               addserialui->ASDBaudComboBox->currentText().trimmed().toInt();
  serialport.parity = addserialui->ASDParityComboBox->currentText().trimmed();
  serialport.stopbits = 
          addserialui->ASDStopBitsComboBox->currentText().trimmed().toFloat();
  serialport.charsize = 
           addserialui->ASDCharSizeComboBox->currentText().trimmed().toInt();
  serialport.flowctrl = addserialui->ASDFlowComboBox->currentText();
  serialport.protocol = 
                    addserialui->ASDProtocolComboBox->currentText().trimmed();
  _serialPortLut["Name: "+addserialui->ASDSerialIDLineEdit->text().trimmed()] = 
                                                                   serialport;

  // Close add serial dialog  
  CloseAddSerialDialog();
}

//************************************************************************
void MainWindow::handleASDProtocolComboBoxSlot(const QString &text)
{
  if (text == "Nucleus")
  {
    addserialui->ASDBaudComboBox->setCurrentText("9600");
    addserialui->ASDParityComboBox->setCurrentText("n");
    addserialui->ASDFlowComboBox->setCurrentText("n");
    addserialui->ASDStopBitsComboBox->setCurrentText("1");
    addserialui->ASDCharSizeComboBox->setCurrentText("8");
  }
}

/////////////////////////////////////////////////////////////////////////
// SOCKET ///////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

//************************************************************************
void MainWindow::handleCheckSocketTimerSlot()
{
  QAbstractSocket::SocketState socketstate = socket.state();
  qDebug() << "Checking socket state - " << socketstate;
  switch(socketstate)
  {
    case QAbstractSocket::ConnectedState:
      break;
    
    case QAbstractSocket::UnconnectedState:
      _checkSocketTimer.stop();
      displayWaitBox("Please wait, Attempting reconnection to POS App", 2000,
                     "Reconnection failed, exiting");
      socket.connectToHost("127.0.0.1", 1800);
      if (!socket.waitForConnected(3000))
      {
        ClosePleaseWaitDialog();
        handleError("Cannot reconnect to POS App, please make sure it is running first", true);
        exit(0);
      }
      ClosePleaseWaitDialog();
      _checkSocketTimer.start(500);
      break;

    case QAbstractSocket::HostLookupState:
    case QAbstractSocket::ConnectingState:
    case QAbstractSocket::ClosingState:
      break;
  };
}

//************************************************************************
void MainWindow::handleSocketStateChangedSlot(
                              QAbstractSocket::SocketState socketState)
{
  qDebug() << "Socket state - " << socketState;

  switch(socketState)
  {
    case QAbstractSocket::ConnectedState:
      break;
    
    case QAbstractSocket::UnconnectedState:
      displayWaitBox("Please wait, Attempting reconnection to POS App", 3000,
                     "Reconnection failed, exiting");
      socket.connectToHost("127.0.0.1", 1800);
      if (!socket.waitForConnected(3000))
      {
        exit(0);
      }
      ClosePleaseWaitDialog();
      break;

    case QAbstractSocket::HostLookupState:
    case QAbstractSocket::ConnectingState:
    case QAbstractSocket::ClosingState:
      break;
  };
}

//************************************************************************
void MainWindow::SocketReadyReadSlot()
{
  qDebug("Socket ready read");

  // Read all socket data
  QByteArray data = socket.readAll();

  // Check if valid xml

  _socketBuffer += data;
  QDomDocument xmldoc;
  if (!xmldoc.setContent(_socketBuffer))
    return;
  _socketBuffer.clear();

  // Parse XML

  QDomNode n = xmldoc.firstChild();  //<?xml version="1.0" encoding="UTF-8"?>
  if (n.isNull())
  {
    handleError("Error in socket xml data - errcode 1", true);
    return;
  }
  QDomElement e = n.nextSiblingElement();
  n = n.nextSibling();
  if (n.isNull())
  {
    handleError("Error in socket xml data - errcode 2", true);
    return;
  }

  QString tag = e.tagName();
  if (tag == "pos_app_config")
  {
    ProcessPOSAppConfigReply(n);
    ClosePleaseWaitDialog();
  }
  if (tag == "pos_serial_data")
  {
    ProcessPOSAppSerialData(n);
  }
  else if (tag == "SUCCESS")
  {
    _initConnect = true;
    ClosePleaseWaitDialog();
    handleError("Operation succeeded", true);
  }
  else if (tag == "FAILURE")
  {
    ClosePleaseWaitDialog();
    handleError("Operation FAILED", true);
  }
}

//************************************************************************
void MainWindow::SocketConnectedSlot()
{
  qDebug("Socket connected");
}

//************************************************************************
void MainWindow::SocketDisconnectedSlot()
{
  qDebug("Socket disconnected");
}

//************************************************************************
void MainWindow::SocketErrorSlot()
{
  qDebug("Socket error");
  ////  socket.disconnect();
}

/////////////////////////////////////////////////////////////////////////
// CONFIG ///////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

//************************************************************************
void MainWindow::handleGetConfigButtonSlot()
{
  getConfig();
}

//************************************************************************
void MainWindow::getConfig()
{
  // If not connected, show error
  if (socket.state() != QAbstractSocket::ConnectedState)
  {
    handleError("Not connected to POS App", true);
    return;
  }

  // Send get config cmd

  socket.write("<?xml version='1.0' encoding='UTF-8'?>"
               "<pos_app_config>"
               "<command id='get_config'/>"
               "</pos_app_config>"
               "<EOF>");
  socket.flush();

  qDebug() << "Get config command sent\n";
  displayWaitBox("Please wait, retrieving POS App configuration", 10000,
                 "Get configuration failed");
}

//************************************************************************
void MainWindow::ProcessPOSAppConfigReply(QDomNode cmdnode)
{
  // Check to make sure all data is present

  if (cmdnode.firstChildElement("pos_location").isNull() || 
      cmdnode.firstChildElement("server_address").isNull() || 
      cmdnode.firstChildElement("server_path").isNull() || 
      cmdnode.firstChildElement("log_path").isNull() || 
      cmdnode.firstChildElement("log_level").isNull())
  {
    handleError("Error retrieving config information", true);
    return;
  }

  _initConnect = true;
  ClosePleaseWaitDialog();

  // Update gui fields

  ui->PLIDLineEdit->setText(
      cmdnode.firstChildElement("pos_location").attribute("id", "empty"));
  ui->ServerAddrLineEdit->setText(
      cmdnode.firstChildElement("server_address").attribute("id", "empty"));
  ui->ServerPathLineEdit->setText(
      cmdnode.firstChildElement("server_path").attribute("id", "empty"));
  ui->LogDirLineEdit->setText(
      cmdnode.firstChildElement("log_path").attribute("id", "empty"));
  int idx = cmdnode.firstChildElement("log_level").attribute("id", "0").toInt();
  if (idx < 10)
    ui->LogLevelComboBox->setCurrentIndex(idx);
  else
    ui->LogLevelComboBox->setCurrentIndex(5);

  // Populate serial tree
  ui->SerialSetupTreeWidget->clear();
  _serialPortLut.clear();

  if (cmdnode.firstChildElement("port").isNull())
    return;
  QDomElement portelement = cmdnode.firstChildElement("port");
  while (!portelement.isNull())
  {
    SerialPort serialport;
    serialport.name = portelement.attribute("id");
    serialport.port = portelement.attribute("value");
    serialport.baud =
           portelement.firstChildElement("baud").attribute("value", "").toInt();
    serialport.parity = 
           portelement.firstChildElement("parity").attribute("value", "");
    serialport.stopbits = 
       portelement.firstChildElement("stop_bits").attribute("value", "").toFloat();
    serialport.charsize = 
         portelement.firstChildElement("char_size").attribute("value", "").toInt();
    serialport.flowctrl = 
           portelement.firstChildElement("flow_ctrl").attribute("value", "");
    serialport.timeout = 
           portelement.firstChildElement("timeout").attribute("value", "1200000").toInt() / 1000 / 60;
    serialport.protocol = 
          portelement.firstChildElement("protocol").attribute("value", "");
    _serialPortLut["Name: " + serialport.name] = serialport;

    portelement = cmdnode.nextSiblingElement("port");
  }

  if (_serialPortLut.size() == 0)
    return;

  SerialPortLut::iterator serialitor;
  for (serialitor=_serialPortLut.begin(); 
       serialitor!=_serialPortLut.end();
       serialitor++)
  {
    SerialPort serialport = serialitor->second;

    QTreeWidgetItem *item = new QTreeWidgetItem(ui->SerialSetupTreeWidget);
    item->setText(0, "Name: " + serialport.name);
    item->addChild(new QTreeWidgetItem(item, 
            QStringList("Port: " + serialport.port)));
    item->addChild(new QTreeWidgetItem(item, 
            QStringList("Baud Rate: " + QString::number(serialport.baud))));
    item->addChild(new QTreeWidgetItem(item, 
            QStringList("Parity: " + serialport.parity)));
    item->addChild(new QTreeWidgetItem(item, 
            QStringList("Flow Ctrl: " + serialport.flowctrl)));
    item->addChild(new QTreeWidgetItem(item, 
            QStringList("Stop Bits: " + QString::number(serialport.stopbits))));
    item->addChild(new QTreeWidgetItem(item, 
            QStringList("Char Size: " + QString::number(serialport.charsize))));
    item->addChild(new QTreeWidgetItem(item, 
            QStringList("Timeout (mins): " + QString::number(serialport.timeout))));
    ui->SerialSetupTreeWidget->addTopLevelItem(item);
  }
}

//************************************************************************
void MainWindow::handleSetConfigButtonSlot()
{
  // Verify all input data

  if ((ui->PLIDLineEdit->text()=="") ||
      (ui->PLIDLineEdit->text()=="null") ||
      (ui->ServerAddrLineEdit->text()=="") ||
      (ui->ServerAddrLineEdit->text()=="null") ||
      (ui->ServerPathLineEdit->text()=="") ||
      (ui->ServerPathLineEdit->text()=="null") ||
      (ui->LogDirLineEdit->text()=="") ||
      (ui->LogDirLineEdit->text()=="null") || 
      (ui->SerialSetupTreeWidget->topLevelItemCount()==0))
  {
    handleError("Please fill out all fields", true);
    return;
  }

  // Form command xml

  _commandXML = "";
  setClearConfig();
  setPOSAppId(ui->PLIDLineEdit->text().trimmed());
  setServerInfo(ui->ServerAddrLineEdit->text().trimmed(), 
                ui->ServerPathLineEdit->text().trimmed(),
                80);
  setLogInfo(ui->LogDirLineEdit->text().trimmed(),
             ui->LogLevelComboBox->currentIndex());

  SerialPortLut::iterator serialitor;
  for (serialitor=_serialPortLut.begin(); 
       serialitor!=_serialPortLut.end();
       serialitor++)
  {
    SerialPort serialport = serialitor->second;
    SetAddSerial(serialport.name, serialport.port, serialport.baud,
                 serialport.parity, serialport.stopbits, serialport.charsize,
                 serialport.flowctrl, serialport.protocol);
  }

  // Display wait box and send config to pos app
  displayWaitBox("Please wait, setting configuration", 20000, 
                 "Setting configuration failed");
  sendConfig();
}

//************************************************************************
void MainWindow::setClearConfig()
{
  _commandXML += "<command id='clear_config'/>";
}

//************************************************************************
void MainWindow::setPOSAppId(const QString &plid)
{
  _commandXML += QString("<command id='set_pos_app_id'>"
                         "<pos_location id='%1'/>"
                         "</command>").arg(plid);
}

//************************************************************************
void MainWindow::setServerInfo(const QString &serveraddr,
                               const QString &serverpath, int serverport)
{
  _commandXML += QString("<command id='set_server_info'>"
                         "<address id='%1'/>"
                         "<path id='%2'/>"
                         "<port id='%3'/>"
                         "</command>")
        .arg(serveraddr).arg(serverpath).arg(QString::number(serverport));
                        
}

//************************************************************************
void MainWindow::setLogInfo(const QString &logpath, int loglevel)
{
  _commandXML += QString("<command id='set_log_info'>"
                         "<path id='%1'/>"
                         "<level id='%2'/>"
                         "</command>")
                 .arg(logpath).arg(QString::number(loglevel));
}

//************************************************************************
void MainWindow::SetAddSerial(const QString &serialname,
                              const QString &serialport, int baud,
                              const QString &parity, float stopbits,
                              int charsize, const QString &flowctrl,
                              const QString &protocol)
{
  _commandXML += QString("<command id='add_serial'>"
                         "<port id='%1' value='%2'>"
                         "<baud value='%3'/>"
                         "<parity value='%4'/>"
                         "<stop_bits value='%5'/>"
                         "<char_size value='%6'/>"
                         "<flow_ctrl value='%7'/>"
                         "<protocol value='%8'/>"
                         "</port>"
                         "</command>")
                         .arg(serialname)
                         .arg(serialport)
                         .arg(QString::number(baud))
                         .arg(parity)
                         .arg(QString::number(stopbits))
                         .arg(QString::number(charsize))
                         .arg(flowctrl)
                         .arg(protocol);
}

//************************************************************************
void MainWindow::SetRemoveSerial(const QString &serialname)
{
  _commandXML += QString("<command id='remove_serial' name='%1'/>")
                    .arg(serialname);
}

//************************************************************************
void MainWindow::sendConfig()
{
  // If not connected, show error
  if (socket.state() != QAbstractSocket::ConnectedState)
  {
    handleError("Not connected to POS App", true);
    return;
  }

  QString sendXML = QString("<?xml version='1.0' encoding='UTF-8'?>"
                            "<pos_app_config>"
                            "%1"
                            "</pos_app_config>"
                            "<EOF>").arg(_commandXML);

  ui->DebugTextEdit->append(sendXML);

  QByteArray data(sendXML.toStdString().c_str());
  socket.write(data);
  socket.flush();
}

/////////////////////////////////////////////////////////////////////////
// MISC /////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

//************************************************************************
void MainWindow::handleError(const QString &errmsg, bool show)
{
  // Show error (1 msgbox at a time)
  if (show && !_showErrBox)
  {
    _showErrBox = true;
    QMessageBox::critical(this, tr("POS App Gui"), errmsg,
                          QMessageBox::Close);
    _showErrBox = false;
  }
}

//************************************************************************
void MainWindow::displayWaitBox(const QString &msg, int waitms, 
                                const QString &timeoutmsg)
{
  if (_waitBox != NULL)
    delete _waitBox;

  _timoutMsg = timeoutmsg;

  _waitBox = new QMessageBox(this);
  _waitBox->setWindowTitle(tr("Please wait"));
  _waitBox->setText(msg);
  _waitBox->setStandardButtons(0);
  _waitBox->setModal(true);
  Qt::WindowFlags wFlags = _waitBox->windowFlags();
  if(Qt::WindowCloseButtonHint == (wFlags & Qt::WindowCloseButtonHint))
  {
     wFlags = wFlags ^ Qt::WindowCloseButtonHint;
     _waitBox->setWindowFlags(wFlags);
  }
  _waitBox->setAttribute(Qt::WA_DeleteOnClose);
  _waitBoxTimer.start(waitms);
  connect(this, SIGNAL(ClosePleaseWaitDialog()), _waitBox, SLOT(accept()));
  connect(this, SIGNAL(ClosePleaseWaitDialog()), &_waitBoxTimer, SLOT(stop()));
  _waitBox->show();
}

//************************************************************************
void MainWindow::handleWaitBoxTimeOutSlot()
{
  _waitBoxTimer.stop();
  if (_waitBox != NULL)
  {
    _waitBox->hide();
    delete _waitBox;
    _waitBox = NULL;
    if (_timoutMsg != "")
      handleError(_timoutMsg, true);
    if (!_initConnect)
    {
      handleError("Error connecting to POS App, please try again", true);
      exit(-1);
    }
  }
}
