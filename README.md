# ClinkCrime
Display crime data within a one mile radius of CenturyLink Field.

This readme is a work in progress; right now it just has some notes for later when I write it out:

# Notes
- Using the v2.1 api, so the data source is up to an hour out of date (and has id pu5n-trf4 instead of 3k2p-39jp)
- when installing, make sure to manually set the libmemcached directory, like
    `LIBMEMCACHED=/opt/local pip install pylibmcv`
- some url escaping happening, but the parser still works fine
- the scraping is fragile, which is why I've isolated it, but I'd want it much more robust before trusting it in production
- event data is coming back as utc, crime data as local time
- named tuples to make it more readable
