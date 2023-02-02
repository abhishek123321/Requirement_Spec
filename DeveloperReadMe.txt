## For all instructions below if your python version is not registered in bash 
## then where the keyword python is used use the full path to your python install

# Install venv using below in git terminal
python -m pip install --proxy="http://10.255.0.83:80" virtualenv

# Create a virtual environment with below in git terminal
python -m venv env

# Activate the environment with below in git terminal
source env/Scripts/activate

# Install requirements with below in git terminal
pip install --proxy="http://10.255.0.83:80" -r requirements.txt

## Updating the python requirements for the project
# With virtual environment running install any libraries you need.
python -m pip install --proxy="http://10.255.0.83:80" <MY_DEPENDENCY>

# Freeze the requirements into requirements.txt (ensure current path is top of project)
pip freeze > requirements.txt

# Push updated requirements.txt to the repo using git

## Setting up environment using dynamic config
# List of configs are available in the src.configs.py file.
# Set which config you wish to use by setting environment variable TRACEABILITYENVIRONMENT equal to the class name of the desired config
export TRACEABILITYENVIRONMENT=<DesiredConfig>

# Import config in your code with the following line
from src import config
# and extracting the config with the following line
config.get_config()