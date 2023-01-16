"""
consoleLogger
format=%(asctime)s [%(levelname)s] %(name)s : %(message)s
Event message   ::= <Datetime> [<LogLevel>] <Message>
Datetime        ::= <Date and Time in UTC>
LogLevel        ::= DEBUG | INFO | WARNING | ERROR | CRITICAL
Message         ::= <CodeLocation>: <string>

metricsLogger
Event message   ::= <Datetime> <Preamble> <Identifier> <Event details>
Datetime        ::= <Date and Time in UTC>

Preamble        ::= User event | Project event | Publication event

Identifier      ::= <User> | <Project> | <Publication>
User            ::= usr:<UUID>[:<User email>]
Project         ::= prj:<UUID>
Publication     ::= pub:<UUID>

Event details   ::= <Verb> [ <Attribute name> <Attribute value>] [by <User>]
Verb            ::= create | modify-add | modify-remove | delete
Attribute name  ::= <string>
Attribute value ::= <string>
UUID            ::= <uuid string>
"""

import logging.config
import os
import time

logging.Formatter.converter = time.gmtime
logging.config.fileConfig(os.path.dirname(os.path.abspath(__file__)) + '/logging.ini')

# create logger
consoleLogger = logging.getLogger('consoleLogger')
metricsLogger = logging.getLogger('metricsLogger')
