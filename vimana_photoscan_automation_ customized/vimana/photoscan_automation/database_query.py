import pymysql

def dbconfig(env =False):
    """
    Function to get dbconfig
    Args:
        env: Boolean to decide whether to use Production credentials or not. 
             [True -> Production, False -> Test Credentials]
    """
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


def dbconnection(env =False):
    global db
    cnx = dbconfig(env)

    # Open database connection
    try:
        db = pymysql.connect(host=cnx['host'], user=cnx['user'], password=cnx['password'], db=cnx['db'],cursorclass=pymysql.cursors.DictCursor)
    except:
        logging.error("Error: unable to update data")
    return db