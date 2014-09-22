class CreateClients < ActiveRecord::Migration
  def change
    create_table :clients do |t|
      t.string :hostname
      t.string :outside_ip
      t.string :local_ip
      t.string :port
      t.string :user
      t.boolean :restart, default: false
      t.datetime :last_report
    end
  end
end
