#pragma warning(disable:4996) 
#pragma warning(disable:4503) 

#include <iostream>
#include <fstream>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <chrono>
#include <ctime>
#ifdef _WIN32
  #include <direct.h>
#else
  #include <unistd.h>
#endif
#include <boost/date_time/posix_time/posix_time.hpp>
#include "POSLogNode.h"

using namespace POS;
using namespace POS::LOG;
using namespace sigslot;

/******************************************************************************
 *
 ******************************************************************************/
POSLogNode::POSLogNode(boost::asio::io_service *iosvc) :
  _ioService(iosvc),
  _httpClient(iosvc),
  _logDir(""),
  _logLevel(0),
  _running(false),
  _plid("")
{
}

/******************************************************************************
 *
 ******************************************************************************/
POSLogNode::POSLogNode(boost::asio::io_service *iosvc,
                       const std::string &logdir, int loglevel) :
  _ioService(iosvc),
  _httpClient(iosvc),
  _logDir(logdir),
  _logLevel(loglevel),
  _running(false),
  _plid("")
{
}

/******************************************************************************
 *
 ******************************************************************************/
POSLogNode::~POSLogNode()
{
}

/******************************************************************************
 *
 ******************************************************************************/
void POSLogNode::SetServerInfo(const std::string &saddress, 
                               const std::string &spath, int sport)
{
  _httpClient.SetServerAddress(saddress);
  _httpClient.SetServerPath(spath);
  _httpClient.SetServerPort(80);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSLogNode::SetLogSettings(std::string dir, int level)
{
  _logDir = dir;
  _logLevel = level;

////#if defined(WIN32)
////  _chdir(_logDir.c_str());
////#else
////  chdir(_logDir.c_str());
////#endif
}

/******************************************************************************
 *
 ******************************************************************************/
void POSLogNode::Listen()
{
  // Run in another thread
  _thread = boost::thread(&POSLogNode::ListenThread, this);
  _thread.detach();
}

/******************************************************************************
 *
 ******************************************************************************/
void POSLogNode::ListenThread()
{
  boost::asio::deadline_timer t((*_ioService));
  _running = true;
  while(_running)
  {
    // Sleep 1000 ms
    t.expires_from_now(boost::posix_time::milliseconds(1000));
    boost::system::error_code ec;
    t.wait(ec);
  } /* End while */
}

/******************************************************************************
 *
 ******************************************************************************/
void POSLogNode::PostError(int errorcode, const std::string &errormsg)
{
  try
  {
    _httpClient.SendError(_plid, errorcode, errormsg);
  }
  catch (...)
  {
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void POSLogNode::LogDataSlot(std::string logdata, int level)
{
  switch (level)
  { 
    case -1: case 0:
      PostError(level, logdata);
      break;

    default: 
      if (level > _logLevel)
        return;
      break;
  };

  printf("%s\n", logdata.c_str());
  std::string logdir = _logDir;
  if (_logDir == "")
  {
#if defined(WIN32)
    logdir = "C:\\POSApp\\";
#else
    logdir = "./";
#endif
  }

  // Make sure directory exists

  if (!boost::filesystem::exists(logdir))
  {
    boost::filesystem::path dir(logdir);
    if (!boost::filesystem::create_directory(dir))
    {
      printf("Error creating log directory : %s\n", logdir.c_str());
      PostError(-1, "Error creating log directory : " + logdir);
    }
  }

  // Get current time
  time_t currtime = time(NULL);
  tm *ltime = localtime(&currtime);

  // Log data

  std::ofstream file;
  file.open(logdir + "POSApp.log", std::ios_base::app);
  if (file.is_open())
  {
    file << "[" 
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_mon << "-"
         << std::setfill('0') << std::setw(2) << ltime->tm_mday << "-"
         << 1900 + ltime->tm_year << " "
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_hour << ":"
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_min << ":"
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_sec 
         << "] - " << logdata << "\n";
    file.close();
  }

  // Check file size

  try
  {
    uintmax_t fsize = boost::filesystem::file_size(logdir + "POSApp.log");
    if (fsize > 2048000)  // 2 MB
    {
      std::string oldfile = logdir + "POSApp.log";
      std::ostringstream os;
      os << logdir << "POSApp_" 
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_mon 
         << std::setfill('0') << std::setw(2) << ltime->tm_mday
         << 1900 + ltime->tm_year << "_"
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_hour
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_min
         << std::setfill('0') << std::setw(2) << 1 + ltime->tm_sec
         << ".log";
      std::string newfile = os.str();
      if (std::rename(oldfile.c_str(), newfile.c_str()) == 0)
      {
        std::ofstream file2;
        file2.open(oldfile, std::ios_base::trunc);
        file2.close();
      }
    }
  }
  catch (...)
  {
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void POSLogNode::ShutdownSlot(const std::string sid)
{
  if (sid == "all")
  {
    printf("Log node shutting down\n");
    _running = false;
  }
}

