import sys
from unittest.mock import Mock


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    module = type(sys)('pyrebase')
    module.pyrebase = type(sys)("pyrebase")
    module.pyrebase.Stream = Mock()
    # module.sum = fwlib_sum
    sys.modules['pyrebase'] = module
    sys.modules['pyrebase.pyrebase'] = module.pyrebase


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
