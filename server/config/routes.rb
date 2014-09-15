Rails.application.routes.draw do
  # views
  get '/', to: 'client#list'

  # api
  get '/a/request_port/:hostname', to: 'client#request_port'
end
