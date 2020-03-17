#ifndef POS_Nucleus
#define POS_Nucleus

#include <regex>
#include <boost/timer/timer.hpp>
#include "POSBase.h"

namespace POS
{
  class POSNucleus : public POSBase
  {
    public:
    POSNucleus(boost::asio::io_service *iosvc);
    POSNucleus(boost::asio::io_service *iosvc, 
               const std::string &logdir);
    virtual void AddConnection(const std::string &sid, 
                               const std::string &port,
                               const unsigned int &baud,
                               const char flow,
                               const char parity,
                               const float stop,
                               const unsigned int char_size,
                               const int timeout,
                               POSType postype);
    virtual void RunPOSSim(boost::program_options::variables_map &vmap);
    virtual void RunPOSSim(const std::string &file, const std::string &serial,
                           size_t iterations);

    protected:
    virtual void SetDefaultParsingExpression(std::vector<std::regex> &regexvec);
    virtual std::string EncodePostData(SerialData &sdata);

    protected:
    std::string   _logDir;
  };
}

#endif
