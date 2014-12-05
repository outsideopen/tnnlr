# tnnlr
#   Simple SSH tunnel manager
#   Alexander Standke - OutsideOpen
#   October 2014

# Configuration
PORT = 5000           # The port for the web interface
TUNNEL_RANGE = 15000  # The starting port, the range of usable ports is this + 1000

require_login = True  # Password protect web interface - recommended
username = 'admin'    #   For real security, use SSL/TLS as well
password = 'password'

base_uri = '/tnnlr'

# Libraries
from flask import Flask, request, jsonify, render_template, redirect, send_from_directory, Response, request
from flask.ext.basicauth import BasicAuth
import sqlite3 as lite
from datetime import datetime as time
from random import randint

app = Flask(__name__)


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


# Authentication
app.config['BASIC_AUTH_FORCE'] = require_login
app.config['BASIC_AUTH_USERNAME'] = username
app.config['BASIC_AUTH_PASSWORD'] = password
basic_auth = BasicAuth(app)

app.config['APPLICATION_ROOT'] = base_uri

# Initialize Database
con = lite.connect('db.sqlite3')
try:
  con.cursor().execute("select * from Clients")
except lite.OperationalError:
  print "No DB found, creating..."
  con.cursor().execute("create table Clients(hostname UNIQUE, " + ", ".join(host_attrs) + "," + ", ".join(extra_attrs) + ");")


# Helper Methods
def get_args(request, key):
  try:
    return request.form[key]
  except:
    return 'Not Submitted'

def find_by_hostname(hostname):
  con = lite.connect('db.sqlite3')
  return con.cursor().execute('select * from Clients where hostname = ?', (hostname,)).fetchone()

def create_or_update_host(hostname, request):
  client = find_by_hostname(hostname)
  if client == None:
    create_client(hostname, request)
    return find_by_hostname(hostname)
  else:
    update_client(hostname, request)
    return client

def create_client(hostname, request):
  con = lite.connect('db.sqlite3')
  args = map(lambda k: get_args(request, k), host_attrs)
  command = "insert into Clients values('%s', '%s', '%i', 'false', 'false', '%s', '%s')" % (hostname, "','".join(args), randint(TUNNEL_RANGE, TUNNEL_RANGE + 1000), str(time.now()), hostname)
  con.cursor().execute(command)
  con.commit()

def update_client(hostname, request):
  con = lite.connect('db.sqlite3')
  args = map(lambda k: k + " = '" + get_args(request, k) + "'", [x for x in host_attrs if x != 'user'])
  command = "update Clients set %s, last_report = '%s', restart = 'false' where hostname = '%s'" % (", ".join(args), str(time.now()), hostname)
  con.cursor().execute(command)
  con.commit()

def update_attr(hostname, attr, value):
  con = lite.connect('db.sqlite3')
  con.cursor().execute("update Clients set "+attr+"=? where hostname=?", (value,hostname))
  con.commit()

def all_clients():
  con = lite.connect('db.sqlite3')
  return con.cursor().execute("select * from Clients").fetchall()

def destroy_client(hostname):
  con = lite.connect('db.sqlite3')
  con.cursor().execute("delete from Clients where hostname = ?", (hostname,))
  con.commit()

# Web Panel Views
@app.route("/")
def index():
  return render_template('index.html', clients=all_clients())

@app.route("/show/<hostname>")
def show(hostname):
  client = find_by_hostname(hostname)
  return render_template('show.html', client=client, hostname=hostname)

@app.route("/tnnlr.sh")
def script():
  return Response(render_template('tnnlr.sh', remote=request.host.split(':')[0], port=PORT), content_type="text/plain;charset=UTF-8")

@app.route("/release/<hostname>")
def release(hostname):
  destroy_client(hostname)
  return redirect('/')

@app.route("/restart/<hostname>")
def restart(hostname):
  update_attr(hostname, 'restart', 'true')
  return redirect('/')

@app.route("/toggle_configs/<hostname>")
def toggle(hostname):
  client = find_by_hostname(hostname)
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
  client = create_or_update_host(hostname, request)
  return client[9] + ";" + client[10] + ";" + client[3] + ";" + client[11]

@app.route("/api/configs")
def configs():
  arr = ["#tnnlr - keep this at the bottom"]
  for c in all_clients():
    arr.append("Host " + c[13])
    arr.append("    ProxyCommand ssh %h nc localhost " + c[9])
    arr.append("    User " + request.args.get('user', ''))
    arr.append("    HostKeyAlias " + c[13])
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

