import sqlite3
    

global last_rows

def create_table():

    conn=sqlite3.connect("weatherData.db")
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS weatherData (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, days INTEGER, seconds INTEGER, temp REAL,dew REAL, humidity REAL, pressure REAL, CO2 REAL, O2 REAL, lux REAL)")
    
    
    
def insert(date,days,seconds,temp,dew,humidity,pressure,CO2,O2,lux):
    
    conn=sqlite3.connect("weatherData.db")
    cur=conn.cursor() 
    cur.execute("INSERT INTO weatherData VALUES(?,?,?,?,?,?,?,?,?,?,?)",(None,date,days,seconds,temp,dew,humidity,pressure,CO2,O2,lux,))
    last_rows = cur.lastrowid
    conn.commit()
    conn.close()
    return last_rows
    
def read_bydays(datatype, days_filter):
    conn = sqlite3.connect("weatherData.db")
    cur = conn.cursor()
    command  = "SELECT {column} FROM weatherData Where days = {days}".format(column = datatype, days = days_filter)
    cur.execute(command)
    rows = cur.fetchall()
    conn.close()
    return rows

def read_byrow(datatype, row_filter):
    conn = sqlite3.connect("weatherData.db")
    cur = conn.cursor()
    command  = "SELECT {column} FROM weatherData Where id = {idd}".format(column = datatype, idd = row_filter)
    cur.execute(command)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_bound(bound):#options are ASC or DESC
    conn = sqlite3.connect("weatherData.db")
    cur = conn.cursor()
    command  = "SELECT * FROM weatherData ORDER BY id {bd} LIMIT 1".format(bd = bound)
    cur.execute(command)
    rows = cur.fetchone()
    conn.close()
    return rows

def view():
    conn=sqlite3.connect("weatherData.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM weatherData")
    rows=cur.fetchall()
    conn.close()#no commit since we are just fetching
    return rows

def delete(number):
      conn=sqlite3.connect("weatherData.db")
      cur=conn.cursor()
      cur.execute("DELETE FROM weatherData WHERE number=?",(number,))#comma after item
      conn.commit()
      conn.close()

def update(date,days,seconds,temp,dew,humidity,pressure,CO2,O2,lux):
      conn=sqlite3.connect("weatherData.db")
      cur=conn.cursor()
      cur.execute("UPDATE weatherData SET date = ?,days= ?,seconds = ?,temp= ?,dew = ?, humidity= ?,pressure= ?,CO2= ?,O2= ?,lux= ? WHERE id=?",(date,days,temp,dew,humidity,pressure,CO2,O2,lux,id,))#comma after item
      conn.commit()
      conn.close()



