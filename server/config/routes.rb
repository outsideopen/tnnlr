Rails.application.routes.draw do
  # views
  get '/', to: 'clients#list'
  get '/release/:id', to: 'clients#release', as: 'release'
  get '/restart/:id', to: 'clients#restart', as: 'restart'

  # api
  get '/a/request_port/:hostname', to: 'clients#request_port', :constraints => { :hostname => /[\w+\.]+/ }
end
