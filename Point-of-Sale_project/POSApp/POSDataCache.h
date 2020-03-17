#ifndef POS_DATA_CACHE
#define POS_DATA_CACHE

#include <vector>
#include <boost/thread.hpp>
#include "sigslot.h"
extern "C"
{
  #include "sqlite3.h"
}

namespace POS
{
  class POSDataCache : public sigslot::has_slots<>
  {
    public:
    void CacheDataSlot(std::string data);
    void ShutdownSlot(std::string sid);
    void CleanupSlot();

    public:
    void RunThread();

    public:
    POSDataCache();
    ~POSDataCache();
    void RunDetachedThread();
    bool OpenDataCache(const std::string &file);
    void CloseDataCache();
    bool RunSQLCmd(const std::string &sqlcmd);

    private:
    // database
    sqlite3             *_dbDataCache;
    // thread
    boost::thread       _thread;
    // misc
    bool                _running;
  };
}

#endif
