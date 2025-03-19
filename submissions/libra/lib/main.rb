# frozen_string_literal: true

require 'dotenv'
require 'tty-prompt'
require 'pg'

require_relative 'book_handling'
require_relative 'book_info'
require_relative 'users'

include BookHandling # rubocop:disable Style/MixinUsage
include BookInfo # rubocop:disable Style/MixinUsage
include Users # rubocop:disable Style/MixinUsage

def ctrlc
  puts
  puts 'Ctrl-C received, exiting...'
  exit 130
end

trap 'SIGINT' do # Control+C received
  ctrlc
end

print 'Establishing database connection.'

sleep 0.25
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
  sleep 0.25
  print '.'
end

puts 'Welcome to Libra!'

sleep 0.5

prompt = TTY::Prompt.new

# prompt for sign in?
options = [
  'Add book',
  'Book status',
  'Book information',
  'Check out',
  'Check in',
  'Renew',
  'Users'
]

begin
  loop do
    Gem.win_platform? ? system('cls') : system('clear')
    selected_option = prompt.select('What would you like to do?', options)

    case selected_option
    when 'Add book'
      add_book(prompt.ask('Book ISBN:'), conn)
    when 'Book status'
      book_status(prompt.ask('Book ISBN:'), conn)
    when 'Book information'
      book_info(prompt.ask('ISBN:'))
    when 'Check out'
      check_book_out(prompt.ask('User ID:'), prompt.ask('Book ISBN:'), conn)
    when 'Check in'
      # TODO: implement check in
    when 'Renew'
      # TODO: implement renew
    when 'Users'
      users_prompt(conn)
    end

    prompt.keypress('Press any key to continue...')

    puts
  end
rescue TTY::Reader::InputInterrupt
  # tty-reader throws a seperate exception when a Control+C is received
  ctrlc
end
