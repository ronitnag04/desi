# DESI Database API <img src="static/Icon.png"  width="32" height="25">
Collaborators: Ronit Nagarapu, Stephen Bailey

Last Updated: 4/25/2023

## For Users
### Using the API
There are many endpoints available, which are listed in the [endpoints.txt](endpoints.txt) document. This document describes the general features and behavior of the endpoints, but more precise functionality and requirements are listed in the docstrings of the associated python method. These can be found in the appropriate .py file in the [api](api) folder. All endpoints use query parameters and GET method. 

There is also a graphical interface for some functionality; specifically, you can plot the tile-qa for a specific tile, and you can plot the spectra of specific targets. More detail is available in the [endpoints.txt](endpoints.txt) document and the .py files in the [gui](gui) folder.

### Common Uses
1) Find targets and redshifts by location: 
    - Look at the endpoints available at /api/loc

2) Display spectra graphically
    - Look at endpoints avaiable at /gui/display

3) Find information on a list of provided targetIDs
    - Use /gui/multispectra to plot or get a .fits file of spectra

4) Get raw .fits file for a set of targetIDs
    - Use /api/multispectra

5) Perform general simple queries on single tables
    - Use endpoint /api/table to perform queries
    - Use endpoint /api/table/columns to get more information on a specific table

## For Future Collaborators
### Workflow:
#### Setup
1) Pull this entire folder into your coding environment.
2) Start up Docker engine and docker login to the dockerhub repo where you will be storing your images, like [Harbor](https://registry.nersc.gov/harbor/projects). 
3) Log into your account on [Rancher](https://rancher2.spin.nersc.gov/dashboard/home).
4) Follow the steps in the [spin_setup.txt](spin_setup.txt) document to initialize your workflow to run the docker image
#### Development
5) Regularly commit your changes to git, and make sure to update the version of your docker tag each time you make a major change or start working on a new feature.
6) To push changes to the Harbor dockerhub, type the following commands into the terminal. NOTE: the url to your repo may be different
   ```
   LATEST="registry.nersc.gov/desi/\<your username\>/database-api:latest"
   TAG="registry.nersc.gov/desi/\<your username\>/database-api:\<version\>"
   docker build -t $TAG . && docker tag $TAG $LATEST && docker push $TAG && docker push $LATEST 
   ```
7) Make sure to update the [requirements.txt](requirements.txt) file if you need to import python packages that are not available by default with python:3.10-buster image.
8) New .html pages should go into the [templates](templates) folder
9)  If you create new folders or python files, make sure to update the imports in [app.py](app.py) accordingly.
10) Add new endpoints to the [endpoints.txt](endpoints.txt) document, and update the [Common Uses](#common-uses) section with any major feature additions.

### Development Notes:
- Setting up new python files:
  - New python files must import the flask app and SQLAlchemy access appropriately. 
  ```
  import desispec.database.redshift as db
  specprod = 'fuji'
  postgresql = db.setup_db(schema=specprod, hostname='nerscdb03.nersc.gov', username='desi')
  from app import app
  ```
-  Endpoints and Query Parameters:
   -  All endpoints current use query parameters to allow users to provide specifications. Lines 3 and 4 must be at the top of any endpoint method, before the parameters are used with SQLAlchemy. 
   ```
   from flask import request
   from api.utils import parseParams 
   params = request.args.to_dict()
   parseParams(params)
   ```
   - NOTE: parseParams is not fully tested, and there is room for future improvements in security
   - See [api.utils.py](api/utils.py) for more useful methods
 - Validation and Errors:
   - When designing methods, make sure to validate your inputs before using them. When performing any queries, file searches, etc. validate the amount of items you expect in return. These are just two examples, there are many other situations to validate. 
   - When you are validating in helper methods, raise ValueError when you encounter invalid items, with messages describing the issue. These errors should be handled in a try except block in the endpoint that uses them, and the error should be returned as a jsonified string to the user. 
   - If you wish to raise and error that should not be passed back to the user, use an assert statement. Note however, that this will just result in a 500 response code to the user, which may not help them resolve the issue.
 - Security:
   - Never add the .pgpass file containing the password to the desi database
   - Never store your github password or any secrets in files in this repo.
   - If secrets must be stored locally, make sure to add them immediately to a .gitignore file
 - Examples of these general practices can be found in the python files

## File Tree:
```
📦database-api
 ┣ 📂api
 ┃ ┣ 📜generic.py
 ┃ ┣ 📜loc.py
 ┃ ┣ 📜multispectra.py
 ┃ ┗ 📜utils.py
 ┣ 📂gui
 ┃ ┣ 📜display.py
 ┃ ┣ 📜multispectra.py
 ┃ ┗ 📜utils.py
 ┣ 📂static
 ┃ ┣ 📜favicon.ico
 ┃ ┣ 📜Icon.png
 ┃ ┗ ...
 ┣ 📂templates
 ┃ ┗ 📜multispectra.html
 ┣ 📜app.py
 ┣ 📜Dockerfile
 ┣ 📜endpoints.txt
 ┣ 📜README.md
 ┣ 📜requirements.txt
 ┗ 📜spin_setup.txt
 ```

## Development Warning
NOTE: This API is still in development. Please report any errors and bugs to ronitnag04@berkeley.edu, and also send any comments, questions, or suggestions.
