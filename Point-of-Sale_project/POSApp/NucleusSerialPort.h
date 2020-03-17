#ifndef NUCLEUS_SERIAL_PORT
#define NUCLEUS_SERIAL_PORT

#include "SerialPort.h"
#include <boost/asio.hpp>
#include <boost/asio/serial_port.hpp>

namespace POS
{
  class NucleusSerialPort : public SerialPort
  {
    public:
    NucleusSerialPort(boost::asio::io_service &iosvc,
               const std::string &sid, 
               const std::string &port,
               const unsigned int &baud,
               const boost::asio::serial_port_base::flow_control::type flow,
               const boost::asio::serial_port_base::parity::type parity,
               const boost::asio::serial_port_base::stop_bits::type stop,
               const unsigned int char_size,
               const int timeout);

    protected:
    virtual bool MatchData(char c, const std::string &buffer);
    virtual bool InvalidDataCheck(char c, const std::string &buffer);

    private:
    int _crkount;
  };
};

#endif
