"""
Wrapper for opening, writing & closing a PPF.

TO DO: Implement Time-Dependent Status Flags. I don't seem to be able to set tdsf's AND specify an itref in order
       to use a previous dtype's time-vector.
added
output file with log
shot,user,date,seq
"""

import logging
import pickle

from ppf import ppfgo, ppfuid, ppfopn, pdstd
from ppf import ppfwri_ihdat, ppfwri_irdat, ppfwri
from ppf import ppfwri_tbsf_ref_set, ppfwri_tbsf_set
from ppf import ppfclo, ppfabo
import datetime
logger = logging.getLogger(__name__)
now = datetime.datetime.now()
date=print(now.strftime("%Y-%m-%d"))
# ----------------------------
__author__ = "L. Kogan"
# ----------------------------



def check_uid(shot_no, write_uid):
    """
    Open PPF to check if UID is valid, then abort

    :param shot_no: shot number
    :param write_uid: write_uid
    :return: 1 if UID is invalid, 0 otherwise
    """

    ier = open_ppf(shot_no, write_uid, comment="Testing UID".ljust(40))

    if ier != 0:
        return 1

#    ier = close_ppf(shot_no)

    ier = ppfabo()

    return 0

def open_ppf(shot_no, write_uid, comment="CORRECTED KG1 DATA FROM KG1C AND KG1R   "):
    """
    Open PPF for writing

    :param shot_no: shot number
    :param write_uid: write UID
    :return: error code from PPF system. It will be 0 if there is no error.
    """

    # Initialise PPF system
    ier = ppfgo(pulse=shot_no)

    if ier != 0:
        return ier

    # Set UID
    ppfuid(write_uid, 'w')

    # Retrieve shot data and time, for PPFOPN
    time, date, ier = pdstd(shot_no)

    if ier != 0:
        return ier

    # Open PPF for writing
    ier = ppfopn(shot_no, date, time, comment)

    return ier

def write_ppf(shot_no, dda, dtype, data, time=None,
              comment=None, unitd=None, unitt=None,
              itref=-1, nt=None, global_status=None,
              status=None):
    """
    Write PPF DDA/DTYPE

    :param shot_no: shot number
    :param dda: DDA
    :param dtype: DTYPE
    :param data: numpy array of data
    :param time: numpy array of time
    :param comment: comment
    :param unitd: units for data
    :param unitt: units for time
    :param itref: reference for timebase
    :param nt: size of the time vector
    :param global_status: status for the DTYPE
    :param status: time-dependent status
    :return: error code (0 if everything is OK), itref for timebase written
    """

    logger.log(5, ( "Writing {}/{} : {}".format(dda, dtype, comment)))

    # PPF dtype needs to have 4 characters: add extra spaces if this is not the case
    if len(dtype) < 4:
        dtype = dtype.ljust(4)

    if nt is None:
        nt = len(time)

    if len(data) != nt:
        logger.error("Could not write {}/{}: data and time vectors are different lengths".format(dda, dtype))
        return 1, -1

    logger.log(5, ( "Length time vector {}".format(nt)))

    logger.log(5, ( "Using itref {}".format(itref)))

    data_type = 'F'
    if (data.dtype == 'int32' or data.dtype == 'int64'):
        data_type = 'I'

    time_type = 'F'
    if (time.dtype == 'int32' or  data.dtype == 'int64'):
        time_type = 'I'

    if global_status is None:
        global_status = 0

    # Create ihdat & irdat
    ihdat = ppfwri_ihdat(unitd, "", unitt, data_type, data_type, time_type, comment)

    logger.log(5, ( "ihdat {}".format(ihdat)))

    irdat = ppfwri_irdat(1, nt, refx=-1, reft=itref, user=0, system=global_status)

    logger.log(5, ( "irdat {}".format(irdat)))

    # Set TDSF : THIS ISN'T WORKING PROPERLY YET... I WANT TO NOT SET A STATUS FLAG WHEN status is NONE ...
#    if status is not None:
#        logger.debug("Length status flag {}".format(len(status)))
#        ppfwri_tbsf_ref_set(-1)
#        ppfwri_tbsf_set(status)
#    else:
#        ppfwri_tbsf_ref_set(0)
#        status = np.zeros(nt)
#        ppfwri_tbsf_set(status)

    # Write data
    # irdat[7]=0 #generates ppf identical to KG1V code
    # irdat[8]=-1
    iwdat, ier = ppfwri(shot_no, dda, dtype, irdat, ihdat, data, global_status, time)

    logger.log(5, ( "iwdat: {}".format(iwdat)))
    logger.log(5, ( "itref for signal that was just written : {}".format(iwdat[8])))
    logger.log(5, ( "ier: {}".format(ier)))

    if ier != 0:
        logger.warning("Failed to write PPF {}/{}. Errorcode {}".format(dda, dtype, ier))

    return ier, iwdat[8]

def close_ppf(shot_no, write_uid,version):
    """
    Close PPF

    :param shot_no: shot number
    :return: error code, 0 if everything is OK
    """
    import time
    import os
    owner = os.getenv('USR')
    timestr = time.strftime("%Y-%m-%d")
    program = 'KG1 PPF  '
    # time, date, ier = pdstd(shot_no)
    seq, ier = ppfclo(shot_no, program, version)
    with open('run_out.txt','a+') as f_out:
        f_out.write("shot: {} user: {} date: {} seq: {} written by: {}\n".format(shot_no,write_uid,str(timestr),seq,owner))
    f_out.close()
    logger.info("\n shot: {} user: {} date: {} seq: {} written by: {}\n".format(shot_no,write_uid,timestr,seq,owner))

    return ier