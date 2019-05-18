# PixyShip

## Requirements
* Python 3.5
* NPM 6.1.0
* Docker

## Getting Started
1. Pip install the dev requirements: `pip install -r dev_reqs.txt`
1. Use Fabric to initialize the virtual env: `fab init_dev`
1. Install npm packages: `fab npm_install`
1. Create Postgres database in a container: `fab create_postgres`
1. Build the UI: `fab build_ui`

Initial data load:
`fab update_data`

To run locally:
1. Start the front-end dev environment: `fab ui`
2. Start the back end from the virtual environment (activate it) then `python run.py`

Access the web server at localhost:8080

## Deploying remotely
The deployment process targets a Ubuntu 16 server with ssh access.

First setup the remote from your local environment: 
`fab -h <host> setup`

Then the first and all subsequent deploys are done with: 
`fab -h <host> deploy`

