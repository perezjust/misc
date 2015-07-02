import os
import string
import sys
import traceback
import shutil
import logging
import os.path
import time
import arcpy
import arceditor



def main():
    '''
    diff_direction=1 will compare DataQuality to Default
    diff_direction=2 will compare Default to DataQuality
    If there are any diff results using 2, this indicates edits in Default are bypassing DataQuality

    TODO: Allow the caller to quit after one diff
    '''
    workspace = "
    mxd = os.getcwd() + "\\versionDiffItems1.mxd"
    sdeconn = os.getcwd() + "\\pods_os.sde"
    gpverdiff_app_path = os.getcwd() + "\\GPVersionDifferences.exe"
    diff_folder = os.getcwd() + "\\diff_folder"
    diff_direction = "1"
    gp_version_diffs(mxd, sdeconn, gpverdiff_app_path, diff_folder, diff_direction)





def gp_version_diffs(mxd, sdeconn, gpverdiff_app_path, diff_folder, diff_direction):
    try:

        rebuildDiffDir(diff_folder)
        for item in get_mxd_items(mxd):
            if len(os.listdir(diff_folder)) == 0:
                execall = gpverdiff_app_path + " " + item + " " + sdeconn + " " + diff_folder + " " + diff_direction
                callGPVersionDiffApp(execall)

    except:
        arcpy.AddMessage(traceback.format_exc())
        print traceback.format_exc()

        

def rebuildDiffDir(diffDir):
    if os.path.exists(diffDir):
        shutil.rmtree(diffDir)
    time.sleep(5)
    os.mkdir(diffDir)


def callGPVersionDiffApp(execall):
    os.system(execall)


def get_mxd_items(mxd):
    input_list = []
    get_layers(mxd, input_list)
    get_tableviews(mxd, input_list)
    return input_list


def get_layers(mxd, input_list):
    mxd = arcpy.mapping.MapDocument(mxd)
    df = arcpy.mapping.ListDataFrames(mxd, mxd.activeDataFrame.name)[0]
    for i in arcpy.mapping.ListLayers(mxd):
        input_list.append(i.dataSource.split("\\")[-1])
    return input_list


def get_tableviews(mxd, input_list):
    mxd = arcpy.mapping.MapDocument(mxd)
    df = arcpy.mapping.ListDataFrames(mxd, mxd.activeDataFrame.name)[0]
    for i in arcpy.mapping.ListTableViews(mxd):
        input_list.append(i.dataSource.split("\\")[-1])
    return input_list



if __name__ == "__main__":
    main()





