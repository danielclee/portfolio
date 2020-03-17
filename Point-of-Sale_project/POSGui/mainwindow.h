#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QMessageBox>
#include <QTcpSocket>
#include <QDomNode>
#include <QPointer>
#include <QTimer>
#include <map>

namespace Ui 
{
  class MainWindow;
  class AddSerialDialog;
}

class MainWindow : public QMainWindow
{
  Q_OBJECT

  private:
  struct SerialPort
  {
    QString name;
    QString port;
    int baud;
    QString parity;
    float stopbits;
    int charsize;
    QString flowctrl;
    int timeout;
    QString protocol;
  };
  typedef std::map<QString, SerialPort>    SerialPortLut;

  public:
  explicit MainWindow(QWidget *parent = 0);
  ~MainWindow();

  private:
  // raw serial data
  void handleSerialData(const QString &data);
  // xml config
  void setClearConfig();
  void setPOSAppId(const QString &plid);
  void setServerInfo(const QString &serveraddr, const QString &serverpath,
                int serverport);
  void setLogInfo(const QString &logpath, int loglevel);
  void SetAddSerial(const QString &serialname, const QString &serialport,
                    int baud, const QString &parity, float stopbits,
                    int charsize, const QString &flowctrl,
                    const QString &protocol);
  void SetRemoveSerial(const QString &serialname);
  void sendConfig();
  void getConfig();
  // gui
  void updatePOSGui(const QString &configxml);
  // xml
  void ProcessPOSAppConfigReply(QDomNode cmdnode);
  void ProcessPOSAppSerialData(QDomNode cmdnode);
  // socket
  void reconnect();
  // misc
  void handleError(const QString &errmsg, bool show);
  void displayWaitBox(const QString &msg, int waitms, 
                      const QString &timeoutmsg="");
  
  private:
  Ui::MainWindow *ui;
  Ui::AddSerialDialog *addserialui;
  QTcpSocket  socket;
  QTimer      _checkSocketTimer;
  QTimer      _waitBoxTimer;
  QString     _commandXML;
  SerialPortLut _serialPortLut;
  QPointer<QMessageBox>  _waitBox;
  QString _timoutMsg;
  bool _showErrBox;
  QByteArray _socketBuffer;
  bool _initConnect;
  
  signals:
  void CloseAddSerialDialog();
  void ClosePleaseWaitDialog();
 
  private slots:
  // init
  void StartAppSlot();
  // gui
  void handleSetConfigButtonSlot();
  void handleGetConfigButtonSlot();
  void handleAddSerialButtonSlot();
  void handleDeleteSerialButtonSlot();
  void handleASDAddSerialButtonSlot();
  void handleASDProtocolComboBoxSlot(const QString &text);
  void handleWaitBoxTimeOutSlot();
  // sockets
  void handleSocketStateChangedSlot(
                     QAbstractSocket::SocketState socketState);
  void handleCheckSocketTimerSlot();
  void SocketConnectedSlot();
  void SocketDisconnectedSlot();
  void SocketReadyReadSlot();
  void SocketErrorSlot();
};

#endif // MAINWINDOW_H
