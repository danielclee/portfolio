#ifndef HTTP_CLIENT
#define HTTP_CLIENT

#include <boost/asio.hpp>
#include "sigslot.h"

namespace POS
{
  namespace HTTP
  {
    class HttpClient
    {
      public:
      sigslot::signal2<std::string, int, sigslot::multi_threaded_local>  SendLogDataSignal;
      sigslot::signal1<std::string>  CacheDataSignal;
  
      public:
      HttpClient(boost::asio::io_service *iosvc);
      HttpClient(boost::asio::io_service *iosvc, const std::string &serveraddr,
                 const std::string &serverpath, const int serverport);
      inline void SetServerAddress(const std::string &addr){_serverAddress=addr;};
      inline void SetServerPath(const std::string &path) {_serverPath=path;};
      inline void SetServerPort(int port) {_serverPort=port;};
      inline std::string GetServerAddress()  {return(_serverAddress);};
      inline std::string GetServerPath()  {return(_serverPath);};
      inline int GetServerPort()  {return(_serverPort);};
  
      void TestPost();
      int SendPOSData(const std::string &uuid, 
                      const std::string &postdata);
      void SendError(const std::string &plid, int errorcode, 
                     const std::string &errormsg);
  
      protected:
      boost::asio::io_service  *_ioService;
      std::string  _serverAddress;
      std::string  _serverPath;
      int          _serverPort;
    };
  }
}

#endif
