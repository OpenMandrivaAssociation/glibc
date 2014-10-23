#!/bin/env python

import string, rpm

def pkg(langname, locale, isonames):
    print(rpm.expandMacro("""
%%package -n    locales-"""+locale+"""
Summary:	Base files for localization ("""+langname+""")
Group:		System/Internationalization
Requires:	locales = %{EVRD}
Obsoletes:	locales <= 2.18.90-2
Requires(post,preun):	sed
Requires(post,preun):	grep"""))
    for isoname in isonames:
        if isoname.count(":"):
            print(rpm.expandMacro("%%{rename locales-%s}" % isoname))
            isonames.remove(isoname)
    print("""
%%description -n locales-"""+locale+"""
These are the base files for """+langname+""" language
localization; you need it to correctly display
non-ASCII """+langname+""" characters, and for proper
alphabetical sorting, and representation of
dates and numbers according to
"""+langname+""" language conventions.""")
    print("""
%%post -n locales-"""+locale+"""
%%{_bindir}/locale_install.sh %s""" % string.join(isonames, " ")+"""

%%preun -n locales-"""+locale+"""
if [ "\$1" = "0" ]; then
	%%{_bindir}/locale_uninstall.sh %s""" % string.join(isonames, " ")+"""
fi

%%files -n locales-"""+locale)
    for isoname in isonames:
        print("""
%optional %{_localedir}/"""+isoname+"""
%optional %{_localedir}/"""+isoname+""".*
%optional %{_localedir}/"""+isoname+"""@*
%exclude %{_localedir}/*/LC_MESSAGES/libc.mo""")
