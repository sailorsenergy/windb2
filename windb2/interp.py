#!/usr/bin/python
#
#
# Mike Dvorak
# Sailor's Energy
# mike@sailorsenergy.com
#
# Created: 2014-05-26
# Modified: 2016-12-20
#
#
# Description: Interpolation utilities for the WinDB WRF grid to a regularly gridded long, lat grid
#


def getCoordsOfReguarGridInWrfCoords(curs, domainNum, long, lat):
    """Calculates the WRF native coordinates of a regularly defined long, lat grid. The return values are meant
    to plug directly into the mpl_toolkits.basemap.interp function.
    
    @param curs: Psycopg2 cursor of the WinDB database
    @param domainNum: WinDB domain number
    @param long: 1D Numpy array of longitudes in the regular grid
    @param lat: 1D Numpy array of latitudes in the regular grid
    
    @return: wrfX -> 1D WRF native longitudinal coordinate
             wrfY  -> 1D WRF native latitudinal coordinate
             regGridInWrfX -> 2D WRF native longitudinal coordinate of the regular grid longitudinal coordinates
             regGridInWrfY -> 2D WRF native latitudinal coordinate of the regular grid latitudinal coordinates
    """
    import numpy as np
    import mpl_toolkits.basemap.pyproj as pyproj
    
    # Get the coordinates of the WRF grid in the native WRF projection
    sql = """SELECT generate_series(x.min::int,x.max::int,x.resolution::int) as x_coords
             FROM (SELECT min(st_x(geom)), max(st_x(geom)), resolution 
                   FROM horizgeom h, domain d
                   WHERE h.domainkey=d.key AND domainkey=""" + str(domainNum) + """ 
                   GROUP BY d.resolution) x
             ORDER BY x_coords"""
    curs.execute(sql)
    results = curs.fetchall()
    wrfX = np.array(results)
    sql = """SELECT generate_series(y.min::int,y.max::int,y.resolution::int) as y_coords
             FROM (SELECT min(st_y(geom)), max(st_y(geom)), resolution 
                   FROM horizgeom h, domain d
                   WHERE h.domainkey=d.key AND domainkey=""" + str(domainNum) + """ 
                   GROUP BY d.resolution) y
             ORDER BY y_coords"""
    curs.execute(sql)
    results = curs.fetchall()
    wrfY = np.array(results)
    
    # Get the SRID of the WRF domain
    sql= """SELECT proj4text FROM spatial_ref_sys WHERE srid=(SELECT st_srid(geom) FROM horizgeom WHERE domainkey=""" + str(domainNum) + """ LIMIT 1)"""
    curs.execute(sql)
    wrfProj4Str = curs.fetchone()[0]
    
    # Change the WRF coordinates of the regular long, lat grid
    # Great tutorial on Basemap Proj4 transformations here: http://all-geo.org/volcan01010/2012/11/change-coordinates-with-pyproj/
    wrfProj4 = pyproj.Proj(wrfProj4Str)
    longGrid, latGrid = np.meshgrid(long,lat)
    regGridInWrfX, regGridInWrfY = wrfProj4(longGrid, latGrid)
    
    return wrfX, wrfY, regGridInWrfX, regGridInWrfY
    