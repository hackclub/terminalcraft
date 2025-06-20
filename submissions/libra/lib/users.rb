# frozen_string_literal: true

require 'tty-prompt'
require 'tty-table'

# Module for user handling (CRUD operations)
# This module assumes an already-functional PostgreSQL connection
module Users
  def users_prompt(conn) # rubocop:disable Metrics/CyclomaticComplexity,Metrics/AbcSize,Metrics/MethodLength
    prompt = TTY::Prompt.new
    options = [
      'Get all users',
      'Get user information',
      'Create user',
      'Update username',
      'Delete user'
    ]
    case prompt.select('Users', options)
    when 'Get all users'
      get_all_users_as_hash(conn)
    when 'Get user information'
      user_information = user_info(conn, prompt.ask('ID of user:').to_i)
      puts 'Error fetching user information' unless user_information
    when 'Create user'
      user = create_user(conn, prompt.ask('Name:'))
      puts "Created user #{user['name']} with ID #{user['id']}"
    when 'Update username'
      id = prompt.ask('ID of user to update:').to_i
      if user_exists?(conn, id)
        update_username(conn, id, prompt.ask('New username:'))
      else
        puts 'User not found'
      end
    when 'Delete user'
      if delete_user(conn, prompt.ask('ID of user to delete:').to_i)
        puts 'User deleted successfully'
      else
        puts 'Error deleting user'
      end
    end
  end

  def create_user(conn, name)
    # Create a new user given a Postgres connection object and the user's name, returns the id and name in a hash
    # note: the id is now a random 8 digit integer
    begin # rubocop:disable Style/RedundantBegin
      conn.exec("INSERT INTO users (id, name) VALUES (#{rand(10_000_000..99_999_999)}, '#{name}') RETURNING id, name")[0] # rubocop:disable Layout/LineLength
    rescue # rubocop:disable Style/RescueStandardError
      # ID collision error
      puts 'Collision error'
      puts 'Somehow, there are either 90 million entries in the database, or you got extremely lucky.'
      puts 'Send me a screenshot of this at @pbhak if you somehow got this error.'
    end
  end

  def get_all_users_as_hash(conn) # rubocop:disable Metrics/AbcSize
    # Get a hash of all users given a Postgres connection object
    res = conn.exec('SELECT * FROM users')
    table = TTY::Table.new(['ID', 'Name', 'Creation Date', '# Books'], [])
    all_fields = [res.field_values('id'), res.field_values('name'), res.field_values('creation_date'), res.field_values('books')] # rubocop:disable Layout/LineLength

    all_fields[0].length.times do |index|
      table << [all_fields[0][index], all_fields[1][index], all_fields[2][index].strftime('%m/%e/%y %r UTC%-:::z'), all_fields[3][index]] # rubocop:disable Layout/LineLength
    end

    puts table.render(:unicode)
  end

  def delete_user(conn, id)
    # Given a connection object and a user ID, attempt to delete the user with that ID.
    # Returns the ID of the deleted user if succesful, and false if otherwise (e.g. the user does not exist)
    return false unless user_exists?(conn, id)
    return id if conn.exec("DELETE FROM users WHERE id = #{id}").instance_of?(PG::Result)

    false
  end

  def user_info(conn, id)
    return false unless user_exists?(conn, id)

    res = conn.exec("SELECT * FROM users WHERE id = #{id}")[0]
    table = TTY::Table.new(['ID', 'Name', 'Creation Date', '# Books'], [])

    table << [res['id'], res['name'], res['creation_date'].strftime('%m/%e/%y %r UTC%-:::z'), res['books']]

    puts table.render(:unicode)
  end

  def user_exists?(conn, id)
    !conn.exec("SELECT COUNT(1) FROM users WHERE id = #{id}")[0]['count'].zero?
  end

  def update_username(conn, id, name)
    conn.exec("UPDATE users SET name = '#{name}' WHERE id = #{id}")
    puts 'User updated'
  end
end
