# frozen_string_literal: true

require 'pg'
require 'tty-table'

require_relative 'book_info'

# Module to handle checking out, renewal, and checking in books to users
module BookHandling
  def three_weeks_from_now
    (Time.now + (3 * 7 * 24 * 60 * 60)).strftime('%-m/%-e/%y')
  end

  def now
    Time.now.strftime('%-m/%-e/%y')
  end

  def book_exists?(isbn, conn)
    if conn.exec("SELECT COUNT(1) FROM books WHERE isbn = #{isbn}")[0]['count'].zero?
      puts 'Book not in library'
      return false
    end
    true
  end

  def add_book(isbn, conn)
    begin
      conn.exec("INSERT INTO books (isbn, checked_out_on, remaining_renews) VALUES (#{isbn}, NULL, NULL)")
    rescue PG::UniqueViolation
      puts 'Error: book already exists in database'
      return
    end

    puts "Book #{isbn} added"
  end

  def check_book_out(user_id, isbn, conn) # rubocop:disable Metrics/MethodLength
    # Check a book out to a user given the user's ID, the book ISBN, and a Postgres connection object
    # Note: queries here will be using upserts (update row instead of insert if it already exists)
    return false unless book_exists?(isbn, conn)
    begin
      conn.exec("INSERT INTO books (isbn, checked_out_to, checked_out_on, due_on, remaining_renews)
                VALUES (#{isbn}, #{user_id}, '#{now}', '#{three_weeks_from_now}', 3)
                ON CONFLICT (isbn)
                DO UPDATE SET isbn = EXCLUDED.isbn, 
                              checked_out_to = EXCLUDED.checked_out_to, 
                              checked_out_on = '#{now}',
                              due_on = EXCLUDED.due_on,
                              remaining_renews = 3")
      conn.exec("UPDATE users
                 SET books = books + 1
                 WHERE id = #{user_id}")
    rescue # rubocop:disable Style/RescueStandardError
      puts 'Error inserting row'
      return false
    end
    true
  end

  def book_status(isbn, conn)
    # Fetch the current information of a book from the database, given a book ISBN and a Postgres connection
    # Attempts to fetch the row from the DB with the given ISBN - if found, gives all current info about the book's status
    return false unless book_exists?(isbn, conn)

    book = conn.exec("SELECT * FROM books WHERE isbn = #{isbn}")[0]
    table = TTY::Table.new(['ISBN', 'Checked out to', 'Checked out on', 'Due on', 'Renews remaining'], [])

    BookInfo.book_info(isbn)

    table << [book['isbn'], book['checked_out_to'], book['checked_out_on'], book['due_on'], book['remaining_renews']]
    puts table.render(:unicode)
  end
end
