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

arcpy.DeleteField_management("D:\KAMIENIEC\PROJEKT GIS\Dane\Odcinek2Poziomy.shp", "XX1")

#dane
temp_loc = os.environ["Temp"]
linie = "D:\KAMIENIEC\PROJEKT GIS\Dane\Odcinek2Poziomy.shp"
raster = "D:\KAMIENIEC\PROJEKT GIS\Dane\GeobazaTestowa.gdb\Spagtest2"
nazwa_pola = "XX1"
punkty = temp_loc + "\Points.shp"
punkty_wart = temp_loc + "\Points_values.shp"

#usuwanie temp-ow
tempy = [punkty, punkty_wart]
for in_data in tempy:
    try:
        arcpy.Delete_management(in_data, "")
    except NameError:
        break

#--------------------------------------------------------------------------------------------------------#
#   PRZYGOTOWANIE I KONWERSJA LINII 
#--------------------------------------------------------------------------------------------------------#

def ReadCellSize(raster):
    
    description = arcpy.Describe(raster)
    cellsize = description.children[0].meanCellHeight
    return cellsize

def CreatePoints(lines, raster):

    points = temp_loc + "\Points.shp"
    cellsize = ReadCellSize(raster)
    
    dist = str(cellsize / 2) + " Meters"
    arcpy.Densify_edit(lines, "DISTANCE", dist, "1 Meters", "10")

    arcpy.FeatureVerticesToPoints_management(lines, points, "ALL")

def ReadRasterValue(lines, field_name, points, raster):

    pts_values = temp_loc + "\Points_values.shp"

    arcpy.AddField_management(lines, field_name, "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

    arcpy.gp.ExtractValuesToPoints_sa(punkty, raster, pts_values, "NONE", "VALUE_ONLY")

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

punkty_wart = ReadRasterValue(linie, nazwa_pola, punkty, raster)

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
tempy = [punkty, punkty_wart]
for in_data in tempy:
    arcpy.Delete_management(in_data, "")