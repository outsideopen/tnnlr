class ClientController < ActionController::Base
  def list
    @clients = Client.all
  end

  def ping
  end

  def request_port
    client = Client.find_or_create_by(hostname: params[:hostname])
    client.assign_port
    client.last_report = Time.now

    if client.save
      render text: client.assign_port
    else
      raise :hell
    end
  end
end
