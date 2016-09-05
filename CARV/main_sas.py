'''
#--------------------------------------------------------------------------------------------------------#
Wersja 1.1
Utworzono: 16.09.2015
Python 2.7
ArcGIS 10.3.1
Autor: Grzegorz Pawlowski
#--------------------------------------------------------------------------------------------------------#
'''

#--------------------------------------------------------------------------------------------------------#
#   WSTEP
#--------------------------------------------------------------------------------------------------------#

#importuj moduly
import arcpy, os, sys

#dane
temp_loc = os.environ["Temp"]
tempy = [punkty, (temp_loc + "\Points_values.shp")]
linie = "D:\KAMIENIEC\PROJEKT GIS\Dane\Odcinek2Poziomy.shp"
raster = "D:\KAMIENIEC\PROJEKT GIS\Dane\GeobazaTestowa.gdb\Spagtest2"
nazwa_pola = "XX1"

#--------------------------------------------------------------------------------------------------------#
#   PRZYGOTOWANIE I KONWERSJA LINII 
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
        if row[0] not in lista_id:
            lista_id.append(row[0])            
        lista_val.append(row[1])
        matrix.append([row[0], row[1]])
    print lista_id
    print lista_val
    print matrix

def CalculateMean(lista_id):
    for ID in lista_id:
        suma = 0
        ilosc = 0
        for row_q in matrix:
            FID = row_q[0]
            valu = row_q[1]
            if FID == ID:
                ilosc += 1
                suma += valu
                print str(row_q[0]) + " = " + str(ID)
        srednia = float(suma)/float(ilosc)
        srednie.append([ID,srednia])
    print srednie

def SaveResults(cur_lin, nazwa_pola):
    fields = ["FID", nazwa_pola]
    with arcpy.da.UpdateCursor(linie, fields) as cur_lin:
        for line in cur_lin:
            for row in srednie:
                ID = row[0]
                srednia = row[1]
                if line[0] == ID:
                    line[1] = srednia
                    cur_lin.updateRow(line)

CreatePoints(linie, raster)
punkty_wart = ReadRasterValue(linie, nazwa_pola, raster)

#--------------------------------------------------------------------------------------------------------#
#   LICZENIE I WPISYWANIE SREDNIEJ
#--------------------------------------------------------------------------------------------------------#

#zmienne
srednia = 0
lista_id = []
lista_val = []
matrix = []
srednie = []

cur_pkt = arcpy.da.SearchCursor(punkty_wart, ["ORIG_FID", "RASTERVALU"])

CreateIdList(cur_pkt)
    
CalculateMean(lista_id)

SaveResults(cur_lin, nazwa_pola)

#--------------------------------------------------------------------------------------------------------#
#   CZYSZCZENIE
#--------------------------------------------------------------------------------------------------------#
            
#usuwanie temp-ow
ClearTemps(tempy)