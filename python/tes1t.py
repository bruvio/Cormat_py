#def is_python_64bit():
#    return (struct.calcsize("P") == 8)

#is_python_64bit()

import os
import sys
# def os_platform():
#     true_platform = os.environ['PROCESSOR_ARCHITECTURE']
#     try:
#             true_platform = os.environ["PROCESSOR_ARCHITEW6432"]
#     except KeyError:
#             pass
#             #true_platform not assigned to if this does not exist
#     return true_platform
#
# os_platform()

import platform

assert platform.architecture()[0] == '64bit'
assert sys.version_info >= (
    3, 5), "Python version too old. Please use >= 3.5.X."
