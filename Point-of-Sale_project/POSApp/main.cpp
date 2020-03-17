#pragma warning(disable:4996) 
#pragma warning(disable:4503) 
#pragma warning(disable:4250) 

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <boost/program_options.hpp>
#include <regex>
#include "POSBase.h"
#include "POSNucleus.h"
#include "POSGuiServer.h"
#include <boost/crc.hpp>  //3434

/******************************************************************************
 * Wait for user input to quit
 ******************************************************************************/
void WaitForQuit()
{
  printf("Press 'q' to quit\n");
  char c;
  do 
  {
    std::cin >> c;
  } 
  while (c != 'q');
}

/******************************************************************************
 * MAIN
 ******************************************************************************/
int main(int argc, char *argv[])
{
  // Define command line options

  boost::program_options::options_description desc("Options"); 
  desc.add_options() 
    ("sim", "Simulator Mode") 
    ("iterations", boost::program_options::value<int>()->default_value(0), 
                            "Sim iterations (0-unlimited, n-interations)")
    ("sim_file", boost::program_options::value< std::vector<std::string> >(), 
                            "Test file (i.e. C:\\postest.txt")
    ("test,t", "Test Mode") 
    ("serial,s", boost::program_options::value< std::vector<std::string> >(), 
                           "Serial port (i.e. COM1, ttyS0)")
    ("baud,b", boost::program_options::value<int>()->default_value(9600), 
                            "Baud rate (i.e. 9600)")
    ("parity,p", boost::program_options::value<char>()->default_value('n'), 
                            "Parity (n, e, o)")
    ("stopbits,i", boost::program_options::value<float>()->default_value(1), 
                            "Stop bits (1, 1.5, 2")
    ("flowcontrol,w", boost::program_options::value<char>()->default_value('n'),
                            "Flow control (n, h, s")
    ("charsize,c", boost::program_options::value<int>()->default_value(8), 
                            "Character size (8, 7)")
    ("server,z", boost::program_options::value< std::vector<std::string> >(), 
                           "Server address (i.e. 192.168.1.1 or http://...)")
    ("serverpath,v", boost::program_options::value<std::vector<std::string> >(), 
                           "Server path (i.e. test/test.html)")
    ("port,r", boost::program_options::value<int>()->default_value(8081), 
                            "Server port (i.e. 8081)")
    ("log,l", boost::program_options::value< std::vector<std::string> >(), 
                            "Log file location (i.e. C:\\")
    ("http", boost::program_options::value< std::vector<std::string> >(), 
                            "Webscript address (i.e. ")
    ("help,h", "Print help messages");

  // Parse command line options

  boost::program_options::variables_map vm; 
  try 
  { 
    boost::program_options::store(
           boost::program_options::parse_command_line(argc, argv, desc),  
           vm); // can throw 
 
    if ( vm.count("help")  ) 
    { 
      std::cout << "Basic Command Line Parameters" << std::endl 
                << desc << std::endl; 
      exit(0);
    } 
 
    boost::program_options::notify(vm); 
  } 
  catch(boost::program_options::error& e) 
  { 
    std::cerr << "ERROR: " << e.what() << std::endl << std::endl; 
    std::cerr << desc << std::endl; 
    WaitForQuit();
    exit(-1);
  } 
  catch(std::exception& e) 
  { 
    std::cerr << "Unhandled Exception reached the top of main: " 
              << e.what() << ", application will now exit" << std::endl; 
    WaitForQuit();
    exit(-1);
  } 

  // IOService object
  boost::asio::io_service ioservice;

  // POS Nucleus object
  POS::POSNucleus posnucleus(&ioservice);

  // POS logging
  posnucleus.StartLogNode();
  
  //******************************************************
  // Sim mode

  if (vm.count("sim"))    // SIM
  {
    // Run POS sim
    posnucleus.RunPOSSim(vm);

    // Exit
    exit(0);
  }

//3434//  //******************************************************
//3434//  // Test mode
//3434//
//3434//  if (vm.count("test")) 
//3434//  {
//3434//    std::vector<std::string> serveraddrvec =
//3434//                         vm["server"].as< std::vector<std::string> >();
//3434//    std::string serveraddr = serveraddrvec[0];
//3434//    std::vector<std::string> serverpathvec =
//3434//                         vm["serverpath"].as< std::vector<std::string> >();
//3434//    std::string serverpath = serverpathvec[0];
//3434//
//3434//    // Setup http
//3434//    posnucleus.SetHttpInfo(serveraddr, serverpath);
//3434//
//3434//    if (!posnucleus.StartApp())
//3434//    {
//3434//      printf("Error starting application, exiting\n\n");
//3434//      WaitForQuit();
//3434//      exit(0);
//3434//    }
//3434//
//3434//    // Start serial threads
//3434//
//3434//    std::string serialport = "";
//3434//    int baud = 9600;
//3434//    char parity = 'n';
//3434//    int charsize = 8;
//3434//    float stopbits = 1;
//3434//    char flow = 'n';
//3434//
//3434//    // Get serial port name
//3434//
//3434//    if (!vm.count("serial"))
//3434//    {
//3434//      std::cerr << "Need to provide a serial port" << std::endl; 
//3434//      WaitForQuit();
//3434//      exit(-1);
//3434//    }
//3434//    std::vector<std::string> serialnamevec =
//3434//                         vm["serial"].as< std::vector<std::string> >();
//3434//    serialport = serialnamevec[0];
//3434//
//3434//    // Get serial port options
//3434//
//3434//    if (vm.count("baud"))
//3434//      baud = vm["baud"].as<int>();
//3434//    if (vm.count("parity"))
//3434//      parity = vm["parity"].as<char>();
//3434//    if (vm.count("stopbits"))
//3434//      stopbits = vm["stopbits"].as<float>();
//3434//    if (vm.count("flowcontrol"))
//3434//      flow = vm["flowcontrol"].as<char>();
//3434//    if (vm.count("charsize"))
//3434//      charsize = vm["charsize"].as<int>();
//3434//
//3434//    // Add testPOS serial connection
//3434//
//3434//    posnucleus.AddConnection("POSTEST", serialport, baud, flow, 
//3434//                             parity, stopbits, charsize, 
//3434//                             POS::POSBase::POS_UNKNOWN);
//3434//    if (!posnucleus.ConnectSerial("POSTEST"))
//3434//    {
//3434//      printf("Error opening serial port %s, exiting\n", serialport.c_str());
//3434//      WaitForQuit();
//3434//      exit(-1);
//3434//    }
//3434//
//3434//    // Listen to POS port(s)
//3434//    posnucleus.Listen("POSTEST");
//3434//
//3434//    // Wait for quit signal
//3434//    WaitForQuit();
//3434//  
//3434//    // Close all serial port(s) and data cache
//3434//    posnucleus.SendShutdownSignal("all");  
//3434//
//3434//    // Exit
//3434//    exit(0);
//3434//  }

  //******************************************************
  // App mode

  // POS Gui
  posnucleus.StartGUIServer();

  // POS config
  posnucleus.LoadConfig();

  // Start running
  if (!posnucleus.StartApp())
  {
    printf("Error starting application, exiting\n\n");
    WaitForQuit();
    exit(0);
  }
  
  // Run ioservice
  while (1)
  {
    ioservice.run();
    ioservice.reset();
  }

  // Exit
  exit(0);
}
