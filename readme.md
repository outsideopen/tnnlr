# tnnlr
#### Simple SSH Tunnel Manager
#### Alexander Standke

This app facilitates the automated maintenence of SSH tunnels from a large number of machines to a central manager. Its goal is to allow machines to be always accessible via SSH regardless of their network situation. tnnlr readily bypasses firewalls and is robust enough to handle drastic network outages and changes with minimal downtime. You can even use a laptop as a client, tnnlr can take it.

### Features

 * Automatic SSH tunnel maintenance
 * Easy client installation, just add a single script to the crontab and let tnnlr do the rest
 * Collects basic diagnostic information such as `w`, `free`, `df -h`, `ifconfig` and others.
 * Optional SSH Configuration updating. Simply type `ssh <hostname>` on any machine in the tunnel network to connect to another machine in the network.

### Organization

There are two types of machines in a tnnlr configuration, a server and a client:

* **Server**: The server must have a public IP and you should have root on this machine to set up tnnlr. This is the machine that all the clients point their SSH tunnels to, and the machine that all the clients route their traffic through when SSHing to other clients in the network. There is only one of these on a given network.

* **Client**: The client may have any type of internet connection where port 22 is not blocked. It also must have passwordless login to a user on the server. You do not need root to set up a client, but basic utilities such as curl, autossh, and screen are required for the script to function. Most servers should have these installed already. You can theoretically have up to 1000 clients on a network.

## Setup

### Server

Clone or download this repository and save it wherever you like. Install the prerequisites (this may require root):
  
    sudo apt-get install python-pip sqlite3
    pip install flask
    pip install Flask-BasicAuth
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

You can now visit the web interface at `server:5000`. You can modify which port the web server uses (as well as which ports it assigns for SSH tunnels) by changing the values at the top of `server.py`.

### Client

If you haven't already, generate an SSH key (`ssh-keygen`) and copy it to the server (`ssh-copy-id`). Ensure that curl, autossh, and screen are installed (`sudo apt-get install curl autossh screen`).

Copy the client script (`curl -s server:5000/tnnlr.sh > tnnlr.sh`) into the directory of your choice, make it executable (`chmod +x tnnlr.sh`) and add it to your crontab like so:

    */5 * * * * /path/to/script/tnnlr.sh

The script will attempt to SSH as the user running the script by default, but the user can be configured after it has first made contact from the web interface.

## Usage

Once tnnlr is set up on a server and client(s), simply visit the web interface at server:5000. From here, you will see a list of the clients that are connected to your tunnel network.

#### Home Page
Basic information such as the most recent update time, internal and external IPs, and the tunnel port the client is assigned is available on the home page. There are three things you can do with a given client on the home page:

 * **Release**: Destroys the record of the client and assigns it a new port the next time it sends a request.
 * **Force Restart**: Causes the client to kill any existing tunnels next time it sends a request. If a client can't be reached, a restart will usually clear it up.
 * **Show**: Links to the client's information and settings page.

You can also manually generate SSH configurations for a given user (to be copied into `~/.ssh/config`), and get a link directly to the client script from the home.

#### Show

The show page shows detailed information on a specific client, including the results of several commonly used diagnostic commands and information that the server has collected.

You can modify the client settings from this page as well:

 * **Nickname**: The name shown on the homepage and used in the generation of SSH configs.
 * **User**: The user that the client will attempt to use to connect to the server.
 * **Update Configs**: Toggles whether or not the client script will update the SSH configs of this client. When true, the script will generate a set of SSH configurations for each client and cat them to the user's SSH config file (or update existing configuration if there are changes).
