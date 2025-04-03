# libra
A CLI library database system that can be used to check information on books as well as check them out/check them in to and from users.

## why a library management system?
Not only can I actually track performance on my own book collection, but I think it's a relatively unique project idea, so why not?

Plus, since this is already a Ruby project, I can probably expand with Rails sometime in the near future so that's cool

## how to use locally?
1. Run `bundle` in the root directory of the project to install all required dependencies
2. Make sure your PostgreSQL server is running
3. Make a .env file in the root of the project with the following properties:
```
dbname = [your PostgreSQL database name]
psql_username = [your PostgreSQL username]
psql_password = [your PostgreSQL password]
```
4. Run `lib/init.rb` to create needed tables
5. Use Libra through `lib/main.rb`

## contributing
Not sure why you would want to contribute to this, but if you want to pull requests will always be encouraged! You can also contact me to report bugs.