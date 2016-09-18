'''
#--------------------------------------------------------------------------------------------------------#
Version 1.3
Created: 2016-09-18
Python 2.7
ArcGIS 10.4.1
#--------------------------------------------------------------------------------------------------------#
'''

#This is stand-alone script and it can be run by copying it to Python command line in ArcGIS with proper parameters in INTRO section.
#For sript working with tool, see IdMatch_ToolScript.py

#--------------------------------------------------------------------------------------------------------#
#   INTRO
#--------------------------------------------------------------------------------------------------------#

#import modules
import arcpy, os, sys
from arcpy import env

arcpy.env.overwriteOutput = True

#parameters
'''fromFC = sys.argv[1] #feature class with IDs
toFC = sys.argv[2] #feature class without IDs
output = sys.argv[3] #feature class
tolerance = sys.argv[4] #any value'''

fromFC = 'Odcinek2Poziomy_FeatureVerti'
toFC = 'Odcinek2Poziomy_t'
output = 'Odcinek2Poziomy_t_new'
tolerance = 1

tol = str(tolerance)+" Meters"

#--------------------------------------------------------------------------------------------------------#
#   RUN
#--------------------------------------------------------------------------------------------------------#

#spatial join
arcpy.SpatialJoin_analysis(toFC,
                           fromFC,
                           output,
                           "JOIN_ONE_TO_MANY",
                           "KEEP_ALL",
                           """PZ "PZ" true true false 10 Long 0 10 ,First,#,Well_Tracks,PZ,-1,-1;PF "PF" true true false 10 Long 0 10 ,First,#,Well_Tracks,PF,-1,-1;BO "BO" true true false 10 Long 0 10 ,First,#,Well_Tracks,BO,-1,-1;MI "MI" true true false 10 Long 0 10 ,First,#,Well_Tracks,MI,-1,-1;RO "RO" true true false 10 Long 0 10 ,First,#,Well_Tracks,RO,-1,-1;KH "KH" true true false 10 Long 0 10 ,First,#,Well_Tracks,KH,-1,-1;KV "KV" true true false 10 Long 0 10 ,First,#,Well_Tracks,KV,-1,-1;H "H" true true false 10 Long 0 10 ,First,#,Well_Tracks,H,-1,-1;RE "RE" true true false 10 Long 0 10 ,First,#,Well_Tracks,RE,-1,-1;RW "RW" true true false 10 Long 0 10 ,First,#,Well_Tracks,RW,-1,-1;L "L" true true false 10 Long 0 10 ,First,#,Well_Tracks,L,-1,-1;A "A" true true false 10 Long 0 10 ,First,#,Well_Tracks,A,-1,-1;BETA "BETA" true true false 10 Long 0 10 ,First,#,Well_Tracks,BETA,-1,-1;DELTA_P "DELTA_P" true true false 10 Long 0 10 ,First,#,Well_Tracks,DELTA_P,-1,-1;B "B" true true false 10 Long 0 10 ,First,#,Well_Tracks,B,-1,-1;MAJOR_AXIS "MAJOR_AXIS" true true false 10 Long 0 10 ,First,#,Well_Tracks,MAJOR_AXIS,-1,-1;MINOR_AXIS "MINOR_AXIS" true true false 10 Long 0 10 ,First,#,Well_Tracks,MINOR_AXIS,-1,-1;AZIMUTH "AZIMUTH" true true false 10 Long 0 10 ,First,#,Well_Tracks,AZIMUTH,-1,-1;MIDPOINT_X "MIDPOINT_X" true true false 10 Long 0 10 ,First,#,Well_Tracks,MIDPOINT_X,-1,-1;MIDPOINT_Y "MIDPOINT_Y" true true false 10 Long 0 10 ,First,#,Well_Tracks,MIDPOINT_Y,-1,-1;START_X "START_X" true true false 19 Double 0 0 ,First,#,Well_Tracks,START_X,-1,-1;START_Y "START_Y" true true false 19 Double 0 0 ,First,#,Well_Tracks,START_Y,-1,-1;END_X "END_X" true true false 19 Double 0 0 ,First,#,Well_Tracks,END_X,-1,-1;END_Y "END_Y" true true false 19 Double 0 0 ,First,#,Well_Tracks,END_Y,-1,-1""",
                           "WITHIN_A_DISTANCE",
                           tol,
                           "")

#Add ID field
arcpy.AddField_management(output, "Well_ID", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

#copy valuest between fields
arcpy.CalculateField_management(output, "Well_ID", "!JOIN_FID!", "PYTHON_9.3", "")

#delete fields
fields = "Join_Count;TARGET_FID;JOIN_FID"
arcpy.DeleteField_management(output, fields)