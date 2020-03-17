import logging
import logging.handlers
import time
from baker import Baker

def main():
    # Setup logging
    logfile = 'receipt.log'
    logrotatesize = 20971520  # 20mb
    logmaxfiles = 100
    loglevel = logging.DEBUG
    logformat = '%(asctime)s [%(levelname)s] %(pathname)s::%(funcName)s(%(lineno)s) - %(message)s'
    loghandlers = [logging.StreamHandler(), logging.handlers.RotatingFileHandler(logfile,
                                                        maxBytes=logrotatesize,
                                                        backupCount=logmaxfiles)]
    logging.basicConfig(level = loglevel, format = logformat, handlers = loghandlers)

    # Bake a pie
    logging.info("---------------------------------------------------------")
    logging.info("Starting pie")
    baker = None
    try:
        # Start baker
        baker = Baker()
        baker.Bake()
        logging.info("Done baking")
        baker = None
    except Exception as e:
        logging.error(e)
        logging.exception(traceback.format_exc())
    finally:
        if baker != None:
            baker.Quit()
    logging.info("Closing PieBox")
    logging.shutdown()
    return

if __name__ == "__main__":
    main()
