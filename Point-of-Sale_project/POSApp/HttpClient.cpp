#pragma warning(disable:4996) 
#pragma warning(disable:4503) 
#pragma warning(disable:4250) 

#include <iostream>
#include <boost/asio/ip/tcp.hpp>
#include <regex>
#include <boost/regex.hpp>
#include <boost/crc.hpp>  // for boost::crc_32_type
#include "HttpClient.h"
#include <fstream>

using namespace std;
using namespace boost;
using namespace boost::asio;
using namespace POS;
using namespace POS::HTTP;

/******************************************************************************
 * CTOR - TEST ONLY
 ******************************************************************************/
HttpClient::HttpClient(boost::asio::io_service *iosvc) :
  _ioService(iosvc),
  _serverAddress(""),
  _serverPath(""),
  _serverPort(80)
{
}

/******************************************************************************
 * CTOR
 ******************************************************************************/
HttpClient::HttpClient(boost::asio::io_service *iosvc, 
                       const std::string &serveraddr,
                       const std::string &serverpath, 
                       const int serverport) : 
  _ioService(iosvc),
  _serverAddress(serveraddr),
  _serverPath(serverpath),
  _serverPort(serverport)
{
}

/******************************************************************************
 *
 *******************************************************************************/
int HttpClient::SendPOSData(const std::string &uuid,
                             const std::string &postdata)
{
  try
  {
#ifdef POSDEBUGGING
    printf("\nDEBUG POST : %s\n", postdata.c_str());
    return(1);
#endif

    // Setup http connection
    
    boost::asio::ip::tcp::iostream s(_serverAddress, "http");
    if (!s)
    {
      return(0);
    }

    // Create/send POST command

    s << "POST " << _serverPath << " HTTP/1.1\r\n"
      << "Host: " << _serverAddress << "\r\n"
      << "Cache-Control: max-age=0\r\n"
      << "Accept: */*\r\n"
      << "Accept-Encoding: gzip,deflate,sdch\r\n"
      << "Accept-Language: en-US,en;q=0.8\r\n"
      << "Connection: close\r\n" 
      << "Content-Type: application/x-www-form-urlencoded\r\n"
      << "Content-Length: " << postdata.length() << "\r\n\r\n"
      << postdata 
      << std::flush;

    // Scrape web page

    int poststatus = -9;
    for( std::string line; getline(s, line); )
    {
      SendLogDataSignal(line, 9);

      if (line.find("[" + uuid + "]") != string::npos)
      {
        poststatus = 1;
        break;
      }
      else if (line.find("[-1]") != string::npos)
      {
        poststatus = -1;
        break;
      }
      else if (line.find("[-2]") != string::npos)
      {
        poststatus = -2;
        break;
      }
      else if (line.find("[-3]") != string::npos)
      {
        poststatus = -3;
        break;
      }
      else if (line.find("[-4]") != string::npos)
      {
        poststatus = -4;
        break;
      }
    }

    return(poststatus);
  }
  catch (std::exception& e)
  {
    std::cout << "SendPOSData() - Exception: " << e.what() << "\n";
  }

  return(0);
}

/******************************************************************************
 *
 *******************************************************************************/
void HttpClient::SendError(const std::string &plid, int errorcode, 
                           const std::string &errormsg)
{
  try
  {
#ifdef POSDEBUGGING
    printf("\nERROR POST : %s\n", errormsg.c_str());
    return;
#endif

    // Setup http connection
    
    boost::asio::ip::tcp::iostream s(_serverAddress, "http");
    if (!s)
      return;

    // Create POST command

    std::string tmpplid = plid;
    tmpplid = std::regex_replace(tmpplid, std::regex("[\\%]"), "%25");
    tmpplid = std::regex_replace(tmpplid, std::regex("[&]"), "%26");
    tmpplid = std::regex_replace(tmpplid, std::regex("[=]"), "%3d");
    tmpplid = std::regex_replace(tmpplid, std::regex("[?]"), "%3f");
    tmpplid = std::regex_replace(tmpplid, std::regex("[$]"), "%24");
    tmpplid = std::regex_replace(tmpplid, std::regex("[+]"), "%2b");
    tmpplid = std::regex_replace(tmpplid, std::regex("[,]"), "%2c");
    tmpplid = std::regex_replace(tmpplid, std::regex("[/]"), "%2f");
    tmpplid = std::regex_replace(tmpplid, std::regex("[:]"), "%3a");
    tmpplid = std::regex_replace(tmpplid, std::regex("[;]"), "%3b");
    tmpplid = std::regex_replace(tmpplid, std::regex("[@]"), "%40");
    tmpplid = std::regex_replace(tmpplid, std::regex("[#]"), "%23");
    tmpplid = std::regex_replace(tmpplid, std::regex("[ ]"), "%20");
    tmpplid = std::regex_replace(tmpplid, std::regex("[<]"), "");
    tmpplid = std::regex_replace(tmpplid, std::regex("[>]"), "");
    tmpplid = std::regex_replace(tmpplid, std::regex("[[]"), "%5b");
    tmpplid = std::regex_replace(tmpplid, std::regex("[\\\\]"), "%5d");
    tmpplid = std::regex_replace(tmpplid, std::regex("[{]"), "%7b"); 
    tmpplid = std::regex_replace(tmpplid, std::regex("[}]"), "%7d"); 
    tmpplid = std::regex_replace(tmpplid, std::regex("[|]"), "%7c");
    tmpplid = std::regex_replace(tmpplid, std::regex("[\\]]"), "%5c");
    tmpplid = std::regex_replace(tmpplid, std::regex("[\\^]"), "%5e"); 
    std::string tmpperrmsg = errormsg;
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[\\%]"), "%25");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[&]"), "%26");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[=]"), "%3d");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[?]"), "%3f");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[$]"), "%24");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[+]"), "%2b");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[,]"), "%2c");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[/]"), "%2f");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[:]"), "%3a");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[;]"), "%3b");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[@]"), "%40");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[#]"), "%23");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[ ]"), "%20");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[<]"), "");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[>]"), "");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[[]"), "%5b");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[\\\\]"), "%5d");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[{]"), "%7b"); 
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[}]"), "%7d"); 
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[|]"), "%7c");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[\\]]"), "%5c");
    tmpperrmsg = std::regex_replace(tmpperrmsg, std::regex("[\\^]"), "%5e"); 

    ostringstream os;
    os << "plid=" << tmpplid << "&errcode=" << errorcode 
       << "&errmsg=" << tmpperrmsg;
    std::string errpost = os.str();

    // Send POST command

    s << "POST " << _serverPath << " HTTP/1.1\r\n"
      << "Host: " << _serverAddress << "\r\n"
      << "Cache-Control: max-age=0\r\n"
      << "Accept: */*\r\n"
      << "Accept-Encoding: gzip,deflate,sdch\r\n"
      << "Accept-Language: en-US,en;q=0.8\r\n"
      << "Connection: close\r\n" 
      << "Content-Type: application/x-www-form-urlencoded\r\n"
      << "Content-Length: " << errpost.length() << "\r\n\r\n"
      << errpost
      << std::flush;
  }
  catch (std::exception& e)
  {
    std::cout << "SendError() - Exception: " << e.what() << "\n";
  }

  return;
}



/******************************************************************************
 *
 ******************************************************************************/
void HttpClient::TestPost()
{
  try
  {
    boost::asio::ip::tcp::iostream s("96.251.22.3", "http");
    if (!s)
    {
      std::cout << "Could not connect to 96.251.22.3\n";
      return;
    }

    std::cout << "WOOOHOOOO\n";
    fflush(stdout);

    std::string data = "ptid=1&uuid=3&eid=1&sid=1&tid=1&date=07302014&time=230000&descr=Swisher Sweets 12 pack&price=5.55&tax=t&misc=damn good shit&gid=1&lid=1&pid=1";
    boost::crc_32_type crc32;
    crc32.process_bytes(data.c_str(), data.length());
    ostringstream os;
    os << data << "&crc32=" << std::hex << std::nouppercase << crc32.checksum();

    std::cout << "HttpClient CHECKSUM : " << std::hex << std::nouppercase
              << crc32.checksum() << std::endl;

    s << "POST /pts_2013/pos/ HTTP/1.1\r\n"
      << "Host: 96.251.22.3\r\n"
      << "Cache-Control: max-age=0\r\n"
      << "Accept: */*\r\n"
      << "Accept-Encoding: gzip,deflate,sdch\r\n"
      << "Accept-Language: en-US,en;q=0.8\r\n"
      << "Connection: close\r\n" 
      << "Content-Type: application/x-www-form-urlencoded\r\n"
      << "Content-Length: " << os.str().length() << "\r\n\r\n"
      << os.str();

    for(std::string line; getline(s, line); )
    {
      std::cout << line << std::endl;
      fflush(stdout);
    }
  }
  catch (std::exception& e)
  {
    std::cout << "TestPost() - Exception: " << e.what() << "\n";
  }
}
