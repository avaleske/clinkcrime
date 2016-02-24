# ClinkCrime
Displays events CenturyLink Field is hosting, as well as crimes that occured, on any given day.

Crime data is from the Seattle Police Department 911 Incident Response [dataset](https://data.seattle.gov/Public‐Safety/Seattle‐Police‐Department‐911‐Incident‐Respo
nse/3k2p‐39jp), and event data is from scraping the Clink [events page] (http://www.trumba.com/calendars/centurylink-field-events-calendar).

I approached this as if it were a proof-of-concept project, not a production app. It's not nearly production ready.

<img src="screenshot.png?raw=true" width="600" >

## Caveats / Notes
- I'm using the SODA v2.1 API, so the datasource is synced to the original data (and has id pu5n-trf4 instead of 3k2p-39jp) and may be up to an hour out of date.
- It's not at all responsive. It's possible to make D3 charts responsive, but I didn't get to it. It loads on mobile, everything's just tiny.
- It works in Edge, but not really in IE. This may have been because my VM was really slow, but it's hard to tell.
- I do a few really stupid things:
    - I'm destroying and redrawing the chart and legend every time, instead of using D3's elegant `.update()` functions, because I still need to figure out how to use `.update()` when pulling data from `d3.csv()`. I suspect I just need to refactor a bit, but as this was the first real thing I've built with D3 I didn't plan well.
    - Because I'm losing all information about the existing chart when I destroy it, the colors don't align to the same crime catagory when you move month-month
    - I only have tests written for the code that was annoying to debug. If this were a production app it'd need much higher test coverage.
- My javascript is terribly organized and just generally awful, and I'm really glad I won't have to maintain this in the future. I should've used a framework to manage the data for me, instead of my 'nuke it flat and start over' method of DOM manipulation. Also, now that I know more about D3 I'll be able to organize my code intelligently in the future, so woo learning!
- The event scraping is really fragile. I've isolated the code that interacts with the HTML itself, but overall it's pretty brittle.
- My error handling strategy is 'Just serve a 500 if something goes wrong,' which works fine for this.
- I'm assuming that the crime datasource is giving me data in Seattle time. The API docs indicated to assume times were local.
- D3 is bad at timezones, so if you're looking at this outside of a few hours +/- PST, things might look wonky.
- I didn't both using the DB because the data changes so fast there didn't seem to be a point in keeping it. Also, I didn't want to write DB code.

## Installation
Ok, so after all that you want to install this? Alright:
### Locally:
To run this locally you'll need a few things.
- You'll want Python 2.7, virtualenv, virtualenvwrapper. Do the things [here](http://docs.python-guide.org/en/latest/starting/install/osx/) and [here](https://github.com/kennethreitz/python-guide/blob/master/docs/dev/virtualenvs.rst)
- You need the [Heroku Toolbelt](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
- You'll also need to have a local install of PostgreSQL. I used [Postgres.app](http://postgresapp.com/) because I'm lazy.
- You'll need to register for a Socrata API key [here](https://dev.socrata.com/register).
- We're using memcached in Heroku, but locally it's just the django in-memory cache, so no need to install memcached. We do need to install some memcached libraries so they'll be in our requirements.txt and picked up by Heroku, so you'll need to `brew install libmemcached`.

Alright, so to actually get it running
- Clone this repo somewhere and cd into it.
- Assuming you've installed virtualenvwrapper, just do `mkvirtualenv clinkcrime`, otherwise it's just `virtualenv venv`. (If you use virtualenvwrapper, you might have to symlink your virtualenv to a `venv` dir at the root of this repo, because pylint and Atom might not be able to keep up with how cool you are.
- Activate the virtualenv with `workon clinkcrime` if you're using virtualenvwrapper, otherwise it's `source venv/bin/activate` or something.
- Install the required pip packages with `pip install -r requirements.txt`. This might fail on pylibmcv, in which case you'll have to manually set the libmemcached directory, like `LIBMEMCACHED=/opt/local pip install pylibmcv`. Then run pip install again.
- Create a .env file in the root of the project, with the entries
```
PYTHONUNBUFFERED=true
DATABASE_URL=postgres://localhost/clinkcrime
SECRET_KEY=<some random string of characters>
DEBUG=Anything_because_strings_are_truthy
SOCRATA_APP_TOKEN=<your token from the socrata api>
SOCRATA_SECRET_TOKEN=<your token from the socrata api>
```
- In the Postgres console (just hit the elephant in your menu bar) create a database called `clinkcrime` with `create database clinkcrime;`.
- Setup the databases with `heroku local:run python manage.py syncdb`.
- Run the site with `heroku local` and go to `localhost:5000` to see it running.

### Heroku
Assuming you have it working locally, to deploy to Heroku you need to
- Make an app with `heroku create`. This should also add `heroku` as a git remote.
- Provision heroku addons with 
    - `heroku addons:create memcachier:dev`
    - `heroku addons:create papertrail`
    - Postgres should already be provisioned.
- Then desploy it with `git push heroku master` and your site should be live.
- Run syncdb with `heroku run python manage.py syncdb`
- You can go to your site with `heroku open`.
