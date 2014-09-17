# client script

### installation

Install requirements

    sudo apt-get install curl autossh screen

Make sure your user can log in to the remote server without a password

    ssh-copy-id user@remoteserver

Add the script to your crontab (`crontab -e`)

    * * * * * /path/to/tnnlr remoteserver

Obviously replace remoteserver with your own server
