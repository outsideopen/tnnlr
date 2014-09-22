class ClientsController < ApplicationController
  def list
    @clients = Client.all
  end

  def ping
  end

  def edit
    @client = Client.find(params[:id])
  end

  def request_port
    client = Client.find_or_create_by(hostname: params[:hostname])
    client.assign_port
    client.last_report = Time.now
    client.local_ip = params[:local_ip]
    client.outside_ip = params[:outside_ip]
    restart = client.restart
    client.restart = false

    if client.save
      render text: "#{client.assign_port};#{restart}"
    else
      raise :hell
    end
  end

  def configs
    arr = []
    Client.all.each do |c|
      arr << "Host #{c.hostname}"
      arr << "ProxyCommand ssh %h nc localhost #{c.port}"
      arr << "User #{params[:user]}"
      arr << "HostKeyAlias #{c.hostname}"
      arr << "Hostname #{request.host}"
      arr << nil
    end

    render text: arr.join("<br>\n")
  end

  def restart
    client = Client.find(params[:id])
    client.restart = true
    client.save
    redirect_to '/'
  end

  def destroy
    client = Client.find(params[:id])
    client.destroy
    redirect_to '/'
  end
end
