'''
#--------------------------------------------------------------------------------------------------------#
Wersja 1.1 Trzeba dodac wybor argument�w, stworzyc toolboxa. UWAGA na sciezke z wiersza 85 przy
dodawaniu wyboru argumentow!
#--------------------------------------------------------------------------------------------------------#
'''

#--------------------------------------------------------------------------------------------------------#
#   WSTEP
#--------------------------------------------------------------------------------------------------------#

#import modulow
import arcpy, os, sys
from arcpy import env

# Zmienna srodowiskowa, katalog operacyjny
env.overwriteOutput = True

in_file = sys.argv[1]
out_file = sys.argv[2]
workspace = sys.argv[3]
env.workspace = workspace

#--------------------------------------------------------------------------------------------------------#
#   KONWERSJA PLIKU .dev na .txt akceptowany przez ArcGIS
#--------------------------------------------------------------------------------------------------------#

#otworz plik tekstowy
dev = in_file
d = open(dev, 'r')

#otworz plik tekstowy wyjsciowy
txt = workspace + '\wynik.txt'
o = open(txt, 'w')
o.write('MD,X,Y,Z,TVD,DX,DY,AZIM,INCL\n')

#liasta spacj wystepujacych w plikach petrela oraz odwrocenie jej kolejnosci, zeby zamienialo od najwiekszej
spacje = [' ', '  ', '   ', '	' ,'    ', '     ', '      ']
spacje.reverse()

#funkcja zamieniajaca odstepy z listy przecinkami
def zamiana(linia, lista):
    nl = linia
    for s in lista:
        nl = nl.replace(s, ',')
    return nl

#wlasciwe formatowanie pliku     
count = 0
for line in d:
    count = count + 1
    if count <= 13: #omija naglowek
        a = 0
    elif count > 13: #linie ponizej naglowka
        new_line = zamiana(line, spacje)
        new_line2 = new_line[1:] #usuwa przecinek z pierwszego miejsca
        o.write(new_line2)

#zamknij pliki
o.close()
d.close()



#--------------------------------------------------------------------------------------------------------#
#   TWORZENIE LINI 3D Z PLIKU
#--------------------------------------------------------------------------------------------------------#



#-----------------Tworzenie pliku przystosowanego do konwersji na polilinie 3D---------------------------#

#tymczasowe zmienne i lokalizacje
out_event = os.environ["TEMP"] + 'TEMPEventLayer.shp'
out_path = env.workspace + '\\'
outFC_name = 'Well_Points'
Well_Track = 'Well_Track1' #tu mozna pomyslec nad nazwa

#uklad odniesienia
CRS = "PROJCS['ETRS_1989_UWPP_1992',GEOGCS['GCS_ETRS_1989',DATUM['D_ETRS_1989',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Gauss_Kruger'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',-5300000.0],PARAMETER['Central_Meridian',19.0],PARAMETER['Scale_Factor',0.9993],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"

#tworzy event layer
arcpy.MakeXYEventLayer_management(txt, "X", "Y", out_event, CRS , "Z")

#konwersja event layera do feature class
arcpy.FeatureClassToFeatureClass_conversion(out_event, out_path, outFC_name, "", """MD "MD" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,MD,-1,-1;X "X" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,X,-1,-1;Y "Y" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,Y,-1,-1;Z "Z" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,Z,-1,-1;TVD "TVD" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,TVD,-1,-1;DX "DX" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,DX,-1,-1;DY "DY" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,DY,-1,-1;AZIM "AZIM" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,AZIM,-1,-1;INCL "INCL" true true false 8 Double 0 0 ,First,#,B2_o_LayerTEMP,INCL,-1,-1""", "")

#-------------------------------------#Tworzenie wlasciwej polilinii---------------------------------------#

punkty = env.workspace + '\\' + 'Well_Points' #musi byc sciezka, zeby kinia dziedziczyla CRS po punktach

#tworzy FC
arcpy.CreateFeatureclass_management(env.workspace, "line3d", "POLYLINE", "", "DISABLED", "ENABLED", punkty)
#arcpy.CreateFeatureclass_management(env.workspace, "line3d", "POLYLINE", "", "DISABLED", "ENABLED", CRS, "", "0", "0", "0")

#Rysuje polilinie
array = arcpy.Array()

for row in arcpy.da.SearchCursor(punkty, ("OID@", "SHAPE@","Z")):
    
        print "Punkt o ID", row[0]
        
        wsp_X = row[1].centroid.X
        wsp_Y = row[1].centroid.Y
        wsp_Z = row[1].centroid.Z
        
        point = arcpy.Point(wsp_X,wsp_Y,wsp_Z)
        array.append(point)


polyline_3d = arcpy.Polyline(array,None,"true")

cursor = arcpy.da.InsertCursor("line3d.shp",("SHAPE@"))
cursor.insertRow((polyline_3d,))
del cursor

arcpy.RefreshActiveView()

#-----------------------------------------------------------------------
#Usuwa niepotrzebne tempy

tempy = [out_event, outFC_name]

for t in tempy:
    arcpy.Delete_management(t, "")

