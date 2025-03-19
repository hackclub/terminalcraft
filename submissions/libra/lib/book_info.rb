# frozen_string_literal: true

require 'net/http'
require 'json'
require 'uri'
require 'tty-spinner'
require 'tty-table'

# Module to fetch metadata of books from it's ISBN using the OpenLibrary ISBN API
# The ISBN of a book can be obtained by either connecting a scanner to the computer and scanning
# the book's barcode (this is what libraries do!) or by entering in the numbers below the barcode on a book
module BookInfo
  ALLOWED_PROPERTIES = %w[
    title
    isbn_13
    isbn_10
    physical_format
    publish_date
    authors
  ].freeze

  # This is a bit odd, so I'll put a bit of an explanation of what it does here
  # The make_request function is self explanatory, it makes an HTTP request and returns a request object
  # However, the OpenLibrary /isbn/[isbn] endpoint does not return the data, it instead redirects
  # to a page that contains the data
  # Because of this, you need to first make a request to /isbn/[isbn], then make another request
  # to the given URL to redirect
  # The data is then parsed from JSON into a Ruby Hash object and subsequently returned
  # If you somehow got here and are reading this, send me a message or email because you're a real one :)

  def make_request(url)
    url = URI(url)

    http = Net::HTTP.new(url.host, url.port)
    http.use_ssl = true

    http.request(Net::HTTP::Get.new(url))
  end

  def book_info(isbn) # rubocop:disable Metrics/MethodLength
    spinner = TTY::Spinner.new(':spinner Loading book information...', format: :dots)
    spinner.auto_spin
    begin
      response = make_request(make_request("https://openlibrary.org/isbn/#{isbn}.json")['location'])
      spinner.stop('done!')
    rescue => e # rubocop:disable Style/RescueStandardError
      spinner.stop
      puts "Error while processing URI - #{e.message}. Is your ISBN correct?"
      return
    end
    parse_book_info(response.read_body)
  end

  def parse_book_info(json) # rubocop:disable Metrics/MethodLength,Metrics/AbcSize
    table = TTY::Table.new
    JSON.parse(json).each do |k, v|
      next unless ALLOWED_PROPERTIES.include?(k)

      k = k.capitalize
           .sub('_', ' ')
           .sub('Isbn ', 'ISBN-')
           .sub('Physical format', 'Format')
           .sub('Publish date', 'Published')
      v = v[0] if v.is_a?(Array)
      v = JSON.parse(make_request("https://openlibrary.org#{v['key']}.json").read_body)['name'] if k == 'Authors'
      table << [k, v]
    end
    puts table.render(:unicode)
  end
end
