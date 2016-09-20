#Some comments

#import modules
import arcpy, os, sys
from arcpy import env

#allow overwrite
env.overwriteOutput = True

#define an output file and templocation
in_path = 'D:\\KAMIENIEC\\PROJEKT GIS\\Skrypty\\PetrelDEVTo3DLine\\ot.txt'
temploc = os.environ['Temp']

to_remove = []

#open a petrel file
d = open(in_path, 'r')

#open the output file
out_path = 'D:\\KAMIENIEC\\PROJEKT GIS\\Skrypty\\PetrelDEVTo3DLine\\wynik.txt' # ZMIEEEEEN NAAAAAAAAAAAAA TEMPPPPPPPPPPPP!!!!!!!!!!!!! #$!@$!#
o = open(out_path, 'w')

#write headers to the out file
o.write('MD,X,Y,Z,TVD,DX,DY,AZIM,INCL\n')

#define a function, which changes characters from a list to commas
def ReplaceFromList(my_string, my_list):
    for ch in my_list:
        my_string = my_string.replace(ch, ',')
    return my_string

#define a function finding empty lines
def CheckLine(string):
    cond = string != "" and string != "\n" and string != "," and string!= " " and string != "\t" and string != "	" 
    return cond
#define funtion writing only anot-empty lines to a list
def FileToList(file):
    correct_lines = []
    for line in file:
        if CheckLine(line) == True:
            correct_lines.append((str(line)).replace("\n", ""))
    return correct_lines

#function skips the header
def RemoveHeader(lines_list):
    c = 0
    no_header_ll = []
    for l in lines_list:
        c += 1
        if c <= 13:
            pass
        elif c > 13:
            no_header_ll.append(l)
    return no_header_ll

#change the petrel file to a list of lines
lines_list = RemoveHeader(FileToList(d))

#chars to be replaced in each line
bad_chars = ([' ', '  ', '   ', '	' ,'    ', '     ', '      '])[::-1]

#rewrite the file in a new structure
for l in lines_list:
    if CheckLine(l) == True:
        cl = ReplaceFromList(l, bad_chars)
        if not str(cl[1]) == ",":
            if not cl == l[-2]:
                o.write(cl + "\n")
            else:
                o.write(cl)

#close in and out files
o.close()
d.close()

to_remove.append(out_path)

#==================================================================#

#define temp variables and locations
out_event_layer = temploc + 'TempEvLay.shp'
out_loc = temploc + '\\'
out_fc = 'Well_Points'
well_track = 'Well_Track'
env.workspace = temploc

#CRS to be chosen as parameter!
CRS = "PROJCS['ETRS_1989_UWPP_1992',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Gauss_Kruger'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',-5300000.0],PARAMETER['Central_Meridian',19.0],PARAMETER['Scale_Factor',0.9993],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"

#create and event layer
arcpy.MakeXYEventLayer_management(out_path, 'X', 'Y', out_event_layer, CRS, 'Z')
to_remove.append(out_event_layer)

#convert the EL to a FC
arcpy.FeatureClassToFeatureClass_conversion(out_event_layer, out_loc, out_fc, "", """MD "MD" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,MD,-1,-1;X "X" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,X,-1,-1;Y "Y" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,Y,-1,-1;Z "Z" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,Z,-1,-1;TVD "TVD" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,TVD,-1,-1;DX "DX" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,DX,-1,-1;DY "DY" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,DY,-1,-1;AZIM "AZIM" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,AZIM,-1,-1;INCL "INCL" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,INCL,-1,-1""", "")

#should be a path in order to get CRS
points = env.workspace + '\\' + 'Well_Points'

#create 3D FC
arcpy.CreateFeatureclass_management(env.workspace, '3D_line', 'POLYLINE', "", 'DISABLED', 'ENABLED', points)

#draw polyline
array = arcpy.Array()

for row in arcpy.da.SearchCursor(punkty, ("OID@", "SHAPE@","Z")):
    
    print 'Point with ID: ', row[0]
    
    x = row[1].centroid.X
    y = row[1].centroid.Y
    z = row[1].centroid.Z

    point = arcpy.Point(x,y,z)

    array.append(point)

polyline_3d = arcpy.Polyline(array,None,"true")

cursor = arcpy.da.InsertCursor("line3d.shp",("SHAPE@"))
cursor.insertRow((polyline_3d,))
del cursor

for x in to_remove:
    os.remove(x)