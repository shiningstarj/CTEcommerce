# Auron
Simple eCommerce web app

To set up simply run the following from the root of the repo:
```
export (set in Windows environment) FLASK_APP=auron
pip install -e .
flask initdb
flask populatedb
flask run
```

Don't forget to log in to use the cart functionality.