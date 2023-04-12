def myLogger(name):
    global loggers
    
    import logging, logging.handlers

    loggers = {}
    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        handler = logging.handlers.SysLogHandler(address=('SYSLOG-SERVER-IP-GOES-HERE',514))
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggers[name] = logger
                       
        return logger