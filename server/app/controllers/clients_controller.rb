class ClientsController < ApplicationController
  def list
    @clients = Client.all
  end

  def ping
  end

  def edit
    @client = Client.find(params[:id])
  end

  def update
    @client = Client.find(params[:id])
    @client.update_attributes(client_params)
    @client.restart = true
    @client.save
    redirect_to '/'
  end

  def request_port
    client = Client.find_or_create_by(hostname: params[:hostname])
    client.assign_port
    client.last_report = Time.now
    client.update_attributes(api_params)
    client.user = params[:user] if client.user.nil?
    restart = client.restart
    client.restart = false

    if client.save
      render text: "#{client.assign_port};#{restart};#{client.user};#{client.update_configs}"
    else
      raise :hell
    end
  end

  def configs
    arr = ['#tnnlr - keep this at the bottom']
    Client.all.each do |c|
      arr << "Host #{c.hostname}"
      arr << "  ProxyCommand ssh %h nc localhost #{c.port}"
      arr << "  User #{params[:user]}"
      arr << "  HostKeyAlias #{c.hostname}"
      arr << "  Hostname #{request.host}"
      arr << nil
    end

    render plain: arr.join("\n")
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

  private

  def client_params
    params.require(:client).permit(:user, :update_configs)
  end

  def api_params
    params.permit(:local_ip, :outside_ip, :uptime, :dfh, :free, :ifconfig, :route)
  end
end
