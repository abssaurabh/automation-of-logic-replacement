'''authored by abs saurabh on 18th august as part of PT_automation Project
This module contains the function defintions which are required to make things happen'''

import os
from user_prompts import *
from lxml import etree as ET
import re
import sys
import fileinput

#define the xml namespace as ElementTree does not handle the namespaces
nsmap = {'def':'http://oval.mitre.org/XMLSchema/oval-definitions-5'}

#return the check title
def get_check_title(xml_name):
    fhandle = open(xml_name,"r")
    root = ET.parse(fhandle).getroot()
    title_node = root.find('./def:definitions/def:definition/def:metadata/def:title',namespaces = nsmap)
    fhandle.close()
    return title_node.text


#returns the platforms in the checks
def get_check_platforms(xml_name):
    fhandle = open(xml_name,"r")
    root = ET.parse(fhandle).getroot()
    platform_node = root.findall('./def:definitions/def:definition/def:metadata/def:affected/def:platform',namespaces = nsmap)
    platform_list = []
    for platform in platform_node:
        platform_list.append(platform.text)
    fhandle.close()
    return platform_list
 
#returns true if it is an IE check 
def set_IE_flag(check_title):
    # find returns -1 if string is not found
    if check_title.find("Internet Explorer") != -1:
        return True
    else: 
        return False

# returns true if it is an embedded check
def set_Embedded_Flag(check_title):
    # find returns -1 if string is not found
    if check_title.find("Embedded") != -1:
        return True
    else: 
        return False
    
def set_Win10_flag(check_title):
    if check_title.find("Windows 10") != -1:
        return True
    else:
        return False
    
    
def get_IE_Version(check_title):
    IE_Version = re.search(".+ (Internet Explorer \d+) .+",check_title)
    return IE_Version.group(1)

def get_Win10_Version(check_title):
    Win10_Version = re.search(".+ (Windows 10 Version \d+) .+",check_title)
    if Win10_Version is None:
        return "Windows 10"
    else:
        return Win10_Version.group(1)
    
def increment_version(fname):
    fhandle = fileinput.FileInput(fname,inplace=True)
    for line in fhandle: 
        
        if line.lstrip().startswith("<definition "):
            line = re.sub('version=\"(\d+?)\"',"version=\"2400\"",line)
        print line


def get_check_KB(check_title):
    KB_number = re.search(".+(KB\d+).+",check_title)
    return KB_number.group(1)
    

def main(auto_check,manual_dir):
  
    found_match = False  
    #get the version,title and platforms from the check
    auto_check_title  = get_check_title(auto_check)
    auto_IS_EMBEDDED_CHECK = set_Embedded_Flag(auto_check_title)
    
    
    fhandle = open(auto_check,"r+")
    tree = ET.parse(fhandle)
    root = tree.getroot()
    # def_node = root.find('./def:definitions/def:definition',namespaces = nsmap)
    # version = def_node.attrib['version']
    # def_node.set('version',(version+"00"))
  
    #increment check version
  
    if auto_IS_EMBEDDED_CHECK:
      
        metadata_node = root.findall('./def:definitions/def:definition/def:metadata',namespaces = nsmap)
        visible_node = ET.SubElement(metadata_node[0],"visible")
        visible_node.attrib['xmlns'] = "http://pa.mcafee.com/XMLSchema/ovalExtensions"
        visible_node.text = "False"
        tree.write(auto_check)
        increment_version(auto_check)
        return
   
    auto_check_platforms = get_check_platforms(auto_check)
    auto_KB_number = get_check_KB(auto_check_title)
    auto_IS_WIN10_CHECK = set_Win10_flag(auto_check_title)
    auto_IS_IE_CHECK = set_IE_flag(auto_check_title)
     
    for subdir, dirs, files in os.walk(manual_dir):
        for filename in files:
            manual_check = os.path.join(subdir, filename)
           
            manual_check_title = get_check_title(manual_check)
        
            manual_KB_number = get_check_KB(manual_check_title)
    
            manual_check_platforms = get_check_platforms(manual_check)
         
            matched_IE_versions = True
                     
            matched_Win10_versions = True
         
            if auto_KB_number != manual_KB_number:
                continue
            
            
            #convert to sets for faster list comparison
            if set(manual_check_platforms) != set(auto_check_platforms):
                continue
            
             
            manual_IS_IE_CHECK = set_IE_flag(manual_check_title)
            manual_IS_Win10_CHECK = set_Win10_flag(manual_check_title)

            
            if auto_IS_IE_CHECK and manual_IS_IE_CHECK:
                auto_IE_version = get_IE_Version(auto_check_title)
                manual_IE_version = get_IE_Version(manual_check_title)
                if auto_IE_version != manual_IE_version:
                    matched_IE_versions = False
                
            if auto_IS_WIN10_CHECK and manual_IS_Win10_CHECK:
                auto_Win10_version = get_Win10_Version(auto_check_title)
                manual_Win10_Version = get_Win10_Version(manual_check_title)
                if auto_Win10_version != manual_Win10_Version:
                    matched_Win10_versions = False
            
            if  not matched_IE_versions or not matched_Win10_versions:
                continue
            
            ##else replace the logic
            found_match = True
            temp_string1 = []
            fhandle.seek(0)
            for line in fhandle.readlines():
                #if line.lstrip().startswith("<definition "):
                #   line = re.sub('version=\"(\d+?)\"',"version=\"2400\"",line)
                if  line.lstrip().startswith("</metadata>"):
                    break
                temp_string1.append(line)
                
            temp_string2 = []
            start_adding = 0
            manual_fhandle = open(manual_check,"r+")
            manual_fhandle.seek(0)
            for line in manual_fhandle.readlines():
                if start_adding:
                    temp_string2.append(line)
                if line.lstrip().startswith("<vendor_data"):
                    start_adding = 1
            
            fhandle.seek(0)
            fhandle.truncate()
            fhandle.flush()
            fhandle.writelines(temp_string1+temp_string2)
            fhandle.flush()
            fhandle.close()          
            manual_fhandle.close()
            increment_version(auto_check)
    return found_match
#for all files in auto_checks_location

prompt_at_start()

auto_dir = prompt_for_auto()

manual_dir = prompt_for_manual()

count = 0

log_fhandle = open("log_file.txt","w+")

for subdir, dirs, files in os.walk(auto_dir):
    for fname in files:
        filepath = os.path.join(subdir, fname)
        is_matched = main(filepath,manual_dir)  
        if not is_matched:
            log_fhandle.write("Error: Could not match file: %s \n" %fname)
            log_fhandle.flush()   
        else:
            count = count + 1

end_message ="Total no. of regular checks modified = " + str(count)

prompt_at_end(end_message)

