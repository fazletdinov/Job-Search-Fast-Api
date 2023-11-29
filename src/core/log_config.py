LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(asctime)s - %(name)s - %(message)s',
        },
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    #      "json": {  # The formatter name
    #         "()": "pythonjsonlogger.jsonlogger.JsonFormatter",  # The class to instantiate!
    #         # Json is more complex, but easier to read, display all attributes!
    #         "format": """
    #                 asctime: %(asctime)s
    #                 created: %(created)f
    #                 filename: %(filename)s
    #                 funcName: %(funcName)s
    #                 levelname: %(levelname)s
    #                 levelno: %(levelno)s
    #                 lineno: %(lineno)d
    #                 message: %(message)s
    #                 module: %(module)s
    #                 msec: %(msecs)d
    #                 name: %(name)s
    #                 pathname: %(pathname)s
    #                 process: %(process)d
    #                 processName: %(processName)s
    #                 relativeCreated: %(relativeCreated)d
    #                 thread: %(thread)d
    #                 threadName: %(threadName)s
    #                 exc_info: %(exc_info)s
    #             """,
    #         "datefmt": "%Y-%m-%d %H:%M:%S",  # How to display dates
    #     },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'logconfig.log',
            'maxBytes': 10240,
            'backupCount': 10,
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'DEBUG',
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": "no"
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": "no"
        }
    },
    'root': {
        'level': 'DEBUG',
        'formatter': 'verbose',
        'handlers': ['file', 'default'],
    },
}