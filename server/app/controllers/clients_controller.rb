class ClientsController < ActionController::Base
  def list
    @clients = Client.all
  end

  def ping
  end

  def request_port
    client = Client.find_or_create_by(hostname: params[:hostname])
    client.assign_port
    client.last_report = Time.now
    client.local_ip = params[:local_ip]
    client.outside_ip = params[:outside_ip]

    if client.save
      render text: client.assign_port
    else
      raise :hell
    end
  end

  def release
    client = Client.find(params[:id])
    client.destroy
    redirect_to '/'
  end
end
