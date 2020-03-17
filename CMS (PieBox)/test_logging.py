import _thread
import traceback
import threading
import logging
import logging.handlers
from time import sleep

class TestLogger1:
    def __init__(self):
        self._module = {'modulename':__class__.__name__}

    def Run(self):
        kount1 = 0;
        while True:
            kount1 += 1
            logging.info("Kount is " + str(kount1), extra=self._module)
            sleep(1.1)


class TestLogger2:
    def __init__(self):
        self._module = {'modulename':__class__.__name__}

    def Run(self):
        kount2 = 0;
        while True:
            kount2 += 1
            logging.info("Kount is " + str(kount2), extra=self._module)
            sleep(1.1)


class HeadClass:
    def __init__(self):
        self._module = {'modulename':__class__.__name__}
        gg = 0
        
    def StartThread1(self):
        gg = TestLogger1()
        gg.Run()


    def StartThread2(self):
        gg2 = TestLogger2()
        gg2.Run()


    def Start(self):
        self._thread1 = threading.Thread(name='thread1', target=self.StartThread1)
        self._thread1.start()
        self._thread2 = threading.Thread(name='thread2', target=self.StartThread2)
        self._thread2.start()
        kount = 0
        while True:
            kount += 1
            logging.debug("Main loop " + str(kount), extra=self._module)
            sleep(0.6)


def testlog1():
    try:
        print(gg)
    except Exception as e:
        logging.exception(traceback.format_exc())


def testlog2():
    try:
        while True:
            logging.debug("1234568910")
            sleep(1.1)
    except Exception as e:
        logging.exception(traceback.format_exc())


def main():
    logfile = 'test_log.log'
    logrotatesize = 20971520  # 20mb
    logmaxfiles = 1000
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.StreamHandler(), logging.handlers.RotatingFileHandler(logfile,
                                                        maxBytes=logrotatesize,
                                                        backupCount=logmaxfiles)]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    ## head = HeadClass()
    ## head.Start()
    logging.info("-------------------------------------------------")
    logging.info("Start test log")
    ## testlog1()
    testlog2()

#
if __name__ == "__main__":
    main()
