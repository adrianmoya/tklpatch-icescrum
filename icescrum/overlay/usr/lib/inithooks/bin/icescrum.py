#!/usr/bin/python
"""Set Icescrum admin password, email and domain to serve

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=icescrum.example.com
"""

import sys
import getopt
import hashlib
import fileinput

from dialog_wrapper import Dialog
from mysqlconf import MySQL

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

DEFAULT_DOMAIN="icescrum.example.com"

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email=', 'domain='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    domain = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val
        elif opt == '--domain':
            domain = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Icescrum Password",
            "Enter new password for the Icescrum 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Icescrum Email",
            "Enter email address for the Icescrum 'admin' account.",
            "admin@example.com")
    
    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        domain = d.get_input(
            "Icescrum Domain",
            "Enter the domain to serve GitLab.",
            DEFAULT_DOMAIN)

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    hashpass = hashlib.sha256(password).hexdigest()

    m = MySQL()
    m.execute('UPDATE icescrum.icescrum2_user SET email=\"%s\" WHERE username=\"admin\";' % email)
    m.execute('UPDATE icescrum.icescrum2_user SET passwd=\"%s\" WHERE username=\"admin\";' % hashpass)

    for line in fileinput.input("/etc/icescrum/config.properties",inplace=True):
        line = line.replace("https://localhost", "https://"+domain)
        sys.stdout.write(line)

if __name__ == "__main__":
    main()

