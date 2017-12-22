import pymysql
import os, sys
script_path = os.path.realpath(__file__)
python_path = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
sys.path.append(python_path)

from python.utils.common import Common

common = Common()
import json
import socket

def dbconfig():
    # hostname = socket.gethostname()
    # if hostname in "test":
    #     return (
    #     {
    #         "host": "35.196.29.90",
    #         "user": "root",
    #         "password": "ywcpkgecELcbuBwk",
    #         "db": "vimana_oltp_server"
    #     }
    #     )
    # else:
    #     return (
    #     {
    #         "host": "35.188.94.146",
    #         "user": "root",
    #         "password": "OCcGbkvk5qka38F6",
    #         "db": "vimana_oltp_server"
    #     }
    #     )

    return (common.mysql_conn())


def dbconnection():
    global db
    cnx = dbconfig()
    # Open database connection
    try:
        db = pymysql.connect(host=cnx['host'], user=cnx['user'], password=cnx['password'], db=cnx['db'],cursorclass=pymysql.cursors.DictCursor)
    except:
        common.logging("Error: unable to update data")
    return db


def update_process_status(process_name=None, site_name=None, stage_name=None, grouping=None):
    db = dbconnection()
    cursor = db.cursor()
    sql = "UPDATE process_statuses SET process_status=(%s) WHERE site=(%s) and stage=(%s) and grouping=(%s)"
    try:
        cursor.execute(sql, (process_name, site_name, stage_name, grouping))
    except:
        common.logging("Error: unable to update data")
    db.commit()
    db.close()


def update_process_log(process_name=None, vm_name=None, photoscan_params=None):
    global vm_id
    db = dbconnection()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM vm_details where vm_name=(%s)",vm_name)
    result_set = cursor.fetchone()
    vlog ={'photoscan_proccess_name':process_name}
    merged_dict = vlog.update(photoscan_params)
    sql = "INSERT INTO vm_logs (vm_log, vm_id,photoscan_params) VALUES (%s,%s,%s)"
    try:
        cursor.execute(sql,(process_name,result_set['id'] , str(merged_dict)))
    except:
        common.logging("Error: unable to insert data")
    db.commit()
    db.close()