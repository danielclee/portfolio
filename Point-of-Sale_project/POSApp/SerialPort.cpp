#pragma warning(disable:4996) 
#pragma warning(disable:4503) 

#include <boost/algorithm/string.hpp>
#include <fstream>
#include "SerialPort.h"

using namespace POS;
using namespace boost::asio;
using namespace sigslot;

/******************************************************************************
 *
 ******************************************************************************/
SerialPort::SerialPort(boost::asio::io_service &iosvc,
                       const std::string &sid, 
                       const std::string &port,
                       const unsigned int &baud,
                       const serial_port_base::flow_control::type flow,
                       const serial_port_base::parity::type parity,
                       const serial_port_base::stop_bits::type stop,
                       const unsigned int char_size,
                       const int timeout) :
  _ioService(&iosvc),
  _threadIOService(NULL),
  _serialTimeOutTimeout(timeout),
  _id(sid),
  _device_name(port),
  _baud_rate(baud),
  _flow_ctrl(flow),
  _parity(parity),
  _stop_bits(stop),
  _char_size(char_size),
  _serialBuffer('\0'),
  _buffer(""),
  _partialBuffer(""),
  _running(false),
  _serialError(false)
{
  // Create serial port
  _serial_port.reset(new boost::asio::serial_port(iosvc));
}

/******************************************************************************
 *
 ******************************************************************************/
SerialPort::~SerialPort()
{
  _running = false;

  // Wait 1000 ms
  boost::asio::deadline_timer t((*_ioService));
  t.expires_from_now(boost::posix_time::milliseconds(1000));
  boost::system::error_code ec;
  t.wait(ec);

  _ioService = NULL;
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// NON-THREAD SERIAL ////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

/******************************************************************************
 *
 ******************************************************************************/
bool SerialPort::Open()
{
  try
  {
    if (_serial_port->is_open())
      return(true);

    _serial_port->open(_device_name);

    _serial_port->set_option(_baud_rate);
    _serial_port->set_option(_flow_ctrl);
    _serial_port->set_option(_parity);
    _serial_port->set_option(_stop_bits);
    _serial_port->set_option(_char_size);

    std::ostringstream os;
    os << "Opened serial port (" << _id << ") : "
       << _device_name << "("
       << _baud_rate.value() << GetParity() << _char_size.value()
       << GetStopBits() << GetFlowCtrl() << ")";
    SendLogDataSignal(os.str(), 6);

    return(true);
  }
  catch(const boost::system::system_error& e)
  {
    std::string errorstr = "Error opening serial port " \
                           "(" + std::string(e.what()) + ")";
    SendLogDataSignal(errorstr, -1);
    return(false);
  }
  catch(...)
  {
    SendLogDataSignal("Unknwon error opening serial port", -1);
    return(false);
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::Close()
{
  try
  {
    if (_serial_port->is_open())
      _serial_port->close();
  }
  catch(const boost::system::error_code& err)
  {
    std::string errorstr = "Error closing serial port " \
                           "(" + std::string(err.message()) + ")";
    SendLogDataSignal(errorstr, -1);
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::Write(char data)
{
  try
  {
    _serial_port->write_some(boost::asio::buffer(&data, 1));
  }
  catch(const boost::system::error_code& err)
  {
    std::string errorstr = "Error writing to serial port " \
                           "(" + err.message() + ")";
    SendLogDataSignal(errorstr, -1);
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::Write(const char *data, size_t len)
{
  try
  {
    _serial_port->write_some(boost::asio::buffer(data, len));
  }
  catch(const boost::system::error_code& err)
  {
    std::string errorstr = "Error writing to serial port " \
                           "(" + err.message() + ")";
    SendLogDataSignal(errorstr, -1);
  }
}

/******************************************************************************
 * 
 ******************************************************************************/
char SerialPort::GetFlowCtrl()
{
  char ret;
  switch(_flow_ctrl.value())
  {
    case serial_port_base::flow_control::type::none:
      ret = 'n';
      break;

    case serial_port_base::flow_control::type::hardware:
      ret = 'h';
      break;

    case serial_port_base::flow_control::type::software:
      ret = 's';
      break;

    default:
      ret = '0';
      break;
  };

  return(ret);
}

/******************************************************************************
 * 
 ******************************************************************************/
char SerialPort::GetParity()
{
  char ret;
  switch(_parity.value())
  {
    case serial_port_base::parity::type::none:
      ret = 'n';
      break;

    case serial_port_base::parity::type::odd:
      ret = 'o';
      break;

    case serial_port_base::parity::type::even:
      ret = 'e';
      break;

    default:
      ret = '0';
      break;
  };

  return(ret);
}

/******************************************************************************
 * 
 ******************************************************************************/
float SerialPort::GetStopBits()
{
  float ret;
  switch(_stop_bits.value())
  {
    case serial_port_base::stop_bits::type::one:
      ret = 1;
      break;
    case serial_port_base::stop_bits::type::onepointfive:
      ret = 1.5;                                        
      break;
    case serial_port_base::stop_bits::type::two:
      ret = 2;
      break;
    default:
      ret = 0;
    break;
  };

  return(ret);
}

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// POS SERIAL ///////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::ShutdownSlot(const std::string sid)
{
  if ((sid==_id) || (sid=="all"))
  {
    SendLogDataSignal("Serial port (" + sid +") shutting down", 9);
    _running = false;
    _threadIOService->stop();
  }
}

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::AddParsingExpression(std::regex e)
{
  _regex_list.push_back(e);
}

/******************************************************************************
 *
 ******************************************************************************/
bool SerialPort::Listen()
{
  // Run in another thread
  _thread = boost::thread(&SerialPort::ListenThread, this, this);
  _thread.detach();

  return(true);
}

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::ListenThread(SerialPort *serialport)
{
  // Set running flag
  _running = true;

  // Set serial error flag
  _serialError = false;

  // Wait for 500 ms
  boost::asio::deadline_timer t((*_ioService));
  t.expires_from_now(boost::posix_time::milliseconds(500));
  boost::system::error_code ec;
  t.wait(ec);

  // Start listening to serial port

  _buffer.clear();
  _partialBuffer.clear();
  boost::match_flag_type regex_flags = boost::match_default;
  while (_running)
  {
    // Create io service

    boost::asio::io_service iosvc;
    boost::asio::serial_port sp(iosvc);
    boost::asio::deadline_timer timeout(iosvc);
    bool  data_available = false;
    serialport->SetThreadIOService(&iosvc);;

    // Wait before trying to open serial port again
    boost::asio::deadline_timer t(iosvc);
    t.expires_from_now(boost::posix_time::milliseconds(500));
    boost::system::error_code ec;
    t.wait(ec);

    // Open serial port

    try
    {
      sp.open(_device_name);
      sp.set_option(_baud_rate);
      sp.set_option(_flow_ctrl);
      sp.set_option(_parity);
      sp.set_option(_stop_bits);
      sp.set_option(_char_size);
    }
    catch(const boost::system::system_error& e)
    {
      std::string errorstr = "Error opening serial port " \
                             "(" + std::string(e.what()) + ")";
      SendLogDataSignal(errorstr, -1);
      sp.close();

      // If serial port error, wait 5 secs before trying to 
      // open serial port again
      boost::asio::deadline_timer t(iosvc);
      t.expires_from_now(boost::posix_time::milliseconds(5000));
      boost::system::error_code ec;
      t.wait(ec);
      continue;
    }
    SendLogDataSignal("Serial (" + _id + ") listening to serial port ...", 0);

    // Read data while serial port is open

    while(sp.is_open() && _running)
    {
      try
      {
        // Serial port async read and timeout

        sp.async_read_some(boost::asio::buffer(&_serialBuffer, 1),
                           boost::bind(&SerialPort::serialDataReadHandler, 
                                       this, boost::ref(data_available), 
                                       boost::ref(timeout),
                                       boost::asio::placeholders::error,
                                 boost::asio::placeholders::bytes_transferred));
        timeout.expires_from_now(
                      boost::posix_time::milliseconds(_serialTimeOutTimeout));
        timeout.async_wait(boost::bind(&SerialPort::serialTimeoutHandler, 
                                       this, boost::ref(sp),
                                       boost::asio::placeholders::error));

        // Run ioservice
        iosvc.run();

        // Reset ioservice for next round
        iosvc.reset();

        // If no data is read then close serial port
        if (!data_available)
        {
          sp.close();
          break;
        }
      }
      catch (boost::system::system_error &e)
      {
        sp.close();
        SendLogDataSignal("Serial(" + _id + ") : " + std::string(e.what()), -1);
      }
      catch (...)
      {
        sp.close();
        SendLogDataSignal("Serial(" + _id + ") : unknown error", -1);
      }
    } /* End while is_open */

    // Closing serial port

    SendLogDataSignal("Serial closing : " + _id, 0);
    sp.close();
    _buffer.clear();
    _partialBuffer.clear();
  }  /* End while _running */

  _threadIOService = NULL;
  SendLogDataSignal("Serial(" + _id + ") : thread stopping", -1);
}

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::serialDataReadHandler(bool& data_available, 
                                       deadline_timer& timeout, 
                                       const boost::system::error_code& error, 
                                       std::size_t bytes_transferred)
{
  if (error || !bytes_transferred)
  {
    // No data was read!
    data_available = false;
    return;
  }

  // Try to match serial data

  _buffer.push_back(_serialBuffer);
  if (MatchData(_serialBuffer, _buffer))
  {
    _buffer.clear();
    if (!_partialBuffer.empty())
    {
      _buffer = _partialBuffer;
      _partialBuffer.clear();
    }
  }
  _serialBuffer = '\0';

  timeout.cancel();  // will cause wait_callback to fire with an error
  data_available = true;
}

/******************************************************************************
 *
 ******************************************************************************/
void SerialPort::serialTimeoutHandler(serial_port& ser_port, 
                                      const boost::system::error_code& error)
{
  if (error)
  {
    // Data was read and this timeout was canceled
    return;
  }

  // Send log info
  SendLogDataSignal("Serial timeout : " + _id, 0);

  // Cancel serial port operations
  ser_port.cancel();
}

/******************************************************************************
 * 
 ******************************************************************************/
void SerialPort::HandleUnparsableData()
{
  std::ostringstream os;
  os << "Unparsable data (" << _id << ")\nDATA BEGIN\n"
     << _buffer << "\nDATA END\n";
  os << "Unparsable data (" << _id << ")\nHEX BEGIN";
  int newline = -1;
  for ( std::string::iterator it=_buffer.begin(); it!=_buffer.end(); ++it)
  {
    if (((++newline) % 8) == 0)
      os << "\n";
    os << "  " << std::setfill('0') << std::setw(2) << std::hex 
       << static_cast<unsigned int>(*it);
  }
  os << "\nHEX END\n";
  SendLogDataSignal(os.str(), -1);
}
