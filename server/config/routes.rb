Rails.application.routes.draw do
  # views
  get '/', to: 'clients#list'
  get '/release/:id', to: 'clients#release', as: 'release'

  # api
  get '/a/request_port/:hostname', to: 'clients#request_port'
end
