import sqlite3
from sqlite3 import Error
import os
import csv
import pdb
import logging
logger = logging.getLogger(__name__)
def create_connection_memory():
    """ create a database connection to a database that resides
        in the memory
    """
    conn = None;
    try:
        conn = sqlite3.connect(':memory:')
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def check_string_in_file(filename, string):
    """

    :param filename:
    :param string:
    :return: checks if the string is in that file
    """
    with open(filename) as myfile:
        if string in myfile.read():
            return True
        else:
            return False


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)


def convert_out_textfile_into_csv(filetxt,csvoutputfile):
        with open(filetxt, "r") as f_in:
            lines = f_in.readlines()
            for index, line in enumerate(lines):
                # print(line)
                if "shot" in str(line):

                    dummy = lines[index].split()
                    shot = int(dummy[1])
                    logger.log(5, "shot {}".format(shot))
                    user = str(dummy[3])
                    date = str(dummy[5])

                    # #             dummy = lines[index + 1].split()
                    sequence = dummy[7]

                    writtenby = dummy[10] 


                    string_to_write = "{}  {}  {}  {}  {}\n".format(
                        str(shot).strip(),
                        user.strip(),
                        str(date).strip(),
                        str(sequence).strip(),
                        writtenby.strip(),
                    )

                    if os.path.exists(csvoutputfile):
                            if check_string_in_file(csvoutputfile, string_to_write):
                                pass
                            else:
                                with open(csvoutputfile, "a+") as f_out:
                                    f_out.write(string_to_write)
                                f_out.close()
                    else:
                        with open(csvoutputfile, "a+") as f_out:
                            f_out.write(string_to_write)
                        f_out.close()                   


def column_header(csvfile):

    with open(csvfile, "rb") as f:
        reader = csv.reader(f)
        i = reader.next()
        rest = list(reader)
    return rest


def create_table():
    try:
        os.remove("cormat_db.db")
    except:
        pass
    connection = sqlite3.connect("cormat_db.db")
    cursor = connection.cursor()
    create_table = ("CREATE TABLE IF NOT EXISTS cormat ( shot integer, user text, date_time,  seq integer,  written_by text );") # use your column names here
    cursor.execute(create_table)

if __name__ == '__main__':

    convert_out_textfile_into_csv('../../kg1lh_py/python/run_out.txt','./run_out.csv')
    create_table()

   
    connection = sqlite3.connect("cormat_db.db")
    cursor = connection.cursor()
    with open('run_out.csv','r') as fin: # `with` statement available in 2.5+
            lines = fin.readlines()
            for index, line in enumerate(lines):
                    dummy = lines[index].split()
                    
                    shot = int(dummy[0])
                    user = str(dummy[1])
                    datee = str(dummy[2])
                    sequencee = dummy[3]
                    writtenby = dummy[4] 
                    # pdb.set_trace()
                    cursor.execute("INSERT INTO cormat  VALUES (?, ?, ?, ?, ?)", (shot, user, datee, sequencee, writtenby))
                


    connection.commit()
    connection.close()
# 