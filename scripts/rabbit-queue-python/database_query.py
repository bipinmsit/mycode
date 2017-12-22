import pymysql
import json

def dbconfig(env=True):
    if env:
         return (
        # production credentials
        {
            "host": "35.188.94.146",
            "user": "root",
            "password": "OCcGbkvk5qka38F6",
            "db": "vimana_oltp_server"
        })
    else:
        return (        
    #     test credential
    {
        "host": "35.196.29.90",
        "user": "root",
        "password": "ywcpkgecELcbuBwk",
        "db": "vimana_oltp_server"
    }
    )


def dbconnection(env=True):
   cnx = dbconfig(env)
   # Open database connection
   db = pymysql.connect(host=cnx['host'],user=cnx['user'],password=cnx['password'],db=cnx['db'])
   return db

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def dbquery(params=None,env=True):
   db=dbconnection(env)
   # prepare a cursor object using cursor() method
   cursor = db.cursor()

   # Prepare SQL query to INSERT a record into the database.
   sql = "SELECT * FROM vm_details where vm_status=(%s)"
   try:
      # Execute the SQL command
      cursor.execute(sql,params)
      # Fetch all the rows in a list of lists.
      results = cursor.fetchall()
      if results:
         return (results)
      else:
         return None
   except:
      return ("Error: unable to fetch data")

   # disconnect from server
   db.close()