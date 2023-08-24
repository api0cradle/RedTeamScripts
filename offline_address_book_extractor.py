import os, pathlib, re, argparse, datetime

# Script to export data from udetails.oab (Outlook Offline address book)
# Author: Oddvar Moe
# August 24, 2023
# V 1.0

# Custom object used to hold data
class OutlookObject:
    def __init__(self):
        self.type = None
        self.smtp = None
        self.phone = None
        self.upn = None
        self.sip = None

def parse_udetails(udetailsfile,outfile):
    #Todo someday: Map the data format correctly: https://msopenspecs.azureedge.net/files/MS-OXOAB/%5bMS-OXOAB%5d.pdf
    #Todo someday: Add X500 and X400 addresses
    #Todo someday: Parse out samaccount, name and more if possible from within the X500/X400 addresses
    f = open(udetailsfile,"r", errors='ignore')
    myStr = f.read()

    # Define the regular expression pattern with a capturing group
    pattern = r"/o=ExchangeLabs/ou=Exchange Administrative Group \(FYDIBOHF23SPDLT\)/cn=Recipients"

    result = re.split(pattern, myStr)
    print(f"[+] Found {len(result)} potential objects from {udetailsfile}")
    
    object_list = []
    
    print(f"[+] Parsing objects and only keeping objects with at least one SMTP proxy address defined")
    for userdata in result:
        # We only care if there is at least one email address
        smtp_match = re.findall(r'smtp:[\w\.-]+@[\w\.-]+\.\w+', userdata, re.IGNORECASE)
        sip_match = re.findall(r'sip:[\w\.-]+@[\w\.-]+\.\w+', userdata, re.IGNORECASE)
        
        if smtp_match:
            # Create new user object
            object = OutlookObject()

            # Set SMTP addresses to the object and use set to make sure the list is unique
            object.smtp = set(smtp_match)

            # Set SIP addresses to the object and use set to make sure the list is unique
            if sip_match:
                object.sip = set(sip_match)
            
            # Get those Phone number if present
            phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
            split_phone_pattern = "cn=Microsoft Private MDB"
            potential_phone_string = userdata.split(split_phone_pattern)
            if len(potential_phone_string) > 1:
                matches = re.findall(phone_pattern,potential_phone_string[1])
                if matches:
                    object.phone = matches
            
            # Userprincipalname
            split_username_pattern = "/cn=Recipients/cn="
            usernamestring = (userdata.split(split_username_pattern)[0]).split("\x00")
            object.upn = usernamestring[1]
            object_list.append(object)
    f.close()
    print(f"[+] Successfully parsed {len(object_list)}")
    
    # Export list
    print(f"[+] Writing data to file {outfile}")
    with open(outfile, 'a') as fp:
        for object in object_list:
            fp.write(f"UPN:{str(object.upn)},Phone:{str(object.phone)},Smtp:{str(object.smtp)},Sip:{str(object.sip)}\n")   
    print(f"[+] Export done")
    

def main():
    def generate_filename():
        timestamp = datetime.datetime.now()
        formatted_timestamp = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"udetails_{formatted_timestamp}.csv"
        return filename

    def check_file(filename):
        try:
            with open(filename, 'r'):
                return filename
        except FileNotFoundError:
            raise argparse.ArgumentTypeError(f"File '{filename}' not found")
        except PermissionError:
            raise argparse.ArgumentTypeError(f"Cannot read file '{filename}'")

    usage = "Usage: %prog [options]"
    parser = argparse.ArgumentParser(description="Udetails.oab extractor")
    parser.add_argument(
        '-i','--udetailsfile',
        required=True,
        type=check_file,
        help="Path to udetails.oab file you want to parse"
    )
    parser.add_argument(
            '-o','--outfile',
            type=pathlib.Path,
            default=os.path.join(os.getcwd(),generate_filename()),
            help="Name of outfile from the export - Default is current directory\\udetails_YYYMMDD_HHMMSS.csv"
    )
    args = parser.parse_args()

    # Print ascii art - Most important step
    ascii = """
      __...--~~~~~-._   _.-~~~~~--...__
    //               `V'               \\ 
   //     OFFLINE     |   ADDRESSBOOK   \\ 
  //__...--~~~~~~-._  |  _.-~~~~~~--...__\\ 
 //__.....----~~~~._\ | /_.~~~~----.....__\\
====================\\|//====================
                    `---`    
"""

    # Run the function
    print(ascii)
    parse_udetails(args.udetailsfile,args.outfile)
        
if __name__ == '__main__':
    main()