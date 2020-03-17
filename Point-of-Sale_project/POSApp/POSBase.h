#ifndef POS_BASE
#define POS_BASE

#include <stdlib.h>
#include <map>
#include <queue>
#include <time.h>
#include <boost/bind.hpp>
#include <boost/program_options.hpp>
#include <boost/log/trivial.hpp>
#include "NucleusSerialPort.h"
#include "HttpClient.h"
#include "POSGuiServer.h"
#include "POSLogNode.h"
extern "C"
{
  #include "sqlite3.h"
}

namespace POS
{
  class POSBase : public sigslot::has_slots<>
  {
    public:
    enum POSType
    {
      POS_UNKNOWN,
      POS_NUCLEUS,
    };

    protected:
    enum CacheMode
    {
      CACHE_EMBEDDED,  // write to hd as little as possible
      CACHE_POWERHIT,
    };

    struct SerialData
    {
      std::string id;
      long        uuid;
      std::vector<std::string> matches;
    };

    enum SQLCmdType
    {
      SQL_NONE,
      SQL_CREATE_TABLE,
      SQL_INSERT,
      SQL_SELECT,
      SQL_DELETE,
      SQL_COUNT,
    };
    
    public:
    static int SqlCmdCallback(void *data, int argc, char **argv, 
                              char **azColName);
    virtual int ProcessPOSDBData(int argc, char **argv, char **azColName);

    public:
    sigslot::signal1<std::string, multi_threaded_local>  SendShutdownSignal;
    sigslot::signal1<std::string, multi_threaded_local>  SendGuiDataSignal;
    sigslot::signal2<std::string, int, multi_threaded_local>  SendLogDataSignal;
    sigslot::signal1<std::string, multi_threaded_local>  SendSerialDataSignal;

    public:
    void ReceivePOSDataSlot(std::string sid, std::smatch matches);
    void ReceivePOSGuiDataSlot(std::string data);
    void ReceiveSerialTimeoutSlot(std::string sid);

    private:
    typedef std::map<std::string, SerialPort*> SerialPortLut;

    public:
    POSBase(boost::asio::io_service *iosvc);
    virtual ~POSBase();
    bool StartApp();
    void LoadConfig();
    // SIM stuff
    virtual void RunPOSSim(const std::string &file, 
                           const std::string &serial,
                           size_t iterations) = 0;
    virtual void RunPOSSim(boost::program_options::variables_map &vmap) = 0;
    // Serial/protocol stuff
    void ClearSerialLut();
    virtual void AddConnection(const std::string &sid, 
                               const std::string &port,
                               const unsigned int &baud,
                               const char flow,
                               const char parity,
                               const float stop,
                               const unsigned int char_size,
                               const int timeout,
                               POSType postype);
    void RemoveConnection(const std::string &sid);
    void AddParsingExpression(const std::string &sid, std::regex e);
    void CloseSerial(const std::string &sid="");
    bool Listen(const std::string &sid);
    // SQL stuff
    inline void SetSQLType(SQLCmdType val) {_sqlCmdType = val;};
    inline SQLCmdType GetSQLType() {return(_sqlCmdType);};
    inline void SetDBCacheKount(unsigned int val) {_dbDataCacheKount=val;};
    
    // HTTP stuff
    void SetHttpInfo(const std::string &ip, const std::string &dir,
                     const int port=80);
    // GUI stuff
    void StartLogNode();
    void StartGUIServer();
    
    protected:
    virtual void SetDefaultParsingExpression(
                std::vector<std::regex> &regexvec) = 0;  // called add conn
    virtual int ProcessPOSData(SerialData &sdata);
    virtual std::string EncodePostData(SerialData &sdata) = 0;

    protected:
    bool createSQLDB();
    bool ExecuteSQLStatement(const std::string &sqlcmd, SQLCmdType type);
    void serialDataQTimeoutHandler(const boost::system::error_code& error);
    virtual void CachePOSData(const unsigned int uuid, const std::string &data);
    virtual void ProcessCachedPOSData();        

    private:
    void startHangCheckThread();
    void handleUnsendableData(std::string data);

    protected:
    // io service
    boost::asio::io_service  *_ioService;
    // thread objects
    SerialPortLut    _serialPortLut;
    POS::HTTP::HttpClient _httpClient;
    POS::GUI::POSGuiServer  _guiServer;
    POS::LOG::POSLogNode    _logNode;
    // database and cache
    std::queue<SerialData>       _serialDataQ;
    boost::asio::deadline_timer  _serialDataQTimer;
    int                          _serialDataQTimeout;
    sqlite3                      *_dbDataCache;
    unsigned int                 _dbDataCacheKount;
    unsigned int                 _sqlErrorKount;
    SQLCmdType                   _sqlCmdType;
    CacheMode                    _cacheMode;
    std::string                  _currentProcessUUID;
    // misc
    bool _listening;
    std::string _logPath;
    int         _logLevel;
    std::string _groupId;
    std::string _locId;
    std::string _posLocationId;
    std::time_t _dbSendErrorTimeStamp;
    std::time_t _posSendErrorTimeStamp;
    unsigned int  _posDataRetryKount;
  };
}

#endif
