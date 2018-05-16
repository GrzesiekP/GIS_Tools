# coding=utf-8
'''
#--------------------------------------------------------------------------------------------------------#
Version 1.2
Created: 2016-09-17
Python 2.7
ArcGIS 10.4.1
Author: Grzegorz Pawlowski grzechu435@gmail.com
#--------------------------------------------------------------------------------------------------------#
'''

# This is script, which can be imported into tool.

# --------------------------------------------------------------------------------------------------------#
#   INTRO
# --------------------------------------------------------------------------------------------------------#

# import modules
import arcpy
import os
import sys

arcpy.env.overwriteOutput = True

# data
temp_loc = os.environ["Temp"]
temps = [(temp_loc + "\Points.shp"), (temp_loc + "\Points_values.shp")]
cur_lin = arcpy.GetParameterAsText(0)
raster = arcpy.GetParameterAsText(1)
field_name = arcpy.GetParameterAsText(2)

if len(field_name) > 10:
    field_name = field_name[:10]


# --------------------------------------------------------------------------------------------------------#
#   DEFINE FUNCTIONS
# --------------------------------------------------------------------------------------------------------#

def clear_temps(temporaries):
    """

    :param temporaries:
    """
    for in_data in temporaries:
        try:
            arcpy.Delete_management(in_data, "")
        except NameError:
            break


def read_cell_size(cur_raster):
    """

    :param cur_raster:
    :return:
    """
    # reads cell size of raster
    description = arcpy.Describe(cur_raster)  # gets raster description
    cell_size = description.children[0].meanCellHeight  # gets cell size from description
    return cell_size


def get_error_code():
    """

    :return:
    """
    # gets 6-number code from current exception
    e = sys.exc_info()[1]  # current exception
    error_message = e.args[0]
    error_code = error_message[6:12]
    return error_code, error_message


def create_points(lines, cur_raster):
    """

    :param lines:
    :param cur_raster:
    :return:
    """
    points = temp_loc + "\Points.shp"  # path to temp file with points from line
    cell_size = read_cell_size(cur_raster)  # gets raster cellsize

    dist = str(cell_size / 2) + " Meters"  # calculates distance between points as 1/2 of cellsize

    temp_lines = temp_loc + "\\temp_lines"
    arcpy.FeatureClassToFeatureClass_conversion(lines, temp_loc, "temp_lines", "", "", "")
    arcpy.Densify_edit(lines, "DISTANCE", dist, "1 Meters", "10")  # densifies line vertices to dist

    try:
        arcpy.FeatureVerticesToPoints_management(lines, points, "ALL")  # convert vertices from lines to points
    except arcpy.ExecuteError:
        error_code = get_error_code()  # gets error code
        if error_code == '000725' or error_code == '000872':  # if code means that points already exist
            arcpy.Delete_management(points, "")  # deletes old points
            arcpy.FeatureVerticesToPoints_management(lines, points, "ALL")  # convert vertices again
        else:  # if it's other error, prints message
            print 'Process broken by error. Info below:'
            print error_message

    arcpy.Delete_management(temp_lines, "")

    return points  # returns path to created points


def read_raster_values(lines, cur_field_name, cur_raster):
    """

    :param lines:
    :param cur_field_name:
    :param cur_raster:
    :return:
    """
    my_points = temp_loc + "\Points.shp"
    pts_values = temp_loc + "\Points_values.shp"

    arcpy.AddField_management(lines, cur_field_name, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    try:
        arcpy.gp.ExtractValuesToPoints_sa(my_points, cur_raster, pts_values, "NONE", "VALUE_ONLY")
    except arcpy.ExecuteError:
        error_code, error_message = get_error_code()  # gets error code
        if error_code == '000725' or error_code == '000872':  # if code means that data already exist
            arcpy.Delete_management(pts_values, "")  # deletes old data
            arcpy.gp.ExtractValuesToPoints_sa(my_points, cur_raster, pts_values, "NONE", "VALUE_ONLY")
        else:  # if it's other error, prints message
            print 'Process broken by error. Info below:'
            print error_message

    return pts_values


def create_id_list(cur_pt):
    """

    :param cur_pt:
    """
    FID = 0
    for row in cur_pt:
        FID += 1
        if row[0] not in id_list:
            id_list.append(row[0])
        values_list.append(row[1])
        matrix.append([row[0], row[1]])
    print id_list
    print values_list
    print matrix


def calculate_mean(cur_id_list):
    """

    :param cur_id_list:
    """
    for ID in cur_id_list:
        sum_total = 0
        amount = 0
        for row_q in matrix:
            FID = row_q[0]
            value = row_q[1]
            if FID == ID:
                amount += 1
                sum_total += value
                print str(row_q[0]) + " = " + str(ID)
        average_of_raster = float(sum_total) / float(amount)
        aver_list.append([ID, average_of_raster])
    print aver_list


def save_results(lines, cur_field_name):
    """

    :param lines:
    :param cur_field_name:
    """
    fields = ["FID", cur_field_name]
    with arcpy.da.UpdateCursor(lines, fields) as cursor:
        for line in cursor:
            for row in aver_list:
                ID = row[0]
                average_of_raster = row[1]
                if line[0] == ID:
                    line[1] = average_of_raster
                    cursor.updateRow(line)


create_points(cur_lin, raster)
points_values_temp = read_raster_values(cur_lin, field_name, raster)

# --------------------------------------------------------------------------------------------------------#
#   RUN FUNCTIONS
# --------------------------------------------------------------------------------------------------------#

# variables
raster_average = 0
id_list = []
values_list = []
matrix = []
aver_list = []

cur_pkt = arcpy.da.SearchCursor(points_values_temp, ["ORIG_FID", "RASTERVALU"])

create_id_list(cur_pkt)

calculate_mean(id_list)

save_results(cur_lin, field_name)

# --------------------------------------------------------------------------------------------------------#
#   CLEAN TEMP
# --------------------------------------------------------------------------------------------------------#

clear_temps(temps)
