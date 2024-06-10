##################
# CircleGPSPoints
# Given a centre, calculate a circle of gps co-ords around this using an inverse haversine formula.
# In other words, we solve a direct problem of deteriming a destination given distance & bearing
#
#
# Designed to determine co-ordinates delineating a RQZ/mobile-no-go zone around a radio observatory.
# See http://www.movable-type.co.uk/scripts/latlong.html
# https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing
# ESL
##################

import sys                                                          # for the usual
from xml.etree.ElementTree import Element, SubElement, ElementTree  # to generate a xml-style .gpx file
from geopy import Point                                             # geopy's encoding of locations
from geopy.distance import geodesic                                 # geodesic = karney(WGS-84)


def create_text_file(points, file_name="test_circle"):
    """Save the list of points as a csv-style text file."""

    # add appropriate extension:
    file = "%s.txt" % file_name

    # open and write:
    with open(file, 'w') as file:
        for lat, long in points:
            file.write(f"{lat}, {long}\n")


def create_gpx_file(points, file_name="test_circle"):
    """I asked chatgpt to write me a function to save list as gpx file...
    I have never used them so not really sure about this.
    But seems to load up ok... Tested with Organic maps."""

    # add appropriate extension:
    file = "%s.gpx" % file_name

    # hmmm
    gpx = Element('gpx', version="1.0", creator="ESL")
    trk = SubElement(gpx, 'trk')
    name = SubElement(trk, 'name')
    name.text = '%s' % file_name
    trkseg = SubElement(trk, 'trkseg')

    for lat, lon in points:
        SubElement(trkseg, 'trkpt', lat=str(lat), lon=str(lon))

    tree = ElementTree(gpx)

    tree.write(file, xml_declaration=True, encoding='utf-8')

################


def generate_circle(centre, radius, num_points=360):
    """Create a list of co-ordinates defining a circle around some centre.
     Takes in a central co-ordinate, a radius [metres] and number of points/resolution"""

    # initialise empty points list:
    points_list = []

    # encode the lat, long of centre into geopy Point
    centre_point = Point(centre)

    # convert radius to kilometres
    radius = radius / 1000.0

    # loop through the number of points:
    for i in range(num_points + 1):

        # get true bearing (ie degrees clockwise from north) for each point
        dtheta = float(i) * 360.0 / num_points

        # call the direct geodesic computation:
        d = geodesic(radius).destination(point=centre_point, bearing=dtheta)

        # extract the lat, long
        point = [d.latitude, d.longitude]

        # strip to <cut_off> decimal places for consistency (what's the loss of accuacy w this?)
        cut_off = 6
        point = [round(point[0], cut_off), round(point[1], cut_off)]

        #add point to list
        points_list.append(point)

    # done:
    return points_list


def sanity_check(centre, radius, coord_list):
    """Prints the results of the indriect formula between the centre and each point of the circle."""

    for lat, long in coord_list:
        point = [lat, long]
        distance = geodesic(radius).measure(centre, point)
        print(distance)


def main_function():
    """Load in parameters and run the component functions."""

    # some debug:
    sanity_check_switch = True                      # to print to standard output the recalculated radii
    test_point = [78.9239722, 11.9233056]           # my bedroom, in DD (ie deciaml) (should it be DMS (ie sexagesimal)?)

    # main parameters:
    centre = test_point                             # lat, long
    radius = 900                                    # in metres

    # get the circle of points
    coord_list = generate_circle(centre, radius)

    # just for fun
    if sanity_check_switch:
        sanity_check(centre, radius, coord_list)

    # create 'descriptive' file name
    file_name = "%sm_RQZ_Circle_w_Centre_%.3f_%.3f" % (radius, centre[0], centre[1])

    # save the circle of points
    create_text_file(coord_list, file_name)         # as csv-style text file
    create_gpx_file(coord_list, file_name)          # as .gpx file...


if __name__ == '__main__':

    try:
        main_function()
    except Exception as e:
        print(e)
        sys.exit(1)

#