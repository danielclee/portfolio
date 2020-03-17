#ifndef POS_LOG_NODE
#define POS_LOG_NODE

#include <stdlib.h>
#include <queue>
#include <boost/asio.hpp>
#include <boost/thread.hpp>
#include "sigslot.h"
#include "HttpClient.h"

namespace POS
{
  namespace LOG
  {
    /*
     * POSLogNode Class
     **/

    class POSLogNode : public sigslot::has_slots<>
    {
      public:
      void ShutdownSlot(std::string sid);
      void LogDataSlot(std::string logdata, int level);
      void SetLogSettings(std::string dir, int level);

      public:
      POSLogNode(boost::asio::io_service *iosvc);
      POSLogNode(boost::asio::io_service *iosvc,
                 const std::string &logdir, int loglevel=0);
      ~POSLogNode();

      inline void SetLogDir(const std::string &logdir) {_logDir=logdir;};
      inline void SetLogLevel(int loglvl) {_logLevel=loglvl;};
      inline void SetLocationID(const std::string &plid) {_plid=plid;};
      void SetServerInfo(const std::string &saddress, 
                         const std::string &spath,
                         int sport);
      void Listen();

      private:
      void PostError(int errorcode, const std::string &errormsg);
  
      public:
      void ListenThread();
  
      private:
      boost::asio::io_service  *_ioService;
      // Thread
      boost::thread       _thread;
      POS::HTTP::HttpClient _httpClient;
      // Log
      std::string         _logDir;
      int                 _logLevel;
      // Misc
      bool                _running;
      // POS location ID
      std::string         _plid;
    };
  };
};

#endif
