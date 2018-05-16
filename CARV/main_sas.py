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

# This is stand-alone script and it can be run by copying it to Python command line in ArcGIS
# with proper parameters in INTRO section (change only cur_lin, raster and field_name!!!).
# For sript working with tool, see CARV_ToolScript.py

# --------------------------------------------------------------------------------------------------------#
#   INTRO
# --------------------------------------------------------------------------------------------------------#

# import moduless
import arcpy, os, sys

arcpy.env.overwriteOutput = True

# data
temp_loc = os.environ["Temp"]
temps = [(temp_loc + "\Points.shp"), (temp_loc + "\Points_values.shp")]
in_lines = "D:\KAMIENIEC\PROJEKT GIS\Dane\Odcinek2Poziomy.shp"
raster = "D:\KAMIENIEC\PROJEKT GIS\Dane\GeobazaTestowa.gdb\Spagtest2"
field_name = "XX1"


# --------------------------------------------------------------------------------------------------------#
#   DEFINE FUNCTIONS
# --------------------------------------------------------------------------------------------------------#

def clear_temps(temporaries):
    for in_data in temporaries:
        try:
            arcpy.Delete_management(in_data, "")
        except NameError:
            break


def read_cell_size(current_raster):
    # reads cell size of raster
    description = arcpy.Describe(current_raster)  # gets raster description
    print (description)
    cell_size = description.children[0].meanCellHeight  # gets cell size from description
    return cell_size


def get_error_code():
    # gets 6-number code from current exception
    e = sys.exc_info()[1]  # current exception
    error_message = e.args[0]
    error_code = error_message[6:12]
    return error_code


def create_points(lines, current_raster):
    points = temp_loc + "\Points.shp"  # path to temp file with points from line
    cell_size = read_cell_size(current_raster)  # gets raster cell_size

    dist = str(cell_size / 2) + " Meters"  # calculates distance between points as 1/2 of cell_size

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


def read_raster_values(lines, current_field_name, current_raster):
    points = temp_loc + "\Points.shp"
    pts_values = temp_loc + "\Points_values.shp"

    arcpy.AddField_management(lines, current_field_name, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    try:
        arcpy.gp.ExtractValuesToPoints_sa(points, current_raster, pts_values, "NONE", "VALUE_ONLY")
    except arcpy.ExecuteError:
        error_code = get_error_code()  # gets error code
        if error_code == '000725' or error_code == '000872':  # if code means that data already exist
            arcpy.Delete_management(pts_values, "")  # deletes old data
            arcpy.gp.ExtractValuesToPoints_sa(points, current_raster, pts_values, "NONE", "VALUE_ONLY")
        else:  # if it's other error, prints message
            print 'Process broken by error. Info below:'
            print error_message

    return pts_values


def create_id_list(cur_pkt):
    FID = 0
    for row in cur_pkt:
        FID += 1
        if row[0] not in id_list:
            id_list.append(row[0])
        values_list.append(row[1])
        matrix.append([row[0], row[1]])
    print id_list
    print values_list
    print matrix


def calculate_mean(id_list):
    for ID in id_list:
        sum_total = 0
        count = 0
        for row_q in matrix:
            FID = row_q[0]
            valu = row_q[1]
            if FID == ID:
                count += 1
                sum_total += valu
                print str(row_q[0]) + " = " + str(ID)
        raster_average = float(sum_total) / float(count)
        aver_list.append([ID, raster_average])
    print aver_list


def save_results(lines, field_name):
    fields = ["FID", field_name]
    with arcpy.da.UpdateCursor(lines, fields) as cur_lin:
        for line in cur_lin:
            for row in aver_list:
                ID = row[0]
                raster_average = row[1]
                if line[0] == ID:
                    line[1] = raster_average
                    cur_lin.updateRow(line)


create_points(in_lines, raster)
points_values_temp = read_raster_values(in_lines, field_name, raster)

# --------------------------------------------------------------------------------------------------------#
#   RUN FUNCTIONS
# --------------------------------------------------------------------------------------------------------#

# variables
raster_average = 0
id_list = []
values_list = []
matrix = []
aver_list = []

cur_points = arcpy.da.SearchCursor(points_values_temp, ["ORIG_FID", "RASTERVALU"])

create_id_list(cur_points)

calculate_mean(id_list)

save_results(cur_lin, field_name)

# --------------------------------------------------------------------------------------------------------#
#   CLEAN TEMP
# --------------------------------------------------------------------------------------------------------#

clear_temps(temps)
