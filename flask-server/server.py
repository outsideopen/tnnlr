from flask import Flask, request, jsonify, render_template, redirect, send_from_directory
import sqlite3 as lite
from datetime import datetime as time
from random import randint

app = Flask(__name__)

# useful vars
host_attrs = [
  "outside_ip",
  "local_ip",
  "user",
  "uptime",
  "free",
  "dfh",
  "ifconfig",
  "route"
]

extra_attrs = [
  "port",
  "restart",
  "update_configs",
  "last_report"
]


# init DB
con = lite.connect('db.sqlite3')
try:
  con.cursor().execute("select * from Clients")
except lite.OperationalError:
  print "No DB found, creating..."
  con.cursor().execute("create table Clients(hostname UNIQUE, " + ", ".join(host_attrs) + "," + ", ".join(extra_attrs) + ");")


# methods
def get_args(request, key):
  try:
    return request.form[key]
  except:
    return 'Not Submitted'

def find_by_hostname(hostname):
  con = lite.connect('db.sqlite3')
  return con.cursor().execute("select * from Clients where hostname = '" + hostname + "'").fetchall()

def find_or_update_host(hostname, request):
  con = lite.connect('db.sqlite3')
  if len(find_by_hostname(hostname)) > 0: # update
    args = map(lambda k: k + " = '" + get_args(request, k) + "'", host_attrs)
    command = "update Clients set " + ", ".join(args)
    command += ", last_report = '" + str(time.now()) + "' "
    command += "where hostname = '" + hostname + "'"
    print command
    con.cursor().execute(command)
    con.commit()
  else: # create
    args = map(lambda k: get_args(request, k), host_attrs)
    command = "insert into Clients values('" + hostname + "', '" + "','".join(args) + "', '" + str(randint(15000, 16000)) + "', 'false', 'false', '" + str(time.now()) + "')"
    con.cursor().execute(command)
    con.commit()


# dat app
@app.route("/")
def index():
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("select hostname, port, last_report, local_ip, outside_ip from Clients").fetchall()
  return render_template('index.html', clients=clients)

@app.route("/api/<hostname>", methods=['POST'])
def api(hostname):
  find_or_update_host(hostname, request)

  client = find_by_hostname(hostname)[0]
  print len(client)
  return client[9] + ";" + client[10] + ";" + client[3] + ";" + client[11]

@app.route("/release/<hostname>")
def release(hostname):
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("delete from Clients where hostname = '" + hostname + "'")
  con.commit()
  return redirect('/')



# static assets
@app.route('/assets/<path:filename>')
def send_foo(filename):
    return send_from_directory('assets', filename)

# ready player one
app.config.update(DEBUG=True)
if __name__ == "__main__":
  app.run(host='0.0.0.0')

