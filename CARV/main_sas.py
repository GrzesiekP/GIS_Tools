'''
#--------------------------------------------------------------------------------------------------------#
Version 1.2
Created: 2016-09-17
Python 2.7
ArcGIS 10.4.1
Author: Grzegorz Pawlowski grzechu435@gmail.com
#--------------------------------------------------------------------------------------------------------#
'''

#--------------------------------------------------------------------------------------------------------#
#   INTRO
#--------------------------------------------------------------------------------------------------------#

#import moduless
import arcpy, os, sys

#data
temp_loc = os.environ["Temp"]
temps = [(temp_loc + "\Points.shp"), (temp_loc + "\Points_values.shp")]
cur_lin = "D:\KAMIENIEC\PROJEKT GIS\Dane\Odcinek2Poziomy.shp"
raster = "D:\KAMIENIEC\PROJEKT GIS\Dane\GeobazaTestowa.gdb\Spagtest2"
field_name = "XX1"

#--------------------------------------------------------------------------------------------------------#
#   DEFINE FUNCTIONS
#--------------------------------------------------------------------------------------------------------#

def ClearTemps(temps):
    for in_data in tempy:
        try:
            arcpy.Delete_management(in_data, "")
        except NameError:
            break

def ReadCellSize(raster):
    #reads cell size of raster
    description = arcpy.Describe(raster) #gets raster description
    cellsize = description.children[0].meanCellHeight #gets cell size from description
    return cellsize

def GetErrorCode():
    #gets 6-numer code from current exception
    e = sys.exc_info()[1] #current exception
    error_message = e.args[0]
    error_code = error_message[6:12]
    return error_code

def CreatePoints(lines, raster):

    points = temp_loc + "\Points.shp" #path to temp file with points from line
    cellsize = ReadCellSize(raster) #gets raster cellsize
    
    dist = str(cellsize / 2) + " Meters" #calculates distance between points as 1/2 of cellsize
    arcpy.Densify_edit(lines, "DISTANCE", dist, "1 Meters", "10") #densifies line vertices to dist

    try:
        arcpy.FeatureVerticesToPoints_management(lines, points, "ALL") #convert vertices from lines to points
    except arcpy.ExecuteError:
        error_code = GetErrorCode() #gets error code
        if error_code == '000725' or error_code == '000872': #if code means that points already exist
            arcpy.Delete_management(points, "") #deletes old points
            arcpy.FeatureVerticesToPoints_management(lines, points, "ALL") #convert vertices again
        else: #if it's other error, prints message
            print 'Process broken by error. Info below:'
            print error_message

    return points #returns path to created points

def ReadRasterValue(lines, field_name, raster):

    punkty = temp_loc + "\Points.shp"
    pts_values = temp_loc + "\Points_values.shp"

    arcpy.AddField_management(lines, field_name, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    try:
        arcpy.gp.ExtractValuesToPoints_sa(punkty, raster, pts_values, "NONE", "VALUE_ONLY")
    except arcpy.ExecuteError:
        error_code = GetErrorCode() #gets error code
        if error_code == '000725' or error_code == '000872': #if code means that data already exist
            arcpy.Delete_management(pts_values, "") #deletes old data
            arcpy.gp.ExtractValuesToPoints_sa(punkty, raster, pts_values, "NONE", "VALUE_ONLY")
        else: #if it's other error, prints message
            print 'Process broken by error. Info below:'
            print error_message

    return pts_values

def CreateIdList(cur_pkt):
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

def CalculateMean(id_list):
    for ID in id_list:
        suma = 0
        ilosc = 0
        for row_q in matrix:
            FID = row_q[0]
            valu = row_q[1]
            if FID == ID:
                ilosc += 1
                suma += valu
                print str(row_q[0]) + " = " + str(ID)
        raster_average = float(suma)/float(ilosc)
        aver_list.append([ID,raster_average])
    print aver_list

def SaveResults(cur_lin, field_name):
    fields = ["FID", field_name]
    with arcpy.da.UpdateCursor(linie, fields) as cur_lin:
        for line in cur_lin:
            for row in aver_list:
                ID = row[0]
                raster_average = row[1]
                if line[0] == ID:
                    line[1] = raster_average
                    cur_lin.updateRow(line)

CreatePoints(linie, raster)
points_values_temp = ReadRasterValue(linie, field_name, raster)

#--------------------------------------------------------------------------------------------------------#
#   RUN FUNCTIONS
#--------------------------------------------------------------------------------------------------------#

#zmienne
raster_average = 0
id_list = []
values_list = []
matrix = []
aver_list = []

cur_pkt = arcpy.da.SearchCursor(points_values_temp, ["ORIG_FID", "RASTERVALU"])

CreateIdList(cur_pkt)
    
CalculateMean(id_list)

SaveResults(cur_lin, field_name)

#--------------------------------------------------------------------------------------------------------#
#   CLEAN TEMP
#--------------------------------------------------------------------------------------------------------#
            
ClearTemps(temps)