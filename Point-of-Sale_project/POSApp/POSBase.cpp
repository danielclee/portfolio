#pragma warning(disable:4996) 
#pragma warning(disable:4503) 

#include <fstream>
#include <regex>
#include <thread>
#include <atomic>
#include <boost/bind.hpp>
#include <boost/crc.hpp>  // for boost::crc_32_type
#include <boost/property_tree/xml_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/filesystem.hpp>
#include "tinyxml2.h"
#include "POSBase.h"

using namespace std;
using namespace POS;
using namespace POS::LOG;
using namespace boost;
using namespace boost::asio;
using namespace boost::property_tree;
using namespace sigslot;
using namespace tinyxml2;

// Globals (yuck)
std::atomic_ulong RUN_KOUNTER;
std::atomic_bool HANG_CHECK_ACTIVE;

/******************************************************************************
 *
 ******************************************************************************/
POSBase::POSBase(boost::asio::io_service *iosvc) :
  _ioService(iosvc),
  _httpClient(iosvc),
  _guiServer(iosvc),
  _logNode(iosvc),
  _serialDataQTimer((*iosvc)),
  _serialDataQTimeout(100),
  _dbDataCache(NULL),
  _dbDataCacheKount(0),
  _sqlErrorKount(0),
  _sqlCmdType(SQL_NONE),
  _cacheMode(CACHE_POWERHIT),
  _currentProcessUUID(""),
  _listening(true),
  _logPath(""), 
  _logLevel(5), 
  _groupId("null"),
  _locId("null"),
  _posLocationId("null"),
  _posDataRetryKount(0)
{
#if defined(WIN32)
    _logPath = "C:\\POSApp\\";
#else
    _logPath = "./";
#endif

  RUN_KOUNTER = 0;
  HANG_CHECK_ACTIVE = false;
}

/******************************************************************************
 *
 ******************************************************************************/
POSBase::~POSBase()
{
  ClearSerialLut();
  if (_cacheMode == CACHE_POWERHIT)
    sqlite3_close(_dbDataCache);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::LoadConfig()
{
  std::string configfile = _logPath + "posconfig.xml";
  XMLDocument xmldoc;
  XMLError errcode = xmldoc.LoadFile(configfile.c_str());
  if (errcode ==  XML_NO_ERROR)
  {
    XMLPrinter printer;
    xmldoc.Accept( &printer );
    std::string xmltext = printer.CStr();
    ReceivePOSGuiDataSlot(xmltext);
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::startHangCheckThread()
{
  // C++11 magic hang checking

  if (HANG_CHECK_ACTIVE)
    return;

  std::thread([&]
  {
    HANG_CHECK_ACTIVE = true;
    unsigned long tmp = RUN_KOUNTER;
    boost::this_thread::sleep(boost::posix_time::seconds(30));
    if (tmp == RUN_KOUNTER)
      exit(-1);
    HANG_CHECK_ACTIVE = false;
  }).detach();
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// SERIAL ///////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

/******************************************************************************
 *
 ******************************************************************************/
bool POSBase::StartApp()
{
#ifdef POSDEBUGGING
  SendLogDataSignal("POSApp DEBUG version 1.3.2 (10-31-2014 11:00)", 0);
#else
  SendLogDataSignal("POSApp version 1.3.2 (10-31-2014 11:00)", 0);
#endif

  if (!boost::filesystem::exists(_logPath))
  {
    boost::filesystem::path dir(_logPath);
    if (!boost::filesystem::create_directory(dir))
    {
      printf("Error creating log directory : %s\n", _logPath.c_str());
      SendLogDataSignal("Error creating log directory : " + _logPath, -1);
      exit(-1);
    }
  }

  // If db exists get row count

  if (_cacheMode == CACHE_POWERHIT)
  {
    ifstream dbfile(_logPath + "pos.db");
    if (dbfile)
      ExecuteSQLStatement("SELECT COUNT(*) from SerialData;", SQL_COUNT);
  }

  // Start serial data Q timer
  _serialDataQTimer.expires_from_now(boost::posix_time::milliseconds(_serialDataQTimeout));
  _serialDataQTimer.async_wait(
               boost::bind(&POSBase::serialDataQTimeoutHandler,
                           this, boost::asio::placeholders::error));

  // Start hang checking
  startHangCheckThread();

  // Set initial timestamps
  time(&_dbSendErrorTimeStamp);
  time(&_posSendErrorTimeStamp);

  return(true);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::ClearSerialLut()
{
  for (SerialPortLut::iterator i=_serialPortLut.begin();
       i!=_serialPortLut.end(); i++)
  {
    delete i->second;
  }
  _serialPortLut.clear();
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::AddConnection(const std::string &sid, 
                            const std::string &port,
                            const unsigned int &baud,
                            const char flow,
                            const char parity,
                            const float stop,
                            const unsigned int char_size,
                            const int timeout,
                            POSType postype)
{
  if (_serialPortLut.find(sid) != _serialPortLut.end())
    return;

  // Set flow control option

  serial_port_base::flow_control::type  flowcontrol;
  switch (flow)
  {
    case 'h':
      flowcontrol = serial_port_base::flow_control::hardware;
      break;
    case 's':
      flowcontrol = serial_port_base::flow_control::software;
      break;
    case 'n': default:
      flowcontrol = serial_port_base::flow_control::none;
      break;
  };
    
  // Set parity option

  serial_port_base::parity::type parityoption;
  switch (parity)
  {
    case 'o':
      parityoption = serial_port_base::parity::odd;
      break;
    case 'e':
      parityoption = serial_port_base::parity::even;
      break;
    case 'n': default:
      parityoption = serial_port_base::parity::none;
      break;
  };

  // Set stop bits option

  serial_port_base::stop_bits::type stopbitsoption;
  if (stop == 1)
    stopbitsoption = serial_port_base::stop_bits::one;
  else if (stop == 1.5)
    stopbitsoption = serial_port_base::stop_bits::onepointfive;
  else if (stop == 2)
    stopbitsoption = serial_port_base::stop_bits::two;
  else
  {
    SendLogDataSignal("Set serial unrecoverable error", -1);
    throw;
  }

  // Create new serial port

  if (postype == POS_NUCLEUS)
  {
    _serialPortLut[sid] = new NucleusSerialPort((*_ioService), sid, port, 
                                                baud, flowcontrol, parityoption,
                                                stopbitsoption, char_size, 
                                                timeout);
  }
  else
  {
    _serialPortLut[sid] = new SerialPort((*_ioService), sid, port, 
                                         baud, flowcontrol, parityoption, 
                                         stopbitsoption, char_size, timeout);
  }

  // Connect signal/slots
  _serialPortLut[sid]->SendPOSDataSignal.connect(this,&POSBase::ReceivePOSDataSlot);
  _serialPortLut[sid]->SendLogDataSignal.connect(&_logNode,&POSLogNode::LogDataSlot);
  SendShutdownSignal.connect(_serialPortLut[sid], &SerialPort::ShutdownSlot);

  // Add default parsing expressions

  std::vector<std::regex> parsingvec;
  SetDefaultParsingExpression(parsingvec);
  for (size_t i=0; i<parsingvec.size(); i++)
    _serialPortLut[sid]->AddParsingExpression(parsingvec[i]);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::RemoveConnection(const std::string &sid)
{
  SerialPortLut::iterator iter = _serialPortLut.find(sid);
  if (iter != _serialPortLut.end())
  {
    SendShutdownSignal(sid);
    SerialPort *sport = iter->second;
    _serialPortLut.erase(sid);
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::AddParsingExpression(const std::string &sid, std::regex e)
{
  if (sid == "all")
  {
    for (SerialPortLut::iterator i=_serialPortLut.begin();
         i!=_serialPortLut.end(); i++)
    {
      SerialPort *sport = i->second;
      sport->AddParsingExpression(e);
    }
  }
  else
  {
    SerialPortLut::iterator iter = _serialPortLut.find(sid);
    if (iter != _serialPortLut.end())
    {
      SerialPort *sport = iter->second;
      sport->AddParsingExpression(e);
    }
  }
}

/******************************************************************************
 *
 ******************************************************************************/
bool POSBase::Listen(const std::string &sid)
{
  bool retval = false;

  SerialPortLut::iterator iter = _serialPortLut.find(sid);
  if (iter != _serialPortLut.end())
    retval = iter->second->Listen();

  return(retval);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::CloseSerial(const std::string &sid)
{
  if (sid == "")   // close all ports
  {
    for (SerialPortLut::iterator i=_serialPortLut.begin();
         i!=_serialPortLut.end(); i++)
    {
      SendShutdownSignal(i->second->GetId());
      delete i->second;
    }
    _serialPortLut.clear();
  }
  else
  {
    SerialPortLut::iterator iter = _serialPortLut.find(sid);
    if (iter != _serialPortLut.end())
    {
      SendShutdownSignal(iter->second->GetId());
      delete iter->second;
      _serialPortLut.erase(sid);
    }
  }
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// CACHE ////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

/******************************************************************************
 *
 ******************************************************************************/
bool POSBase::createSQLDB()
{
  char *errmsg = 0;

  // Open DB
  std::string dbfilepath = _logPath + "pos.db";
  int retval = sqlite3_open(dbfilepath.c_str(), &_dbDataCache);
  if(retval)
  {
    SendLogDataSignal("Can't open database: " + std::string(sqlite3_errmsg(_dbDataCache)), -1);
    _sqlErrorKount++;
    sqlite3_close(_dbDataCache);
    return(false);
  }  

  // Create SQL tables
  std::string sql = "CREATE TABLE SerialData("   \
                    "id Integer PRIMARY KEY AUTOINCREMENT NOT NULL," \
                    "uuid INT               NOT NULL," \
                    "post_data  TEXT  NOT NULL)";
  int rc = sqlite3_exec(_dbDataCache, sql.c_str(), SqlCmdCallback, 0, &errmsg);
  if (rc != SQLITE_OK)
  {
    SendLogDataSignal("SQL create table error - " + std::string(errmsg), -1);
    _sqlErrorKount++;
    sqlite3_free(errmsg);
    sqlite3_close(_dbDataCache);
    return(false);
  }

  // Close DB  
  sqlite3_close(_dbDataCache);

  return(true);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::ReceivePOSDataSlot(std::string sid, std::smatch matches)
{
  static long uuid = 0;
  uuid++;
  if (uuid > 2147483643)
    uuid = 1;

  SerialData sdata;
  sdata.id = sid;
  sdata.uuid = uuid;
  for (size_t i=0; i<matches.size(); i++)
    sdata.matches.push_back(matches[i]);
  _serialDataQ.push(sdata);

  // Send serial data to Gui
  SendSerialDataSignal(matches[0]);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::serialDataQTimeoutHandler(const boost::system::error_code& error)
{
  // Update RUN_KOUNTER and start hang checker

  static int cumulative_time = 0;
  cumulative_time = cumulative_time + _serialDataQTimeout;
  if (cumulative_time >= 1000)
  {
    RUN_KOUNTER++;
    startHangCheckThread();
    cumulative_time = 0;
  }

  // If power hit, save any serial data into db

  if (_cacheMode == CACHE_POWERHIT)
  {
    while (!_serialDataQ.empty())
    {
      SerialData sdata = _serialDataQ.front();
      std::string encodedpostdata = EncodePostData(sdata);

      if (encodedpostdata != "")
      {
        SendLogDataSignal("Caching serial data (" + encodedpostdata + ")", 9);
        CachePOSData(sdata.uuid, encodedpostdata.c_str());
      }
      _serialDataQ.pop();
    }
  }

  // If have data in sql db then handle first since it is older
  
  if (_cacheMode == CACHE_POWERHIT)
  {
    if (_dbDataCacheKount > 0)
      ProcessCachedPOSData();
  }
  else if (_cacheMode == CACHE_EMBEDDED)
  {
    if (!_serialDataQ.empty())
    {
      SerialData sdata = _serialDataQ.front();
      ProcessPOSData(sdata);
    }
  }
  
  // Re-start serial data Q timer
  _serialDataQTimer.expires_from_now(boost::posix_time::milliseconds(_serialDataQTimeout));
  _serialDataQTimer.async_wait(
               boost::bind(&POSBase::serialDataQTimeoutHandler,
                           this, boost::asio::placeholders::error));
}

/******************************************************************************
 *
 ******************************************************************************/
int POSBase::ProcessPOSData(SerialData &sdata)
{
  static int lasterror = 1;

  // Send http post
  std::string encodedpostdata = EncodePostData(sdata);
  int retval = -1;
  if (encodedpostdata != "")
  {
    retval = _httpClient.SendPOSData(
                                boost::lexical_cast<std::string>(sdata.uuid),
                                encodedpostdata.c_str());
  }

  switch (retval)
  {
    case 1:   // success
      if (_cacheMode == CACHE_EMBEDDED)
        _serialDataQ.pop();
      _serialDataQTimeout = 100;
      _posDataRetryKount = 0;
      break;

    case 0:   // network error
      // Slow down timer
      _serialDataQTimeout = 2000;
      break;

    // Just post these errors to the error table
    // since retries are likely to fail
    case -1:  // post invalid - required variable not in post
    case -2:  // plid invalid - location not registered
    case -3:  // checksum invalid - not being used
    case -4:  // server db issue - sql query is invalid
    case -9:  // unknown error
    default:
      handleUnsendableData(encodedpostdata);
      if (_cacheMode == CACHE_EMBEDDED)
        _serialDataQ.pop();
      _serialDataQTimeout = 100;
      _posDataRetryKount = 0;
      break;
  };

  return(retval);
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::CachePOSData(const unsigned int uuid, const std::string &data)
{
  std::string sql = "INSERT INTO SerialData (uuid, post_data) ";
  sql += "VALUES (" + boost::lexical_cast<std::string>(uuid) + ", '";
  sql += data + "');";

  if (!ExecuteSQLStatement(sql, SQL_INSERT))
  {
    SendLogDataSignal("Error inserting into db cache", -1);
    return;
  }

  // Increment db cache count
  _dbDataCacheKount++;
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::ProcessCachedPOSData()
{
  SendLogDataSignal("Processing cached serial data", 9);

  _currentProcessUUID = "";
  std::string sql = "SELECT * FROM SerialData LIMIT 1";

  if (!ExecuteSQLStatement(sql, SQL_SELECT))
  {
    SendLogDataSignal("Error selecting from db cache", -1);
    return;
  }
  else
  {
    SendLogDataSignal("Finished processing cached serial data", 9);
    if (_currentProcessUUID != "")
    {
      if (ExecuteSQLStatement("DELETE FROM SerialData WHERE id=" + _currentProcessUUID, 
                              SQL_DELETE) == 1)
      {
        SendLogDataSignal("SQL DATA id deleted : " + _currentProcessUUID, 9);

        if (_dbDataCacheKount > 0)
          _dbDataCacheKount--;
        else
          _dbDataCacheKount = 0;
      }
    }
  }

  _currentProcessUUID = "";
}

/******************************************************************************
 *
 ******************************************************************************/
bool POSBase::ExecuteSQLStatement(const std::string &sqlcmd, SQLCmdType type)
{
  // Check to see if tables need to be created

  static bool dbinit = true;
  if (dbinit)
  {
    ifstream dbfile(_logPath + "pos.db");
    if (!dbfile)
    {
      if (!createSQLDB())
      {
        _sqlErrorKount++;
        SendLogDataSignal("Can't create database", -1);
        exit(-1);
      }
    }
    dbinit = false;
  }

  // Set SQL cmd type
  _sqlCmdType = type;
  
  // Run sql cmd
  
  std::string dbfilepath = _logPath + "pos.db";
  int retval = sqlite3_open(dbfilepath.c_str(), &_dbDataCache);
  if (retval)
  {
    SendLogDataSignal("Can't open database:"+std::string(sqlite3_errmsg(_dbDataCache)), -1);
    _sqlErrorKount++;
    sqlite3_close(_dbDataCache);
    return(false);
  }  
  char *errmsg = 0;
  int rc = sqlite3_exec(_dbDataCache, sqlcmd.c_str(),
                        POSBase::SqlCmdCallback, (void*) this, &errmsg);
  if (rc != SQLITE_OK)
  {
    SendLogDataSignal("SQL error" + std::string(errmsg), -1);
    _sqlErrorKount++;
    sqlite3_free(errmsg);
    sqlite3_close(_dbDataCache);
    return(false);
  }
  sqlite3_close(_dbDataCache);

  return(true);
}

/******************************************************************************
 *
 ******************************************************************************/
int POSBase::SqlCmdCallback(void *data, int argc, char **argv, char **azColName)
{
  // Process SELECT data
  POSBase *posbase = static_cast<POSBase*>(data);
  if (posbase == NULL)
  {
    posbase->SendLogDataSignal("Error accessing object", -1);
    return(-1);
  }

  SQLCmdType sqlcmdtype = posbase->GetSQLType();
  if (sqlcmdtype == SQL_COUNT)
  {
    posbase->SetDBCacheKount(boost::lexical_cast<unsigned int>(argv[0]));
    return(0);
  }
  else if (sqlcmdtype != SQL_SELECT)
  {
    posbase->SetSQLType(SQL_NONE);
    return(0);
  }
  else
  {
    // Check column size
    if (argc != 3)
    {
      posbase->SendLogDataSignal("SQL SELECT results column mismatch", -1);
      return(0);
    }
  }

  return(posbase->ProcessPOSDBData(argc, argv, azColName));
}

/******************************************************************************
 *
 ******************************************************************************/
int POSBase::ProcessPOSDBData(int argc, char **argv, char **azColName)
{
  static int lasterror = 1;

  // Get SQL row data
  std::string id = argv[0];
  std::string uuid = argv[1];
  std::string encodedpostdata = argv[2];
  _currentProcessUUID = "";   //clear until success

  SendLogDataSignal("Processing cached SQL data ("+ encodedpostdata +")", 9);

  // Send http post
  int retval = _httpClient.SendPOSData(uuid, encodedpostdata);
  switch (retval)
  {
    case 1:   // success
      _currentProcessUUID = id;
      _serialDataQTimeout = 100;
      _posDataRetryKount = 0;
      break;
      
    case 0:   // network error
      // Slow down timer
      _serialDataQTimeout = 2000;
      break;

    case -1:  // post invalid - required variable not in post
    case -2:  // plid invalid - location not registered
    case -3:  // checksum invalid - not being used
    case -4:  // server db issue - sql query is invalid
    case -9:  // unknown error
    default:
      handleUnsendableData(encodedpostdata);
      _currentProcessUUID = id;
      _serialDataQTimeout = 100;
      _posDataRetryKount = 0;
      break;
  };

  return(0);   // need to return 0 on success otherwise sqlite error
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// GUI //////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::ReceivePOSGuiDataSlot(std::string data)
{
  bool cmd_success = true;
  bool save_config = false;

  // Parse xml
  XMLDocument xmldoc;
  xmldoc.Parse(data.c_str());

  // Parse XML command(s)

  XMLNode *n = xmldoc.FirstChild();  //<?xml version="1.0" encoding="UTF-8"?>
  if (n == NULL)
    return;
  n = n->NextSibling();   //<pos_app_config>
  if (n == NULL)
    return;
  XMLElement *e = n->ToElement();
  if ((e==NULL) || (std::string(e->Value())!="pos_app_config"))
    return;
  n = n->FirstChild();   //<command id="..."/>
  bool breakloop = false;
  while ((n!=NULL) && (!breakloop))
  {
    // Get XML command

    XMLElement *ecmd = n->ToElement();
    if ((ecmd==NULL) || (std::string(ecmd->Value())!="command"))
      return;
    std::string xmlcmd = ecmd->Attribute("id");

    // Handle XML command

    if (xmlcmd == "get_config")
    {
      // <command id="get_config"/>

      //<?xml version="1.0" encoding="UTF-8"?>
      //<pos_app_config>
      //   <pos_location   id=”HNS035”/>
      //   <server_address id=”92.12.23.112”/>
      //   <server_path    id=”/pos/beta/”/>
      //   <server_port    id=”80”/>
      //   <log_path       id=”C:\POSApp”/>
      //   <log_level      id=”9”/>
      //   <port id=”1” value=”COM1”>
      //     <baud value=”9600”/>
      //     <parity value=”n”/>
      //     <stop_bits value=”1”/>
      //     <char_size value=”8”/>
      //     <flow_ctrl value=”n”/>
      //     <protocol value="nucleus"/>
      //   </port>
      //   <port id=”1” value=”COM1”>
      //     ...
      //     ...
      //   </port>
      //</pos_app_config>

      ostringstream os;
      os << "<?xml version='1.0' encoding='UTF-8'?>"
         << "<pos_app_config>"
         << "<pos_location   id='" << _posLocationId << "'/>"
         << "<server_address id='" << _httpClient.GetServerAddress() << "'/>"
         << "<server_path    id='" << _httpClient.GetServerPath() << "'/>"
         << "<server_port    id='" << _httpClient.GetServerPort() << "'/>"
         << "<log_path       id='" << _logPath << "'/>"
         << "<log_level      id='" << _logLevel << "'/>";
      for (SerialPortLut::iterator i=_serialPortLut.begin();
           i!=_serialPortLut.end(); i++)
      {
        SerialPort *sport = i->second;
        os << "<port id='" << sport->GetID() << "' "
           << "value='" << sport->GetDeviceName() << "'>"
           << "<baud value='" << sport->GetBaudRate() << "'/>"
           << "<parity value='" << sport->GetParity() << "'/>"
           << "<stop_bits value='" << sport->GetStopBits() << "'/>"
           << "<char_size value='" << sport->GetCharSize() << "'/>"
           << "<flow_ctrl value='" << sport->GetFlowCtrl() << "'/>"
           << "<timeout value='" << sport->GetTimeOut() << "'/>"
           << "<protocol value='" << sport->GetProtocol() << "'/>"
           << "</port>";
      }
      os << "</pos_app_config>";
      SendGuiDataSignal(os.str());
      breakloop = true;     // don't handle any more commands
      break;
    }
    else if (xmlcmd == "clear_config")
    {
      // <command id="clear_config"/>

      CloseSerial();  // close all serial threads
      _groupId = "null";
      _locId = "null";
      _posLocationId = "null";
      _httpClient.SetServerAddress("");
      _httpClient.SetServerPath("");
      _httpClient.SetServerPort(80);
    }
    else if (xmlcmd == "set_pos_app_id")
    {
      // <command id="set_pos_app_id">
      //   <pos_location id=”1”/>
      // </command>

      XMLElement *e = n->FirstChildElement("pos_location");
      _posLocationId = (e != NULL) ? e->Attribute("id") : "null";
      _logNode.SetLocationID(_posLocationId);
      save_config = true;
    }
    else if (xmlcmd == "set_server_info")
    {
      // <command id="set_server_info">
      //   <address id=”92.12.23.112”/>
      //   <path id=”/pos/beta/”/>
      //   <port id=”80”/>
      // </command>

      XMLElement *e = n->FirstChildElement("address");
      std::string ipaddr = (e != NULL) ? e->Attribute("id") : "null";
      _httpClient.SetServerAddress(ipaddr);
      e = n->FirstChildElement("path");
      std::string path = (e != NULL) ? e->Attribute("id") : "null";
      _httpClient.SetServerPath(path);
      _httpClient.SetServerPort(80);
      _logNode.SetServerInfo(ipaddr, path, 80);
      save_config = true;
    }
    else if (xmlcmd == "set_log_info")
    {
      // <command id="set_log_info">
      //   <path id=”C:\\POSApp\\”/>
      //   <level id=”9”/>
      // </command>

      XMLElement *e = n->FirstChildElement("path");
      _logPath = (e != NULL) ? e->Attribute("id") : "";
#if defined(WIN32)
      if (_logPath.find_last_of("\\", _logPath.length()) == string::npos)
        _logPath += "\\";
#else
      if (_logPath.find_last_of("/", _logPath.length()) == string::npos)
        _logPath += "/";
#endif
      e = n->FirstChildElement("level");
      _logLevel = (e != NULL) ? e->IntAttribute("id") : 5;
      _logNode.SetLogSettings(_logPath, _logLevel);
      save_config = true;
    }
    else if (xmlcmd == "add_serial")
    {
      //   <command id="add_serial">
      //     <port id=”1” value=”COM1”>
      //       <baud value=”9600”/>
      //       <parity value=”n”/>
      //       <stop_bits value=”1”/>
      //       <char_size value=”8”/>
      //       <flow_ctrl value=”n”/>
      //       <timeout value=”600000”/>
      //       <protocol value="nucleus"/>
      //     </port>
      //   </command>

      XMLElement *e = n->FirstChildElement("port");
      if (e == NULL)
        return;

      // Serial name
      std::string serialname = e->Attribute("id");
      // Serial port
      std::string serialport = e->Attribute("value");
      // Baud
      XMLElement *e2 = e->FirstChildElement("baud");
      int baud = (e2 != NULL) ? e2->IntAttribute("value") : 9600;
      // Parity
      e2 = e->FirstChildElement("parity");
      std::string tmp = (e2 != NULL) ? e2->Attribute("value") : "";
      char parity = (tmp.length() == 1) ? tmp[0] : 'n';
      // Stop bits
      e2 = e->FirstChildElement("stop_bits");
      float stopbits = (e2 != NULL) ? e2->FloatAttribute("value") : 1;
      // Char size
      e2 = e->FirstChildElement("char_size");
      int charsize = (e2 != NULL) ? e2->IntAttribute("value") : 8;
      // Flow ctrl
      e2 = e->FirstChildElement("flow_ctrl");
      tmp = (e2 != NULL) ? e2->Attribute("value") : "";
      char flowctrl = (tmp.length() == 1) ? tmp[0] : 'n';
      // Timeout
      e2 = e->FirstChildElement("timeout");
      int timeout = (e2 != NULL) ? e2->IntAttribute("value") : 1200000;  //20min
      // Protocol
      e2 = e->FirstChildElement("protocol");
      std::string protocol = (e2 != NULL) ? e2->Attribute("value") : "";

      AddConnection(serialname, serialport, baud, flowctrl, 
                    parity, stopbits, charsize, timeout, POS_UNKNOWN);
      if (!Listen(serialname))
        cmd_success = false;
      else
        save_config = true;
    }
    else if (xmlcmd == "remove_serial")
    {
      // <command id="remove_serial" name=”1”/>

      if (ecmd->FindAttribute("name") == NULL)
        return;
      RemoveConnection(ecmd->Attribute("name"));
    }

    // Get next command
    n = n->NextSibling();
  }

  // Send acknowledgement

  if (cmd_success)
    SendGuiDataSignal("<?xml version='1.0' encoding='UTF-8'?><SUCCESS/>");
  else
    SendGuiDataSignal("<?xml version='1.0' encoding='UTF-8'?><FAILURE/>");

  // Save the config xml
  if (save_config)
  {
    std::string configfile = _logPath + "posconfig.xml";
    XMLPrinter printer;
    xmldoc.Accept( &printer );
    std::string xmltext = printer.CStr();
    std::ofstream file;
    file.open(configfile.c_str(), std::ios_base::trunc);
    file << printer.CStr();
    file.close();
  }
}

/******************************************************************************
 * 
 ******************************************************************************/
void POSBase::StartGUIServer()
{
  SendShutdownSignal.connect(&_guiServer, 
                             &POS::GUI::POSGuiServer::ShutdownSlot);
  SendGuiDataSignal.connect(&_guiServer, 
                             &POS::GUI::POSGuiServer::SendGuiDataSlot);
  SendSerialDataSignal.connect(&_guiServer, 
                             &POS::GUI::POSGuiServer::SendSerialDataSlot);
  _guiServer.SendPOSGuiDataSignal.connect(this, 
                                          &POS::POSBase::ReceivePOSGuiDataSlot);
  _guiServer.SendLogDataSignal.connect(&_logNode,&POSLogNode::LogDataSlot);
  _guiServer.Listen();  
}

/******************************************************************************
 *
 ******************************************************************************/
void POSBase::SetHttpInfo(const std::string &ip, const std::string &dir,
                          const int port)
{
  _httpClient.SetServerAddress(ip);
  _httpClient.SetServerPath(dir);
  _httpClient.SetServerPort(port);
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// LOG //////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

/******************************************************************************
 * 
 ******************************************************************************/
void POSBase::StartLogNode()
{
  SendShutdownSignal.connect(&_logNode, 
                             &POS::LOG::POSLogNode::ShutdownSlot);
  SendLogDataSignal.connect(&_logNode, &POSLogNode::LogDataSlot);
  _httpClient.SendLogDataSignal.connect(&_logNode, &POSLogNode::LogDataSlot);

  _logNode.Listen();  
}

/******************************************************************************
 * 
 ******************************************************************************/
void POSBase::handleUnsendableData(std::string data)
{
  std::ostringstream os;
  os << "Unsendable data\nDATA BEGIN\n"
     << data << "\nDATA END\n";
  os << "Unsendable data\nHEX BEGIN";
  int newline = -1;
  for ( std::string::iterator it=data.begin(); it!=data.end(); ++it)
  {
    if (((++newline) % 8) == 0)
      os << "\n";
    os << "  " << std::setfill('0') << std::setw(2) << std::hex 
       << static_cast<unsigned int>(*it);
  }
  os << "\nHEX END\n";
  SendLogDataSignal(os.str(), -1);
}
