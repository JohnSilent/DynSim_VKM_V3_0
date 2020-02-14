import sqlite3 

def get_db(db_name="./data/DB_Faults.db"):
    """Connects to sqlite3-database ('db_name') and return Connection and cursor object.
    Connection has to be closed manually with conn.close().

    Parameters
    ----------
    conn:  
        sqlite3 Connection object as a result of sqlite3.connect('DB_name.db')
    c: 
        sqlite3 Cursor as a result of sqlite3.cursor()
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    return (conn, c)

    
def insert_fault(conn, c, tablename, fault):
    """Inserts a new row of values (stored in fault) into the database table "tablename",
    to which the connection (conn) and the cursor (c) are pointing.

    Parameters
    ----------
    conn:  
        sqlite3 Connection object as a result of sqlite3.connect('DB_name.db')
    c: 
        sqlite3 Cursor as a result of sqlite3.cursor()
    tablename: str
        Name of a database table
    fault: 
        instance of class Faults"""
    with conn:
        str_execute = "INSERT INTO {} VALUES ('{}', {}, {}, {}, '{}', '{}', {}, {})".format(tablename, fault.test, fault.duration, fault.fault_type, fault.uf, fault.grid, fault.qset, fault.phases, fault.uv)
        # print(str_execute)
        c.execute(str_execute)
        

def get_faults_by_test(conn, c, tablename, test=None):
    """Selects a row or all rows (test=None) of the database table "tablename",
    to which the connection (conn) and the cursor (c) are pointing.

    Parameters
    ----------
    conn:  
        sqlite3 Connection object as a result of sqlite3.connect('DB_name.db')
    c: 
        sqlite3 Cursor as a result of sqlite3.cursor()
    tablename: str
        Name of a database table
    test : str
        number of the fault according to VDE-AR-N 4110/4120, FGW TR8 Rev 9
        
    Returns: 
    --------
    c.fetchall(): list
        Fetches all rows of a query result, returning a list.
    str(e): str
        Error message (string) if table could not be loaded
    """
    
    str_execute = "SELECT * FROM {}".format(tablename)
    if not test is None:
        str_execute = str_execute + " WHERE test={}".format(test)
    try:
        c.execute(str_execute)
    except sqlite3.OperationalError as e:
        return str(e)        
    return c.fetchall()

def update_fault(conn, c, tablename, fault, change_col, value):
    """Update a value of the column "change_col" of the database table "tablename",
    to which the connection (conn) and the cursor (c) are pointing.

    Parameters
    ----------
    conn:  
        sqlite3 Connection object as a result of sqlite3.connect('DB_name.db')
    c: 
        sqlite3 Cursor as a result of sqlite3.cursor()
    tablename: str
        Name of a database table
    fault: 
        instance of class Faults
    change_col: str
        Name of the column of the database table
    value: str, int or double
        value, which the choosen cell is changed to
        
    TODO 
    ----------
    1) Try Except einfügen, falls change_col nicht in Table Faults 
    """
    with conn:
        str_execute = "UPDATE {} SET {}={} WHERE test={}".format(tablename, change_col, value, fault.test)
        
        c.execute(str_execute)
        
def remove_fault(conn, c, tablename, fault):
    """Removes a row from the database table "tablename",
    to which the connection (conn) and the cursor (c) are pointing.

    Parameters
    ----------
    conn:  
        sqlite3 Connection object as a result of sqlite3.connect('DB_name.db')
    c: 
        sqlite3 Cursor as a result of sqlite3.cursor()
    tablename: str
        Name of a database table
    fault: 
        instance of class Faults
    """
    with conn:
        str_execute = "DELETE from {} WHERE test = {}".format(tablename, fault.test)
        c.execute(str_execute)