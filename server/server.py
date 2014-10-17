# tnnlr
#   Simple SSH tunnel manager
#   Alexander Standke - OutsideOpen
#   October 2014

from flask import Flask, request, jsonify, render_template, redirect, send_from_directory, Response, request
import sqlite3 as lite
from datetime import datetime as time
from random import randint

app = Flask(__name__)

# Configuration
PORT = 5000           # The port for the web interface
TUNNEL_RANGE = 15000  # The starting port, the range of usable ports is this + 1000


# Don't change anything below here unless you know what you're doing :)

# Schema for hosts
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
  "last_report",
  "nickname"
]


# Initialize Database
con = lite.connect('db.sqlite3')
try:
  con.cursor().execute("select * from Clients")
except lite.OperationalError:
  print "No DB found, creating..."
  con.cursor().execute("create table Clients(hostname UNIQUE, " + ", ".join(host_attrs) + "," + ", ".join(extra_attrs) + ");")


# Methods
def get_args(request, key):
  try:
    return request.form[key]
  except:
    return 'Not Submitted'

def find_by_hostname(hostname):
  con = lite.connect('db.sqlite3')
  return con.cursor().execute('select * from Clients where hostname = ?', (hostname,)).fetchall()

def create_or_update_host(hostname, request):
  con = lite.connect('db.sqlite3')
  if len(find_by_hostname(hostname)) > 0: # update
    args = map(lambda k: k + " = '" + get_args(request, k) + "'", [x for x in host_attrs if x != 'user'])
    command = "update Clients set " + ", ".join(args)
    command += ", last_report = '" + str(time.now()) + "', restart = 'false' "
    command += "where hostname = '" + hostname + "'"
    print command
    con.cursor().execute(command)
    con.commit()
  else: # create
    args = map(lambda k: get_args(request, k), host_attrs)
    command = "insert into Clients values('" + hostname + "', '" 
    command += "','".join(args) + "', '" 
    command += str(randint(TUNNEL_RANGE, TUNNEL_RANGE + 1000))
    command += "', 'false', 'false', '" + str(time.now()) + "', '" + hostname + "')"
    con.cursor().execute(command)
    con.commit()

def update_attr(hostname, attr, value):
  con = lite.connect('db.sqlite3')
  con.cursor().execute("update Clients set "+attr+"=? where hostname=?", (value,hostname))
  con.commit()

# Web Panel Views
@app.route("/")
def index():
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("select hostname, port, last_report, local_ip, outside_ip, restart, nickname from Clients").fetchall()
  return render_template('index.html', clients=clients)

@app.route("/show/<hostname>")
def show(hostname):
  client = find_by_hostname(hostname)[0]
  return render_template('show.html', client=client, hostname=hostname)

@app.route("/release/<hostname>")
def release(hostname):
  con = lite.connect('db.sqlite3')
  con.cursor().execute("delete from Clients where hostname = ?", (hostname,))
  con.commit()
  return redirect('/')

@app.route("/restart/<hostname>")
def restart(hostname):
  update_attr(hostname, 'restart', 'true')
  return redirect('/')

@app.route("/toggle_configs/<hostname>")
def toggle(hostname):
  client = find_by_hostname(hostname)[0]
  if (client[11] == 'true'):
    update_attr(hostname, 'update_configs', 'false')
  else:
    update_attr(hostname, 'update_configs', 'true')
  return redirect('/show/' + hostname)

@app.route("/set_user/<hostname>", methods=['POST'])
def set_user(hostname):
  update_attr(hostname, 'user', request.form['user'])
  return redirect('/show/' + hostname)

@app.route("/set_nick/<hostname>", methods=['POST'])
def set_nick(hostname):
  update_attr(hostname, 'nickname', request.form['nick'])
  return redirect('/show/' + hostname)


# API Endpoints
@app.route("/api/<hostname>", methods=['POST'])
def api(hostname):
  try:
    client = find_by_hostname(hostname)[0]
    create_or_update_host(hostname, request)
  except:
    create_or_update_host(hostname, request)
    client = find_by_hostname(hostname)[0]

  print len(client)
  return client[9] + ";" + client[10] + ";" + client[3] + ";" + client[11]

@app.route("/api/configs")
def configs():
  arr = ["#tnnlr - keep this at the bottom"]
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("select hostname, port, nickname from Clients")
  for c in clients:
    arr.append("Host " + c[2])
    arr.append("    ProxyCommand ssh %h nc localhost " + c[1])
    arr.append("    User " + request.args.get('user', ''))
    arr.append("    HostKeyAlias " + c[2])
    arr.append("    Hostname " + request.host.split(':')[0])
    arr.append("")

  return Response("\n".join(arr), content_type="text/plain;charset=UTF-8")
 
# Serve Static Assets
@app.route('/assets/<path:filename>')
def send_assets(filename):
    return send_from_directory('assets', filename)

# Run Like the Wind
app.config.update(DEBUG=True)
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=PORT)

