# RedTeamScripts
This repo will contain some random Red Team Scripts that I made that can be useful for others.


## Scripts usage

### application_downloader.py
Thanks to the awesome research by Nick Powers (@zyn3rgy) and Steven Flores (@0xthirteen) over at Specterops I decided that I needed to create this script in order to quickly download .application files.
The script will download the .application file and parse it. Figure out the manifest and pull down the rest of the files. 

Link to research: https://posts.specterops.io/less-smartscreen-more-caffeine-ab-using-clickonce-for-trusted-code-execution-1446ea8051c5

Link to talk: https://www.youtube.com/watch?v=cyHxoKvD8Ck

They also released some tools: 
- https://github.com/zyn3rgy/ClickonceHunter
- https://github.com/0xthirteen/AssemblyHunter
```
Usage: application_downloader.py [options]

Options:
  -h, --help            show this help message and exit
  -u URL, --url=URL     Required. Url of application file
  -o OUTPUTFOLDER, --outputfolder=OUTPUTFOLDER
                        Output folder for the downloaded application. Default
                        is: currentdir\downloaded
  --useragent=USERAGENT
                        Useragent you want to use for the requests. Default
                        is: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
                        AppleWebKit/537.36 (KHTML, like Gecko)
                        Chrome/112.0.0.0 Safari/537.36
  -l URLLIST, --list=URLLIST
                        Path to file containing list of urls pointing to
                        .application files
```

The urllist needs to be a list seperated with newline with a url to each .application file url. 
Example:
```
https://www.randomdomain.com/someapp/someapp.application
https://www.randomdomain2.com/someapp2/someapp2.application
```

### offline_address_book_extractor.py
A script I wrote based losely on the https://github.com/grnbeltwarrior/OAB_Cleaver/blob/main/OAB_Cleaver.py script.
You will need to get your hands on a udetails.oab file that by default resides in the folder `C:\Users\<USERNAME>\AppData\Local\Microsoft\Outlook\Offline Address Books\<GUID>\udetails.oab`.
The `udetails.oab` will be input to this script and it parses out SMTP,SIP,UPN and Phone numbers.

```
usage: offline_address_book_extractor.py [-h] -i UDETAILSFILE [-o OUTFILE]

Udetails.oab extractor

options:
  -h, --help            show this help message and exit
  -i UDETAILSFILE, --udetailsfile UDETAILSFILE
                        Path to udetails.oab file you want to parse
  -o OUTFILE, --outfile OUTFILE
                        Name of outfile from the export - Default is current directory\udetails_YYYMMDD_HHMMSS.csv
```

Example output:
```
UPN:mail.user1@company.com,Phone:None,Smtp:{'SMTP:mail.user1@company.com', 'smtp:user1_alias@company.com'},Sip:None
UPN:mail.user2@company.com,Phone:999-999-9999,Smtp:{'smtp:mail.user2@company.onmicrosoft.com', 'SMTP:mail,user2@company.com'},Sip:{'SIP:mail,user2@company.com'}
```