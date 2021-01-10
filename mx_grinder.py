# coding=utf-8
import os
import sys

import argparse
import requests
from bs4 import BeautifulSoup

# Bedøm platform ift. konsol clearing
if sys.platform == 'win32':
    cmd = "cls"
else:
    cmd = "clear"


def clear_console():
    print os.system(cmd), chr(13), " ", chr(13),


def get_option(ask):
    clear_console()
    print_logo()
    print "(Interaktiv version. Kør scriptet med -h eller --help for flere indstillinger.)"
    print
    return raw_input(ask + "\n")


# Definer CLI arguments
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Stemmer på en bestemt valgmulighed x antal gange i afstemninger på MX.dk',
    epilog='DISCLAIMER: Denne kode er et Proof of Concept.\nForfatteren kan ikke stilles til ansvar for evt. misbrug.',
    add_help=True)

parser.add_argument(
    '-u',
    '--url',
    help='URL til artiklen der indeholder afstemningen. (gælder også embeddede afstemninger på bt.dk)',
    required=False)

parser.add_argument(
    '-t',
    '--times',
    help='Antal stemmer der skal afgives. 0 for uendeligt.',
    required=False)

parser.add_argument(
    '-c',
    '--choice',
    help='Valgmulighed i afstemningen, fra toppen. I JA/NEJ afstemninger er JA=1 og NEJ=0.'
         '(BUGGY! Tjek om stemmerne bliver afgivet rigtigt eller brug interaktiv version.)',
    required=False)

parser.add_argument(
    '-n',
    '--noclear',
    help='Clear ikke konsollen efter hver stemme.',
    required=False,
    action='store_true')


def print_logo():
    print """+yyyyyyyyyyyyyyyyyyyyyyyyyyyys.
yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy:
yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy:
yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy/
yyyyyyyyyyyyyyyyyyyyyyyyyyyhhh/      `:/++:`     -::::::-.     -:::   -:::    :::-  `::::::-`     .:::::::::`  -:::::--`
yyyyyyyyyyyyyyyyyyyyyyyyhhhhhh/    /dMMMMMMMy    NMMMMMMMMN/  `MMMd   NMMMy  -MMMo  +MMMMMMMMm/   yMMMMMMMMM` .MMMMMMMMMm-
yyys//oo///so+//oo/+yhhh++hhhh/   hMMM+..sNNN/  :MMMy--+MMMo  +MMMo  :MMMMMo sMMM-  dMMM:-/mMMM-  NMMN------  oMMMo--sMMM/
yyyy/ `+o/  /o+  yo`.so`.shhhh/  oMMM+  +++++.  yMMMhssdMMy`  hMMM.  yMMNNMM+dMMm  .MMMd   yMMM: :MMMMmmmm+   dMMMyssmMNs
yyyyo -yyy `yyy. yhh-  /hhhhhh/  mMMM. -NMMMM`  NMMMmmMMMm:  `MMMm   NMMh:MMMMMMo  +MMM+  .NMMm  yMMMyssss.  .MMMNmmMMMd-
yyyyo -yyy `hhh. yh/ :.`ohhhhh/  yMMMh//sMMMd  :MMMs  :MMMs  +MMMo  :MMM+ /MMMMM-  dMMMo+sNMMm.  NMMM+++++/  +MMM+  +MMM/
yyys: .oy+ `ohh. /.`ohh/ -yhhh/  `sNMMMMNhMM+  yMMM:  +MMM/  hMMM.  yMMM.  oMMMm  .MMMMMMMmy/   :MMMMMMMMMy  dMMM.  sMMM.
yyyyyyhhhhhhhhhhhhhhhhhhhhhhhh/     .--.  ``   ````    ```   ````   ````    ````   ``````        `````````   ````   ````
yyyhhhhhhhhhhhhhhhhhhhhhhhhhhh/
hhhhhhhhhhhhhhhhhhhhhhhhhhhhhh/
+yhhhhhhhhhhhhhhhhhhhhhhhhhhhs.
"""


def get_id(url):
    """
    Find afstemningens ID fra artiklens HTML
    """
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, "lxml")

    divs = soup.findAll('div', attrs={'class': 'interactive'})
    poll_url = divs[0].find('a')['href']

    global votetype
    if "advancedvotes" in html:
        votetype = "advancedvotes"
    else:
        votetype = "simplevotes"

    return poll_url.rsplit('/', 1)[-1]


def show_options(id):
    r = requests.get("https://interaktiv.mx.dk/toolbox/" + votetype + "/get/" + id)
    soup2 = BeautifulSoup(r.text, "lxml")

    clear_console()
    print_logo()
    print "(Interaktiv version. Kør scriptet med -h eller --help for flere indstillinger.)"
    print

    vote_text = soup2.find("div", attrs={"id": "vote_text"}).text
    print vote_text
    print

    if votetype == "advancedvotes":
            for option in soup2.find_all("div", attrs={"class": "vote_button"}):

                number = option.get("data-vote")
                text = option.text

                print "(%s) %s" % (number, text)
            print

    else:

            for option in soup2.find_all("div", attrs={"class": "vote_button"}):
                if option.get("id") == "vote_yes":
                    number = "1"

                else:
                    number = "0"

                text = option.text
                print "(%s) %s" % (number, text)
            print


def parse_url(url):
    return url if "://" in url else "http://" + url


def vote(poll_id, choice, times):
    """
    Primært vote-funktions loop
    """
    # Clear konsol hvis ikke -n / --noclear er brugt
    if not args.noclear:
        clear_console()

    # Print logo
    print_logo()

    print "Afstemningens ID: " + str(poll_id)

    i = 0

    try:
        while True:

            i += 1

            if i > times and not times == 0:
                print 'Stopper.'
                break

            # Send POST request
            r = requests.post('https://interaktiv.mx.dk/toolbox/%s/vote' % votetype,
                              data={
                                  'id': poll_id,
                                  'vote': choice - 1,
                                  'ci_csrf_token': ''})  # Tak til MX for en awesome anti-CSRF implementation.

            # Clear konsol hvis ikke -n / --noclear er brugt
            if not args.noclear:
                clear_console()

                # Printer info om afstemningen efter hver clearing
                print_logo()
                print "Afstemningens ID: " + str(poll_id)

            # Ved success får vi et 'status: ok' tilbage. Hvis ikke, break.
            if r.text != 'status: ok':
                print 'Uventet svar:', '\"' + r.text + '\"' + '\n', 'Stopper.'
                break

            # Alt gik fint, print info.
            else:
                print r.text
                print "Stemt %d gang%s" % (i, "e"[i == 1:])
                # time.sleep(0.3)

    # Stop ved ctrl-C,
    except KeyboardInterrupt:
        print ""
        print 'Stopper.'


# Parser arguments
args = parser.parse_args()

# Printer help og exiter, hvis en eller flere arguments mangler
if args.url or args.times or args.choice:
    if not args.url or not args.times or not args.choice:
        parser.error(
            "En eller flere argumenter mangler. Brug -h eller --help for hjælp.")
        parser.print_help()
        parser.exit()

# Hvis alle arguments er udfyldt, start vote()
if args.url and args.times and args.choice:
    # Laver variabler
    url = args.url
    choice = int(args.choice)
    times = int(args.times)
    poll_id = get_id(url)
    vote(poll_id, choice, times)

# Hvis ingen arguments er udfyldt, start interaktiv version
if not any(vars(args).values()):
    url = parse_url(
        get_option("Indsæt URLen til artiklen der indeholder afstemningen:"))
    print "Henter svarmuligheder..."

    poll_id = get_id(url)

    show_options(poll_id)

    choice = int(raw_input("Valgmulighed:" + "\n"))

    times = int(
        get_option("Hvor mange stemmer vil du afgive? 0 for uendeligt."))

    vote(poll_id, choice, times)
