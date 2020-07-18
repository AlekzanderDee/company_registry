# Company registry

This is a research project that is focused on strings deduplication. Its goal is to implement a basic application, that
can store company names, and provide deduplication algorithms when a new company name gets added.

## Problem

An application needs to keep track of company names. There is no any additional info (like, some reg numbers), but only 
a company name. Service must implement a functionality that will detect, if a duplicate name gets added to the dataset.
This check (deduplication) should happen at the request-response time (not in the background).

## Solution

There are multiple ways to approach this problem. Each way has its pros and cons, and works better with different 
lengths of string (company names). Here are one of the existing solutions for checking the similarity between strings:
1. Python [difflib](https://docs.python.org/3.7/library/difflib.html) built-in module
2. [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
3. [Hamming distance](https://en.wikipedia.org/wiki/Hamming_distance)
4. [FuzzyWuzzy](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/) library

This project is utilizing the FuzzyWuzzy library to find if two strings might be representing the same value. It provides 
an API that allows to use different algorithms for scoring the similarity between two sequences. In the current version,
the service uses `token_set_ratio` method for scoring, but it requires further investigation to find the best algorithm for 
a different string lengths.

Overall, this service should serve as an adviser, rather than a decision maker. Instead of rejecting possible duplicate,
a user may be presented with a list of similar company names (with high similarity score) and make a decision about the
duplicate. 

One other approach would be to accept all incoming company names, and process deduplication in the background 
(using ML as one of the options). The processing results may be presented to a user, and she/he will make a decision.

## Implementation

This application is based on the [Django](https://www.djangoproject.com/) web-framework. 
It also uses [Django-REST](https://www.django-rest-framework.org/) web-framework for the REST implementation, 
and [FuzzyWuzzy](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/) library for scoring 
the similarity. You may find all requirements in the `requirements.txt` file. 

### Setup

You will need Python 3.7 to run this application on your machine. 
You should follow these steps to get application running:
1. Open a console and ensure you are in the project's directory
2. Create a new Python virtual environment: `python3 -m venv env`
3. Activate virtual environment: `source env/bin/activate`
4. Install all requirements: `pip install -r requirements.txt`
5. Check that Django is installed correctly: `python -m django --version`. This call should result in `3.0.8` output.
5. Create empty database: `python manage.py migrate` (this will create empty SQLite database with all required tables)
6. Run `dev` server on a localhost: `python manage.py runserver`

### Tests

You may use `python manage.py test` command to run tests. 

### Sending requests

Application provides a single endpoint for adding company names. You may use REST clients or console to send requests.
Currently, endpoint does not require authentication.

Valid request example (using `curl`):
```
curl -X POST \
  http://localhost:8000/add-company/ \
  -H 'Content-Type: application/json' \
  -d '{"company_name": "Unicorns Ltd."}'
```

Response:
```
{"company_name":"Unicorns Ltd.","duplicate":false}
```

## Notes:

There is a `companies.sqlite3` database file in the root directory. This database has ~ 10 000 records. 
In case you might want to use a prepopulated database, you may switch a database setting 
in the `company_registry/settings.py` file `DATABASES` section.

Also, there is another option in the same settings file, that you might want to change when experimenting 
with deduplication algorithms - `MAX_SIMILARITY_SCORE`. It represents the maximum similarity score, 
up to which two strings won't be considered as duplicates.
