from flask import Flask, request, jsonify, render_template, redirect
import sqlite3 as lite
from datetime import datetime as time

app = Flask(__name__)

# useful vars
host_attrs = [
  "outside_ip",
  "local_ip",
  "port",
  "user",
  "uptime",
  "free",
  "dfh",
  "ifconfig",
  "route"
]

extra_attrs = [
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
  if len(find_by_hostname(hostname)) > 0:
    # exists already, just update
    print 'it exists! lets just update'
  else:
    print 'time to add a new one!'



# dat app
@app.route("/")
def index():
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("select hostname, port, last_report, local_ip, outside_ip from Clients").fetchall()
  return render_template('index.html', clients=clients)

@app.route("/api/<hostname>", methods=['POST'])
def api(hostname):
  args = map(lambda k: get_args(request, k), host_attrs)
  con = lite.connect('db.sqlite3')
  # command = "insert into Clients values('" + hostname + "', '" + "','".join(args) + "', 'false', 'false', '" + str(time.now()) + "')"
  # print command
  # con.cursor().execute(command)
  # con.commit()
  find_or_update_host(hostname, request)
  return 'HELLO'


# ready player one
app.config.update(DEBUG=True)
if __name__ == "__main__":
  app.run(host='0.0.0.0')

