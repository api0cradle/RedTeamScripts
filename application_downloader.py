from optparse import OptionParser
import urllib.request
import shutil
from pathlib import Path
from urllib.parse import urlparse,urlunparse
import xml.etree.ElementTree as ET
import os

# Script to download a complete .NET ClickOnce application
# Author: Oddvar Moe
# May 16, 2023
# V 1.1

def download_and_parse_application(url, outputfolder, useragent):
    try:
        url = url.replace(" ", "%20") #probably a better way of doing this...just lazy
        outfolder = Path(outputfolder)
        filename = Path(urlparse(url).path).name
        outputfolder = Path.joinpath(outfolder, filename)
        
        # Create directory
        Path(outputfolder).mkdir(parents=True, exist_ok=True)
        application_output_path = outputfolder / filename

        # Set user agent
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={'User-Agent': useragent}
        )

        # Download .application file
        print("[+] # ==== {} ====".format(filename))
        print("[+] # Starting downloading {}".format(url))
        with urllib.request.urlopen(req) as response, open(application_output_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        # Parse and prepare needed paths
        parsed = urlparse(url)
        urlstructure = parsed.path.split("/")
        urlstructure = urlstructure[:-1]
        new_path = "/".join(urlstructure)
        new_parsed = parsed._replace(path=new_path)
        new_url = urlunparse(new_parsed)
        tree = ET.parse(application_output_path)
        root = tree.getroot()
        for elem in root.iter():
            if 'codebase' in elem.attrib:
                if ".manifest" in elem.attrib['codebase']:
                    # Create folder from name
                    manifestname = elem.attrib['codebase'].replace("\\", "/")
        
        urlmanifest = (new_url+"/"+manifestname).replace(" ", "%20") #again, probably a better way of doing this...just lazy

        # Set user agent
        req = urllib.request.Request(
            urlmanifest, 
            data=None, 
            headers={'User-Agent': useragent}
        )

        # Download manifest
        manifest_output_path = outputfolder / manifestname
        Path(manifest_output_path.parent).mkdir(parents=True, exist_ok=True)
        print("[+] # Starting downloading {}".format(urlmanifest))
        with urllib.request.urlopen(req) as response, open(manifest_output_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        ### Basepath for additional files
        url_basepath = '/'.join(urlmanifest.split("/")[:-1])

        ### Parse the manifest file, find files and get downloading
        print("[+] # Parsing manifest {}".format(manifest_output_path))
        files = parse_manifest(manifest_output_path)
        print("[+] # Found {} files to download".format(len(files)))
        for file in files:
            file = file + ".deploy" #All files have .deploy
            
            # Create folder structure
            file_outputpath = manifest_output_path.parent / file
            Path(file_outputpath.parent).mkdir(parents=True, exist_ok=True)

            # Construct url
            file_downloadurl = file
            file_downloadurl = (url_basepath+"/"+file_downloadurl).replace(" ", "%20").replace("\\", "/")           
            
            # Set user agent
            req = urllib.request.Request(
                file_downloadurl, 
                data=None, 
                headers={'User-Agent': useragent}
            )

            # Download the file
            print("[+] # Starting downloading {}".format(file_downloadurl))
            with urllib.request.urlopen(req) as response, open(file_outputpath, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
    
        print("[+] # ==== Done downloading {} ====\n\n".format(filename))
    except Exception as e:
        if e.response.status_code == 404:
            print("Got 404 - Seems the files are not present")
            print("[+] # ==== Done downloading {} ====\n\n".format(filename))
        else:
            print(f"An error occurred: {e}")


def parse_manifest(manifestfile):
    manifesttree = ET.parse(manifestfile)
    filenames = []

    root = manifesttree.getroot()
    for elem in root.iter():
        if 'codebase' in elem.attrib:
            filenames.append(elem.attrib['codebase'])
        if 'name' in elem.attrib and elem.tag.endswith('file'):
            filenames.append(elem.attrib['name'])
            
    return filenames

def main():
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-u", "--url", dest="url",
                    help="Required. Url of application file")
    parser.add_option("-o", "--outputfolder", dest="outputfolder",
                      help="Output folder for the downloaded application. Default is: currentdir\downloaded")
    parser.add_option("--useragent", dest="useragent",
                      help="Useragent you want to use for the requests. Default is: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
    parser.add_option("-l", "--list", dest="urllist",
                      help="Path to file containing list of urls pointing to .application files")
    
    (options, args) = parser.parse_args()

    # VERIFY ARGS
    if options.url is None and options.urllist is None:
         print("[!] # Need to specify url or input list")
         exit()
    
    if options.outputfolder is None:
         directory = os.path.join(os.getcwd(),"downloaded")
         options.outputfolder = directory
         print("[!] # No Output folder specified - Using current_directory/downloaded as base")
         
    # Create output directory
    try:
        Path(options.outputfolder).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("[!] # Specified output folder already created - Skipping creation")

    if not options.useragent:
        options.useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"

    logo = """
              ▄▄▄▄▄▄▄▀▀▄▄▄▄▄
          ▄▄▀▀▄▄▄▄▄▄▀▀▀▄▄▄▄▀▀█▄
     ▄▄▄█▀██████████████▄▄▄▄▄██▄
  █▀▀▄▄▄▄▄▄▄██████████████████▄
 ███████████████████████████████▄
███████████.APPLICATION███████████
▀████████████████████████████████
 ▀██████████████████████████████▀
   ▀██████████████████████████▀▀
        ▀███████████████████▀
        ▄▄    ▀▀▀▀▀▀     ▄▀▀
     ▄███         ▄    ▄██
   █████       ▄██   ████    ▄
    ▀██▀     ▄████   ▀▀▀  ▄██
          ▄█  ████        ████
       ▄███   ▀▀         ████
        ▀▀                 ▀▀
        ▄                ▄
    ▄███         ▄    ▄██
  █████       ▄██   ████    ▄
   ▀██▀     ▄████   ▀▀▀  ▄██
         ▄█  ████        ████
      ▄███   ▀▀         ████
       ▀▀                 ▀▀
    .NET APPLICATION RAINCLOUD
"""
    print(logo)

    #RUN SCAN
    if options.urllist:
        with open(options.urllist) as file:
            for url in file:
                download_and_parse_application(url, options.outputfolder, options.useragent)        
    else:
        download_and_parse_application(options.url, options.outputfolder, options.useragent)

if __name__ == '__main__':
    main()