#pragma warning(disable:4996) 
#pragma warning(disable:4503) 
#pragma warning(disable:4250) 

#include "POSDataCache.h"

using namespace std;
using namespace POS;

/******************************************************************************
 * CTOR
 ******************************************************************************/
POSDataCache::POSDataCache() :
  _dbDataCache(NULL),
  _running(true)
{
printf("##################### STARTING DATA CACHE\n");
fflush(stdout);
}

/******************************************************************************
 * DTOR
 ******************************************************************************/
POSDataCache::~POSDataCache()
{
  printf("#################################### DTOR 1111111111\n");
  fflush(stdout);
}

/******************************************************************************
 * RunDetachedThread
 ******************************************************************************/
void POSDataCache::RunDetachedThread()
{
  // Run in another thread
  _thread = boost::thread(&POSDataCache::RunThread, this);
  _thread.detach();
}

/******************************************************************************
 * StoreDataSlot
 ******************************************************************************/
void POSDataCache::CacheDataSlot(std::string data)
{
  printf("#################################### CACHE DATA SLOT\n");
  fflush(stdout);
}

/******************************************************************************
 * CleanupSlot
 ******************************************************************************/
void POSDataCache::CleanupSlot()
{
}

/******************************************************************************
 * RunSQLCmd
 ******************************************************************************/
bool POSDataCache::RunSQLCmd(const std::string &sqlcmd)
{
  return(false);
}

/******************************************************************************
 * RunThread
 ******************************************************************************/
void POSDataCache::RunThread()
{
  while (_running)
  {

  }
}

/******************************************************************************
 * ShutdownSlot
 ******************************************************************************/
void POSDataCache::ShutdownSlot(std::string sid)
{
  printf("Data cache shutting down\n");
  _running = false;
}
