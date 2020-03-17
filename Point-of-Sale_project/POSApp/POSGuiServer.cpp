#pragma warning(disable:4996) 
#pragma warning(disable:4503) 

#include <iostream>
#include <boost/algorithm/string.hpp>
#include <boost/array.hpp>
#include <boost/bind.hpp>
#include <boost/asio.hpp>
#include <chrono>
#include <boost/date_time/posix_time/posix_time.hpp>
#include "tinyxml2.h"
#include "POSGuiServer.h"

using namespace POS;
using namespace POS::GUI;
using namespace boost::asio;
using namespace boost::asio::ip;
using namespace sigslot;
using namespace tinyxml2;

/******************************************************************************
 *
 ******************************************************************************/
POSGuiServer::POSGuiServer(boost::asio::io_service *iosvc) :
  _ioService(iosvc),
  _sendBuffer(""),
  _tcpAcceptor((*iosvc), tcp::endpoint(tcp::v4(), 1800)),
  _tcpSocket(NULL),
  _running(false)
{
}

/******************************************************************************
 *
 ******************************************************************************/
POSGuiServer::~POSGuiServer()
{
}

/******************************************************************************
 *
 ******************************************************************************/
void POSGuiServer::Listen()
{
  // Run in another thread
  _thread = boost::thread(&POSGuiServer::ListenThread, this);
  _thread.detach();
}

/******************************************************************************
 *
 ******************************************************************************/
void POSGuiServer::ListenThread()
{
  // Start listening for tcp sockets

  _running = true;
  while(_running)
  {
    // Wait for inooming sockets
    tcp::socket socket((*_ioService));
    _tcpAcceptor.accept(socket);
    _tcpSocket = &socket;   // save pointer so can have member access

////    // Set socket timeouts
////
////#if defined(WIN32)
////    int32_t timeout = 15000;
////    setsockopt(socket.native(), SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof(timeout));
////    setsockopt(socket.native(), SOL_SOCKET, SO_SNDTIMEO, (const char*)&timeout, sizeof(timeout));
////#else
////    struct timeval tv;
////    tv.tv_sec  = 15; 
////    tv.tv_usec = 0;         
////    setsockopt(socket.native(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
////    setsockopt(socket.native(), SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
////#endif

    // Here we have a connection

    SendLogDataSignal("Client connected", 9);
    _sendBuffer = "";
    bool checkbyte = true;
    do
    {
      // Wait for read data
      boost::system::error_code error;
      boost::array<char, 1024> buf;
      std::size_t buflen = socket.read_some(buffer(buf, 1024), error);

      // If detect socket error, then disconnect socket

      if ((error>0))
      {
        SendLogDataSignal("Disconnecting client", 9);
        boost::system::error_code ec;
        socket.shutdown(boost::asio::ip::tcp::socket::shutdown_both, ec);
        socket.close();
        _tcpSocket = NULL;
        break;
      }

      // Check very 1st byte of connection and if not '<' then close socket

      if (checkbyte && (buflen>0))
      {
        if (buf[0] != '<')
        {
          SendLogDataSignal("Shutting down invalid connection", 9);
          boost::system::error_code ec;
          socket.shutdown(boost::asio::ip::tcp::socket::shutdown_both, ec);
          socket.close();
          break;
        }
        checkbyte = false;
      }

      // Append socket data
      std::string data(buf.begin(), buf.begin()+buflen);

      // If valid XML message, then process

      XMLDocument xmldoc;
      if (xmldoc.Parse(data.c_str()))
      {
        SendPOSGuiDataSignal(data);
        data.clear();
      }
    }
    while(socket.is_open());
  } /* End while */
}

/******************************************************************************
 *
 ******************************************************************************/
void POSGuiServer::SendGuiDataSlot(std::string socketdata)
{
  if (_tcpSocket != NULL)
  {
    // Wait 100 ms
    boost::asio::deadline_timer t((*_ioService));
    t.expires_from_now(boost::posix_time::milliseconds(100));
    boost::system::error_code ec;
    t.wait(ec);

    // Send data
    boost::system::error_code ignored_error;
    write((*_tcpSocket), boost::asio::buffer(socketdata), ignored_error);
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void POSGuiServer::SendSerialDataSlot(std::string serialdata)
{
  if (_tcpSocket == NULL)
    return;

  std::ostringstream os;
  os << "<?xml version='1.0' encoding='UTF-8'?>"
     << "<pos_serial_data>"
     << "<serial_data value='" << serialdata << "'/>"
     << "</pos_serial_data>";

  boost::system::error_code ignored_error;
  write((*_tcpSocket), boost::asio::buffer(os.str()), ignored_error);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSGuiServer::ShutdownSlot(const std::string sid)
{
  if (sid == "all")
  {
    SendLogDataSignal("GUI Server shutting down", 0);
    _running = false;
  }
}

