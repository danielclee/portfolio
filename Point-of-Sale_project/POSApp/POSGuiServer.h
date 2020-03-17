#ifndef POSGUI_SERVER
#define POSGUI_SERVER

#include <stdlib.h>
#include <vector>
#include <boost/asio.hpp>
#include <boost/asio/serial_port.hpp>
#include <regex>
#include <boost/thread.hpp>
#include "sigslot.h"

namespace POS
{
  namespace GUI
  {
    /*
     * POSGuiServer Class
     **/

    class POSGuiServer : public sigslot::has_slots<>
    {
      public:
      sigslot::signal1<std::string, multi_threaded_local>  SendPOSGuiDataSignal;
      sigslot::signal2<std::string, int, multi_threaded_local>   SendLogDataSignal;
      void ShutdownSlot(std::string sid);
      void SendGuiDataSlot(std::string socketdata);
      void SendSerialDataSlot(std::string serialdata);

      public:
      POSGuiServer(boost::asio::io_service *iosvc);
      ~POSGuiServer();
  
      void Listen();
  
      public:
      void ListenThread();
  
      protected:
      boost::asio::io_service  *_ioService;

      private:
      void waitForTcpConnection();
      void handleSocketRead();
  
      private:
      // Buffer
      std::string                                    _sendBuffer;
      // Thread
      boost::thread                                  _thread;
      // Socket stuff
      boost::asio::ip::tcp::acceptor                 _tcpAcceptor;
      boost::asio::ip::tcp::socket                   *_tcpSocket;
      // Misc
      bool                                           _running;
    };
  };
};

#endif
