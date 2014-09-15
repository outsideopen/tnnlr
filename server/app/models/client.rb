class Client < ActiveRecord::Base
  def assign_port
    self.port = port || rand(1000)+15000
  end
end
