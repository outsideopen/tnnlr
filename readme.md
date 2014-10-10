# tnnlr

This app facilitates the automated maintenence of SSH tunnels from a large number of machines to a central manager. Its goal is to allow machines to be always accessible via SSH regardless of their network situation. tnnlr readily bypasses firewalls and is robust enough to handle drastic network outages and changes with minimal downtime. You can even use a laptop as a client, tnnlr can take it.

## Organization

There are two types of machines in a tnnlr configuration, a server and a client:

* **Server**: The server must have a public IP and you should have root on this machine to set up tnnlr. This is the machine that all the clients point their SSH tunnels to, and the machine that all the clients route their traffic through when SSHing to other clients in the network.

* **Client**: The client may have any type of internet connection where port 22 is not blocked. It also must have passwordless login to a user on the server. You do not need root to set up a client, but basic utilities such as curl, autossh, and screen are required for the script to function. Most servers should have these installed already.

## Setup

### Server

Clone or download this repository and save it wherever you like. Install the prerequisites (this may require root):
  
    sudo apt-get install python-pip sqlite3
    pip install flask
    pip install sqlite3

Then just fire up the server with `python server.py`.

Make sure that the server has an account with passwordless ssh login enabled (**not root**), this is for the clients to connect to.

It may be a good idea to add a keepalive script to make sure it doesn't randomly die, and to make the server come back up on reboots. Here's the simple one I use:

    #!/bin/bash
    lines=`ps aux | grep tnnlr | wc -l`
    echo 'Checking...'
    if [ $lines -eq 1 ]
    then
      echo 'tnnlr not running, restarting...'
      screen -dmS tnnlr-server /usr/bin/python /srv/tnnlr/server/server.py
    fi

You can now visit the web interface at server:5000.

### Client

If you haven't already, generate an SSH key (`ssh-keygen`) and copy it to the server (`ssh-copy-id`). Ensure that curl, autossh, and screen are installed (`sudo apt-get install curl autossh screen`).

Copy the client script into the directory of your choice and add it to your crontab like so:

    */5 * * * * /path/to/script/tnnlr <server>

Where 'server' is either the IP or DNS of your server. The script will attempt to SSH as the user running the script by default, this can be configured after it has first made contact from the web interface.
