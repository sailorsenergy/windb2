Wind Database version 2 (WinDB2)
======

# Contact
Mike Dvorak
[Sail Tactics](http://sailtactics.com)
[Contact](https://app.sailtactics.com/support)

# Overview

WinDB2 is a geospatial database and a suite of associated utilities to store geodata in a flexible manner. This code is a work in progress and a partial rewrite of the original WinDB software that Mike Dvorak used for his PhD research in offshore wind resource assessment at Stanford University. The database schema is written for PostgreSQL/PostGIS. The plotting, analysis, and utility scripts were written in Java, BASH, and Python. The currently implementation, WinDB2 is completely written in Python and PostgreSQL/PostGIS only.

# Current Status

As of 2016-06-13, the basic functionality from WinDB1 has been reimplmented using only Postgresql/PostGIS and Python 3.x, with backwards compatability for Python 2.7.

# Demo

WinDB2 is current driving the entire backend of the sailing-wind forecasting site [Sail Tactics](http://sailtactics.com). You an see an example interactive forecast of the forecast output for [San Francisco](https://app.sailtactics.com/forecasts/sample/us-sfbay).

By using WinDB(1) and WinDB2 on on the Sail Tactics website, it has been possible to keep all 200-m resolution WRF forecast for San Francisco Bay since February 2014 online in a single Amazon RDS PostgreSQL database, queryable on a moments notice. 

# Volunteers Wanted

The project is seeking volunteers to extend, test, document this code, and document use cases.

# Quick Start

## Creating a new WinDB2

### Dependencies
 
 Install the following libraries (or similar versions, depending on your operating system):
 * postegresql-9.5
 * postgresql-9.5-postgis-2.2
 * python3-psycopg2
 * python3-tz
 * python3-numpy

### Add the WinDB2 bin to your PATH

To run the WinDB2 scripts, all you need to do is add the WinDB2 `bin` directory to your path. The WinDB2 Python scripts take care of adding the appropriate locations to the `PYTHONPATH` automatically. 
```Shell
.../windb2 $ export PATH=$PWD/bin:$PATH
```
Make sure you don't have conflicting libraries in your `PYTHONPATH`, which will cause errors when you attempt to execute the scripts. You can easily verify there are no import errors by running `interpolate-wrf-file.py` without commands. If there are no import errors, you should see instructions printed on the screen about how to use the command. If you have errors trying to run a WinDB2 script, try running `unset PYTHONPATH` first.

### Running the create-windb2.py script

This assumes that you have a working PostgreSQL 9.x database setup on your system *and* that you have already [created a Postgres user with superuser privileges](https://www.postgresql.org/docs/9.5/static/app-createuser.html).

```Shell
.../windb2 $ export $PATH=$PWD/bin

$ create-windb2.py 
usage: create-windb2.py [-h] [-p PORT] dbhost dbuser dbname
create-windb2.py: error: the following arguments are required: dbhost, dbuser, dbname
/data/pycharm-workspace/windb2/schema/bin $ ./create-wind-db.sh localhost postgres test-windb2-1 

$ create-windb2.py localhost testuser windb2-testdb-1
Opening connection using dns: dbname=windb2-testdb-1 host=localhost user=testuser port=5432
database "windb2-testdb-1" does not exist... trying to create it
successfully created database "windb2-testdb-1"
Opening connection using dns: dbname=windb2-testdb-1 host=localhost user=testuser port=5432
Encoding for this connection is UTF8
Successfully created your WinDB2. Enjoy!
...
```
If this command completes without any errors, you will have successfully created an empty WinDB2.

## Postgres authentication

The WinDB2 commands require that you have automatic Postgres authentication set up in your account either via a `~/.pgpass` file (preferred) or using the PGUSER and PGPASS environment variables. This way, you never have to type in your password to connect to your WinDB2 nor do you have to leave your password in an unsecured file. Refer to [this Postgres documentation](http://www.postgresql.org/docs/current/static/libpq-pgpass.html) on how to set up your `~/.pgpass` file. Once you have successfully set up your Postgres authentication, you should be able to run the command `psql -h localhost -U postgres test-windb2-1` or similar without having to enter a password.

## Interpolating WRF wrfout files

WinDB2 is set up to accept meteorological variables at _height above ground level_. Because WRF native coordinates are on eta levels, WRF files need to be height-interpolated before inserting them into WinDB2.

### Setting up a configuration file

You need a configuration file named `windb2-wrf.conf` in your WRF directory containing the wrfout file to interpolate and insert the file into a WinDB2. You can find an example of this file in `.../config/`. This config file states which heights are to be interpolated and inserted. Currently, only the `UV` (wind) variable is supported. Support for temperature, pressure, and air density is coming soon.

### Running the interpolation command

Creating height interpolated files is easy:
 1. Set up your `windb2-wrf.conf` file as described above. Make sure there is a copy of this file in your directory containing the WRF out files.
 2. Interpolate the wrfout file(s) using `/tmp/windb2-example $ interpolate-wrf-file.py wrfout_d01`

## Inserting into the WinDB2

In order to configure your WinDB2 with your new WRF domain(s), you have to run a one-time command to set up a new WinDB2 domain. Use the `insert-windb2-file.py` command with the `-n` flag to create a new domain in the WinDB2.
```Shell
/tmp/windb2-example $ insert-windb2-file.py -n localhost postgres test-windb2-1 wrfout_d01_2016-02-14_00
Opening connection using dns: dbname=test-windb2-1 host=localhost user=postgres port=5432
...
Processing time:  2016-02-14T00:00:00.000Z
Inserted 9216, 10.0 height x,y wind points at 837.8181818181819 I/s
Inserted 9216, 60.0 height x,y wind points at 418.90909090909093 I/s
```

This command created a new WinDB2 domain #1 and inserted the wind fields at the 10 and 60 m height from this wrfout file for one time.

The ncfile argument is again a wildcard. Note that sometimes Unix/Linux filenames that contain colons (e.g. WRF files like `wrfout_d01_2016-02-14_00:00:00`) can get messed up with the shell trying to escape these colons. If you have problems with wrfout files not being found, try using *fewer* characters in the WRF filename (e.g. `wrfout_d01`) and let the wildcard functionality in Python script find the filenames.

You can verify the interpolated file was created with the `ls -ltr` command, which should show file(s) named `wrfout_d01_*-height-interp.nc`.

We can verify that WinDB2 domain was created inside the PostgreSQL database by inspecting the `domain` table:
```SQL
$ psql -U postgres test-windb2-1
psql (9.3.10)
Type "help" for help.

test-windb2-1=# SELECT * FROM domain;
 key |             name              | resolution | units | datasource | mask 
-----+-------------------------------+------------+-------+------------+------
   1 |  OUTPUT FROM WRF V3.6.1 MODEL |       3000 | m     | WRF        | 
(1 row)
```

We can also see that a table names `wind_1` contains all of the wind speed and direction data from the WRF file:
```Shell
 domainkey | geomkey |           t            | height |  speed   | direction 
-----------+---------+------------------------+--------+----------+-----------
         1 |       1 | 2016-02-14 00:00:00+00 |     10 |  11.0395 |       336
         1 |      97 | 2016-02-14 00:00:00+00 |     10 |  11.0583 |       336
         1 |     193 | 2016-02-14 00:00:00+00 |     10 |   11.086 |       336
         1 |     289 | 2016-02-14 00:00:00+00 |     10 |  11.1183 |       336
         1 |     385 | 2016-02-14 00:00:00+00 |     10 |  11.1517 |       336
         1 |     481 | 2016-02-14 00:00:00+00 |     10 |   11.186 |       336
         1 |     577 | 2016-02-14 00:00:00+00 |     10 |  11.2256 |       336
         1 |     673 | 2016-02-14 00:00:00+00 |     10 |  11.2668 |       336
         1 |     769 | 2016-02-14 00:00:00+00 |     10 |  11.3011 |       336
         1 |     865 | 2016-02-14 00:00:00+00 |     10 |  11.3215 |       335
         1 |     961 | 2016-02-14 00:00:00+00 |     10 |  11.3265 |       335
         1 |    1057 | 2016-02-14 00:00:00+00 |     10 |  11.3272 |       335
         1 |    1153 | 2016-02-14 00:00:00+00 |     10 |  11.3346 |       335
         1 |    1249 | 2016-02-14 00:00:00+00 |     10 |  11.3562 |       335
...
```

More WRF domains can be created in the WinDB2 by issuing the same command. Although it is not a requirement, it makes sense to keep the WinDB2 domain numbers consistent with the WRF domain numbers.

# Supported Models

Most of the functionality of WinDB(1) was directed at the NCAR's Weather Research and Forecasting Model (WRF). The original WinDB code aimed to rapidly post-process and validate WRF wind fields. The new version aims to be an extensible database for both atmospheric and ocean models.

# License

This code is licensed under the Gnu Public License version 3 (GPL3). You can read the license in the LICENSE.md file in the root directory of this repository.
