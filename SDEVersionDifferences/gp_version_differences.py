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

import bwplogger as logger
log = logger.LogIt(os.getcwd() + "\\python_logs", "Yes")

def main():
    '''
    diff_direction=1 will compare DataQuality to Default
    diff_direction=2 will compare Default to DataQuality
    If there are any diff results using 2, this indicates edits in Default are bypassing DataQuality

    TODO: Allow the caller to quit after one diff
    '''

    
    mxd = os.getcwd() + "\\versionDiffItems1.mxd"
    sdeconn = os.getcwd() + "\\pods_os.sde"
    gpverdiff_app_path = os.getcwd() + "\\GPVersionDifferences.exe"
    diff_folder = os.getcwd() + "\\diff_folder"
    diff_direction = "1"
    #gp_version_diffs(mxd, sdeconn, gpverdiff_app_path, diff_folder, diff_direction)
    iterate_items(mxd, sdeconn)


def persist_results(result):
    with open(os.getcwd() + "\\" + result[0], "w") as writer:
        writer.write("There are " + str(len(result)) + " fields that have values outside of the Domain.")
        for item in result:
            writer.write(item)
            writer.write(result[item])


def iterate_items(mxd, connection):
    for item in get_mxd_items(mxd):
        try:
            result = validate_domains(item, connection)
            persist_results(result)
        except:
            log.logMessage(traceback.format_exc())


def validate_domains(map_item, connection):
    total_res_dict = {}
    '''
        Apparently tableviews don't act like map layers when returning the objects.
        A bit of an if statment is needed to handle this.
        map_item will convert to table_name...
    '''
    table_name = str(map_item)
    if str(type(map_item)) == "<class 'arcpy._mapping.TableView'>":
        table_name = str(map_item.name)
    for fld in arcpy.Describe(map_item).fields:
        print fld.name
        domain_name = get_domain_name(fld)
        if domain_name is not None:
            print fld.name
            print domain_name
            sql_result = sql_validate_domain(domain_name, fld.name, table_name, connection)
            if sql_result is not True:
                total_res_dict[fld.name] = sql_result
    if len(total_res_dict) > 0:
        final_result_dict = {}
        final_result_dict[table_name] = total_res_dict
        return final_result_dict
           

def sql_validate_domain(domain_name, field_name, table_name, connection):
    sdeconn = arcpy.ArcSDESQLExecute(connection)
    storedproc = "exec GIS.usp_ValidateCodedDomainOnVersion '" + table_name + "_VW', '" + field_name + "', '" + domain_name + "', 'DATAQUALITY.DataQuality'"
    try:
        ret = sdeconn.execute(storedproc)
        return ret
    except:
        log.logMessage(storedproc)


def get_domain_name(field):
    domain_name = field.domain
    if len(str(domain_name)) > 0:
        return domain_name


def gp_version_diffs(mxd, sdeconn, gpverdiff_app_path, diff_folder, diff_direction):
    try:
        rebuild_dir(diff_folder)
        for item in get_mxd_items(mxd):
            if len(os.listdir(diff_folder)) == 0:
                execall = gpverdiff_app_path + " " + item + " " + sdeconn + " " + diff_folder + " " + diff_direction
                callGPVersionDiffApp(execall)
    except:
        log.logMessage(traceback.format_exc())
        arcpy.AddMessage(traceback.format_exc())
        print traceback.format_exc()


def rebuild_dir(diffDir):
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


def get_layers(mxd, input_list, strip=None):
    mxd = arcpy.mapping.MapDocument(mxd)
    df = arcpy.mapping.ListDataFrames(mxd, mxd.activeDataFrame.name)[0]
    for i in arcpy.mapping.ListLayers(mxd):
        if strip is not None:
            input_list.append(i.dataSource.split("\\")[-1])
        else:
            input_list.append(i)
    return input_list


def get_tableviews(mxd, input_list, strip=None):
    mxd = arcpy.mapping.MapDocument(mxd)
    df = arcpy.mapping.ListDataFrames(mxd, mxd.activeDataFrame.name)[0]
    for i in arcpy.mapping.ListTableViews(mxd):
        if strip is not None:
            input_list.append(i.dataSource.split("\\")[-1])
        else:
            input_list.append(i)
    return input_list






if __name__ == "__main__":
    main()





