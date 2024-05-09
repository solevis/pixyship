from app import create_app

"""
This snippet is the WSGI entry point of the application. It creates the application instance and runs it.
The create_app function is defined in app/__init__.py
The app instance is created with the create_app function
The app instance is run with app.run()
"""


app = create_app()
