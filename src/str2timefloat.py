import time
import argparse
from datetime import datetime

formats = ['%Y-%m-%d', '%Y-%m-%d:%H', '%Y-%m-%d:%H:%M', '%Y-%m-%d:%H:%M:%S']

def ds2tf(input):
    """Takes a string containing a date and optionally also time and converts to a float.
    Input must be formatted as:
     %Y-%m-%d, %Y-%m-%d:%H, %Y-%m-%d:%H:%M or %Y-%m-%d:%H:%M:%S.
    For example 2013-04-27:13:37
    
    Returns a floating point number compatible with time(), or None for ''.
    """

    output = None

    if (input != ''):
        dt = None

        for format in formats:
            try:
                dt = datetime.strptime(input, format)
            except ValueError:
                continue #continue trying formats
            break #compatible format found

        if (dt is not None):
            output = time.mktime(time.struct_time(dt.timetuple()))
        else:
            raise ValueError("time data '" + input + "' does not match any supported format.")

    return output


def timefloat(input):
    try:
        return ds2tf(input)
    except ValueError as e:
        raise argparse.ArgumentTypeError("'{}' is not a valid date time format. The expected format is 'yyyy-MM-dd[:HH[:mm[:ss]]]'.".format(input)) from e

