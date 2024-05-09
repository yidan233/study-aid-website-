from website import create_app

# create app function in __init__

app = create_app()
if __name__ == '__main__': # only run the web server if you run this line 
  app.run(debug = True)