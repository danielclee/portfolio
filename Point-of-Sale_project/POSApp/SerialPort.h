#ifndef SERIAL_PORT
#define SERIAL_PORT

#include <stdlib.h>
#include <vector>
#include <boost/asio.hpp>
#include <boost/asio/serial_port.hpp>
#include <regex>
#include <boost/thread.hpp>
#include "sigslot.h"

namespace POS
{
  class SerialPort : public sigslot::has_slots<>
  {
    public:
    sigslot::signal2<std::string, std::smatch, multi_threaded_local>  SendPOSDataSignal;
    sigslot::signal2<std::string, int, multi_threaded_local>   SendLogDataSignal;
    void ShutdownSlot(std::string sid);

    public:
    SerialPort(boost::asio::io_service &iosvc,
               const std::string &sid, 
               const std::string &port,
               const unsigned int &baud,
               const boost::asio::serial_port_base::flow_control::type flow,
               const boost::asio::serial_port_base::parity::type parity,
               const boost::asio::serial_port_base::stop_bits::type stop,
               const unsigned int char_size,
               const int timeout);
    virtual ~SerialPort();
    bool Open();
    void Close();
    std::string GetId()  {return(_id);};
    void AddParsingExpression(std::regex e);

    bool Listen();
    void Write(char data);
    void Write(const char *data, size_t len);

    inline std::string GetID()  {return(_id);};
    inline std::string GetDeviceName()  {return(_device_name);};
    inline unsigned int GetBaudRate()  {return(_baud_rate.value());};
    inline unsigned int GetCharSize()  {return(_char_size.value());};
    char GetFlowCtrl();
    char GetParity();
    float GetStopBits();
    inline int GetTimeOut()  {return(_serialTimeOutTimeout);};
    inline std::string GetProtocol()  {return("nucleus");};

    inline void SetThreadIOService(boost::asio::io_service *iosvc) {_threadIOService = iosvc;};

    public:
    void ListenThread(SerialPort *serialport);
    void serialDataReadHandler(bool& data_available, 
                               boost::asio::deadline_timer& timeout, 
                               const boost::system::error_code& error, 
                               std::size_t bytes_transferred);
    void serialTimeoutHandler(boost::asio::serial_port& ser_port, 
                              const boost::system::error_code& error);

    protected:
    virtual bool MatchData(char c, const std::string &buffer) {return(false);};
    virtual bool InvalidDataCheck(char c, const std::string &buffer) {return(false);};
    void HandleUnparsableData();

    private:
    struct SerialPortDeleter
    { 
      SerialPortDeleter() { };
      SerialPortDeleter(const SerialPortDeleter&) { }
      void operator() (SerialPort* p) const 
      {
        p->Close();
        delete p;
      }
    };

    protected:
    boost::asio::io_service                        *_ioService;
    boost::asio::io_service                        *_threadIOService;
    int                                            _serialTimeOutTimeout;
    // Serial info
    std::string  _id;
    std::string  _device_name;   // i.e. COM1 or /dev/ttyS1
    boost::asio::serial_port_base::baud_rate       _baud_rate;
    boost::asio::serial_port_base::flow_control    _flow_ctrl;
    boost::asio::serial_port_base::parity          _parity;
    boost::asio::serial_port_base::stop_bits       _stop_bits;
    boost::asio::serial_port_base::character_size  _char_size;
    std::unique_ptr<boost::asio::serial_port>      _serial_port;
    // Buffer
    std::vector<std::regex>                        _regex_list;
    char                                           _serialBuffer;
    std::string                                    _buffer;
    std::string                                    _partialBuffer;
    // Thread
    boost::thread                                  _thread;
    // Misc
    bool                                           _running;
    bool                                           _serialError;
  };
};

#endif
