from flask import Flask, request, jsonify, render_template, redirect, send_from_directory, Response, request
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
    command += ", last_report = '" + str(time.now()) + "', restart = 'false' "
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
  clients = con.cursor().execute("select hostname, port, last_report, local_ip, outside_ip, restart from Clients").fetchall()
  return render_template('index.html', clients=clients)

@app.route("/release/<hostname>")
def release(hostname):
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("delete from Clients where hostname = '" + hostname + "'")
  con.commit()
  return redirect('/')

@app.route("/restart/<hostname>")
def restart(hostname):
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("update Clients set restart = 'true' where hostname = '" + hostname + "'")
  con.commit()
  return redirect('/')

@app.route("/toggle_configs/<hostname>")
def toggle(hostname):
  con = lite.connect('db.sqlite3')
  update_configs = con.cursor().execute("select update_configs from Clients where hostname = '" + hostname + "'").fetchall()[0][0]
  if (update_configs == 'true'):
    update_configs = 'false'
  else:
    update_configs = 'true'

  con.cursor().execute("update Clients set update_configs = '" + update_configs + "' where hostname = '" + hostname + "'")
  con.commit()
  return redirect('/show/' + hostname)

@app.route("/show/<hostname>")
def show(hostname):
  client = find_by_hostname(hostname)[0]
  return render_template('show.html', client=client, hostname=hostname)


# api endpoints
@app.route("/api/<hostname>", methods=['POST'])
def api(hostname):
  try:
    client = find_by_hostname(hostname)[0]
    find_or_update_host(hostname, request)
  except:
    find_or_update_host(hostname, request)
    client = find_by_hostname(hostname)[0]

  print len(client)
  return client[9] + ";" + client[10] + ";" + client[3] + ";" + client[11]

@app.route("/api/configs")
def configs():
  arr = ["#tnnlr - keep this at the bottom"]
  con = lite.connect('db.sqlite3')
  clients = con.cursor().execute("select hostname, port from Clients")
  for c in clients:
    arr.append("Host " + c[0])
    arr.append("    ProxyCommand ssh %h nc localhost " + c[1])
    arr.append("    User " + request.args.get('user', ''))
    arr.append("    HostKeyAlias " + c[0])
    arr.append("    Hostname " + request.host.split(':')[0])
    arr.append("")

  return Response("\n".join(arr), content_type="text/plain;charset=UTF-8")
 
# static assets
@app.route('/assets/<path:filename>')
def send_foo(filename):
    return send_from_directory('assets', filename)

# ready player one
app.config.update(DEBUG=True)
if __name__ == "__main__":
  app.run(host='0.0.0.0')

