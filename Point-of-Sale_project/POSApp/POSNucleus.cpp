#include <climits>
#include <fstream>
#include <boost/algorithm/string.hpp>
#include <boost/crc.hpp>  // for boost::crc_32_type
#include <chrono>
#include <thread>
#include <boost/date_time/posix_time/posix_time.hpp>
#include "POSNucleus.h"

using namespace POS;

/******************************************************************************
 *
 ******************************************************************************/
POSNucleus::POSNucleus(boost::asio::io_service *iosvc) :
  POSBase(iosvc)
{
}

/******************************************************************************
 *
 ******************************************************************************/
POSNucleus::POSNucleus(boost::asio::io_service *iosvc, 
                       const std::string &logdir) :
  POSBase(iosvc)
{
  _logDir = logdir;
}

/******************************************************************************
 *
 ******************************************************************************/
void POSNucleus::SetDefaultParsingExpression(std::vector<std::regex> &regexvec)
{
  // Nucleus protocol
  // NUCLEUS_POS_EMPLOYEE    0 
  // NUCLEUS_POS_SHIFT       4
  // NUCLEUS_POS_TERMINAL    8
  // NUCLEUS_POS_TIMESTAMP   12
  // NUCLEUS_POS_DESC_START  28
  // NUCLEUS_POS_DESC_END    68
  // NUCLEUS_POS_PRICE       70
  
  // 4 bytes: employee id (int)
  // 4 bytes: shift id    (int)
  // 4 bytes: terminal id (int)
  // 16 bytes: time stamp (systemtime)
  // 40 bytes: text description
  // 1 byte: null character
  // 8 bytes: price (double)

  // Nucleus example

  // Type 1
  //e3s1t2   08/19/03 18:07:50
  //12qt coole                       0.00T

  // Type 2
  //e3s1t2   08/19/03 18:07:50
  //TRANSACTION ID#000001

  // Type 3
  // e21s552t1 10/21/14 12:09:48 Credit: Old Price $3.639, New Price $3.599 

  regexvec.push_back(std::regex("\\s*[e](\\d{1,3})[s](\\d{1,3})[t](\\d{1,3})\\s*(\\d{1,2}/\\d{1,2}/\\d{1,2}|\\d{4})\\s*(\\d{1,2}[:]\\d{2,}[:]\\d{2})\\s*(.{30,31}\\s*)(\\d{1,3}[.]\\d{2})([T]*)\\s+"));
  regexvec.push_back(std::regex("\\s*[e](\\d{1,3})[s](\\d{1,3})[t](\\d{1,3})\\s*(\\d{1,2}/\\d{1,2}/\\d{1,2}|\\d{4})\\s*(\\d{1,2}[:]\\d{2,}[:]\\d{2})\\n+(.{1,38})\\n+"));
  regexvec.push_back(std::regex("\\s*[e](\\d{1,3})[s](\\d{1,3})[t](\\d{1,3})\\s*(\\d{1,2}/\\d{1,2}/\\d{1,2}|\\d{4})\\s*(\\d{1,2}[:]\\d{2,}[:]\\d{2})\\s*(.{30,55})(?=\\s*e\\d{1,3})"));
}

/******************************************************************************
 *
 ******************************************************************************/
void POSNucleus::AddConnection(const std::string &sid, 
                               const std::string &port,
                               const unsigned int &baud,
                               const char flow,
                               const char parity,
                               const float stop,
                               const unsigned int char_size,
                               const int timeout,
                               POSType postype)
{
  POSBase::AddConnection(sid, port, baud, flow, parity, stop, char_size, 
                         timeout, POS_NUCLEUS);
}

/******************************************************************************
 *
 ******************************************************************************/
std::string POSNucleus::EncodePostData(SerialData &sdata)
{
  // Need to have at least 7 matches (0-based) otherwise have bad data
  // and need to log

  if (sdata.matches.size() < 7)
  {
    SendLogDataSignal("Matches array size not correct (" + sdata.matches[0] + ")", -1);
    return("");
  }

  // Process regex matches

  std::ostringstream postdata;
  std::ostringstream encodedpostdata;
  postdata << "uuid="  << sdata.uuid
           << "&eid="   << sdata.matches[1] << "&sid="   << sdata.matches[2]
           << "&tid="   << sdata.matches[3] << "&date="  << sdata.matches[4] 
           << "&time="  << sdata.matches[5] << "&descr=" ;
  encodedpostdata << "uuid="  << sdata.uuid
                  << "&eid="   << sdata.matches[1] << "&sid="   << sdata.matches[2]
                  << "&tid="   << sdata.matches[3] << "&date="  << sdata.matches[4] 
                  << "&time="  << sdata.matches[5] << "&descr=" ;
  
  // Encode what needs to be encoded

  std::string description = sdata.matches[6];
  boost::algorithm::trim(description);
  std::string encodeddescription = description;
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[\\%]"), "%25");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[&]"), "%26");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[=]"), "%3d");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[?]"), "%3f");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[$]"), "%24");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[+]"), "%2b");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[,]"), "%2c");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[/]"), "%2f");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[:]"), "%3a");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[;]"), "%3b");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[@]"), "%40");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[#]"), "%23");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[ ]"), "%20");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[<]"), "");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[>]"), "");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[[]"), "%5b");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[\\\\]"), "%5d");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[{]"), "%7b"); 
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[}]"), "%7d"); 
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[|]"), "%7c");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[\\]]"), "%5c");
  encodeddescription = std::regex_replace(encodeddescription, std::regex("[\\^]"), "%5e"); 
  postdata << description;
  encodedpostdata << encodeddescription;

  // Process remaining regex matches
  // Note : from this point, post data and encoded post data will be different

  if (sdata.matches.size() >= 8)
  {
    postdata << "&price=" << sdata.matches[7];
    encodedpostdata << "&price=" << sdata.matches[7];
  }
  else
  {
    postdata << "&price=0.00";
    encodedpostdata << "&price=0.00";
  }

  if (sdata.matches.size() >= 9)
  {
    postdata << "&tax=" << (sdata.matches[8]=="T"?"Y":"N");
    encodedpostdata << "&tax=" << (sdata.matches[8]=="T"?"Y":"N");
  }
  postdata << "&plid=" << _posLocationId << "&pid=" << sdata.matches[3];
  encodedpostdata << "&plid=" << _posLocationId << "&pid=" << sdata.matches[3];

  postdata << "&misc=";   // for future use
  encodedpostdata << "&misc=";   // for future use
  
  // Setup CRC32

  boost::crc_32_type crc32;
  crc32.process_bytes(postdata.str().c_str(), postdata.str().length());
  encodedpostdata << "&crc32=" << std::hex << std::nouppercase << crc32.checksum();

  return(encodedpostdata.str());
}

/******************************************************************************
 *
 ******************************************************************************/
void POSNucleus::RunPOSSim(boost::program_options::variables_map &vmap)
{
  // Get serial port name

  if (!vmap.count("serial"))
  {
    std::cerr << "Need to provide a serial port" << std::endl; 
    exit(-1);
  }
  std::vector<std::string> serialnamevec =
                       vmap["serial"].as< std::vector<std::string> >();
  std::string serialname = serialnamevec[0];

  // Get sim test file

  if (!vmap.count("sim_file"))
  {
    std::cerr << "Need to specify a test file" << std::endl; 
    exit(-1);
  }
  std::vector<std::string> filenamevec =
                   vmap["sim_file"].as< std::vector<std::string> >();
  std::string filename = filenamevec[0];

  // Get iterations
  if (!vmap.count("iterations"))
  {
    std::cerr << "Need to specify # of iterations" << std::endl; 
    exit(-1);
  }
  int iterations = vmap["iterations"].as<int>();

  // Run sim
  RunPOSSim(filename, serialname, iterations);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSNucleus::RunPOSSim(const std::string &file,  
                           const std::string &serial,
                           size_t iterations)
{
  printf("Simulator mode activated on serial (%s)\n", serial.c_str());

  // Open POS data file

  std::ifstream testfile(file);
  if (!testfile.is_open())
  {
    printf("Opening %s failed\n", file.c_str());
    exit(-1);
  }

  // Read in POS test file

  std::vector<char>  buffervec;
  typedef std::istreambuf_iterator<char> buf_iter;
  for(buf_iter i(testfile), e; i != e; ++i)
  {
    char c = *i;
    buffervec.push_back(c);
  }
  testfile.close();

  // Open serial port

  boost::asio::io_service  iosvc;
  POS::SerialPort testsp(iosvc, "test", serial, 9600,
                         boost::asio::serial_port_base::flow_control::none,
                         boost::asio::serial_port_base::parity::none,
                         boost::asio::serial_port_base::stop_bits::one, 8, 300000);
  testsp.Open();

  // Stream data through serial port

  size_t loopkount = 0;
  do 
  {
    boost::asio::deadline_timer t(iosvc);
    for (size_t i=0; i<buffervec.size(); i++)
    {
      printf("Sending char to serial : (0x%0.2X,%c)\n", buffervec[i],buffervec[i]);
      testsp.Write(buffervec[i]);

      if (buffervec[i] == '\n')
      {
        t.expires_from_now(boost::posix_time::milliseconds(500));
        boost::system::error_code ec;
        t.wait(ec);
      }
    }

    if (iterations > 0)
    {
      loopkount++;
      if (loopkount >= iterations)
        break;
    }
  } 
  while(1);
  testsp.Close();

  // Wait for a 60 seconds

  boost::asio::deadline_timer t(iosvc);
  t.expires_from_now(boost::posix_time::seconds(60));
  boost::system::error_code ec;
  t.wait(ec);
}

