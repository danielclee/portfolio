#pragma warning(disable:4996) 
#pragma warning(disable:4503) 

#include "NucleusSerialPort.h"

using namespace POS;
using namespace boost::asio;

/******************************************************************************
 *
 ******************************************************************************/
NucleusSerialPort::NucleusSerialPort(boost::asio::io_service &iosvc,
                       const std::string &sid, 
                       const std::string &port,
                       const unsigned int &baud,
                       const serial_port_base::flow_control::type flow,
                       const serial_port_base::parity::type parity,
                       const serial_port_base::stop_bits::type stop,
                       const unsigned int char_size,
                       const int timeout) :
  SerialPort(iosvc, sid, port, baud, flow, parity, stop, char_size, timeout),
  _crkount(0)
{
}

/******************************************************************************
 *
 ******************************************************************************/
bool NucleusSerialPort::MatchData(char c, const std::string &buffer)
{
  bool clearbuffer = false;
  bool checkmatch = false;
  bool foundmatch = false;

  if (c == '\n')
  {
    _crkount++;
    checkmatch = true;
  }
  else if (buffer.length() >= 73)
  {
    checkmatch = true;
  }

  // Look for any regex matches

  if (checkmatch)
  {  
    for (size_t i=0; i<_regex_list.size(); i++)
    {
      std::smatch m;
      if (std::regex_search(buffer, m, _regex_list[i]))
      {
        // Send data signal
        SendPOSDataSignal(_id, m);

        // Set match flag
        foundmatch = true;

        // Set clear buffer flag
        clearbuffer = true;

        // Clear the CR count
        _crkount = 0;

        // See if need to save the partial buffer

        std::string tmpbuff = m[0];
		if (tmpbuff.length() < _buffer.length())
        {
          _partialBuffer = _buffer.substr(tmpbuff.length(), std::string::npos);
        }

        // Found match, skipping loop
        break;
      }
    }
  }

  // If 3rd set of CRs then clear buffer

  if ((_crkount>=3) || (buffer.length()>=75))
  {
    if (!foundmatch)
    {
      HandleUnparsableData();
      _crkount = 0;
      clearbuffer = true;
    }
  }

  return(clearbuffer);
}

/******************************************************************************
 *
 ******************************************************************************/
bool NucleusSerialPort::InvalidDataCheck(char c, const std::string &buffer)
{
  bool retval = false;
  if (c == '\n')
  {
    _crkount++;
    if (buffer.size() > 154)
    {
      retval = true;
      _crkount = 0;
    }
  }

  return(retval);
}

