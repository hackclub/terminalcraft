# frozen_string_literal: true

require 'dotenv'
require 'pg'

print 'Establishing database connection.'

SLEEP_TIME = 0.25

sleep SLEEP_TIME
print '.'

begin
  Dotenv.load('.env')
  conn = PG.connect(dbname: ENV['dbname'], user: ENV['psql_username'], password: ENV['psql_password'])
  conn.type_map_for_results = PG::BasicTypeMapForResults.new(conn)
rescue # rubocop:disable Style/RescueStandardError
  puts "\nError connecting to database. Check your PostgreSQL credentials."
  exit
end

2.times do
  sleep SLEEP_TIME
  print '.'
end
puts "\n"

begin
  conn.exec("CREATE TABLE users (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              creation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
              books INTEGER DEFAULT 0)")
rescue PG::DuplicateTable
  puts 'Table users already exists'
end

begin
  conn.exec("CREATE TABLE books (
              isbn BIGINT PRIMARY KEY,
              checked_out_to INTEGER,
              checked_out_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
              due_on TIMESTAMP WITH TIME ZONE,
              remaining_renews INTEGER DEFAULT 3)")
rescue PG::DuplicateTable
  puts 'Table books already exists'
end
