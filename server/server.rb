require 'sinatra'
require 'sinatra/activerecord'

set :database, {adapter: 'sqlite3', database: 'db.sqlite3'}

get '/' do
  "hello world"
end
