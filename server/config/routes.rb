Rails.application.routes.draw do
  # views
  get '/', to: 'clients#list'
  get '/restart/:id', to: 'clients#restart', as: 'restart'
  post '/configs', to: 'clients#configs', as: 'configs'
  resources :clients, only: ['edit', 'update', 'destroy']

  # api
  get '/a/request_port/:hostname', to: 'clients#request_port', :constraints => { :hostname => /[\w+\.]+/ }
end
