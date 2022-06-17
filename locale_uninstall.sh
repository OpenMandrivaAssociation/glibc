#!/bin/bash

# this script is to be called when a locale is removed from the sistem;
# so translations in the language(s) of the locale are no longer installed

# the list of languages that rpm installs their translations
if [ -r /etc/rpm/macros ]; then
	RPM_INSTALL_LANG="$(grep '^%_install_langs' /etc/rpm/macros | cut -d' ' -f2-)"
fi
[ -z "$RPM_INSTALL_LANG" ] && RPM_INSTALL_LANG=C
OLD_RPM_INSTALL_LANG="$RPM_INSTALL_LANG"

for i in "$@"; do
	langs="$i"
	for j in /usr/share/locale/$i.*; do
		[ -d "$j" ] || continue
		lng="$(basename $j)"
		# sanity check
		echo "$lng" | grep -q "$i" || continue
		langs="$langs $lng"
	done

	# remove the locale from the list known to rpm (so translations in that
	# language are no more installed), and from the menu system
	if [ "$RPM_INSTALL_LANG" != "all" ]; then
		RPM_INSTALL_LANG="$(echo $RPM_INSTALL_LANG |sed -e 's,$i,,' |tr ':' '\n' |grep -v '^$' |sort |tr '\n' ':' |sed -e 's,:$,,')"
	fi

	langs="$(localedef --list-archive | grep \"$i\")"
	for lng in $langs; do
		localedef --delete-from-archive "$lng"
	done
done

if [ "$OLD_RPM_INSTALL_LANG" != "$RPM_INSTALL_LANG" ]; then
	# update /etc/rpm/macros file
	if [ -w /etc/rpm/macros ]; then
		sed -i -e "s/^%_install_langs .*/%_install_langs $RPM_INSTALL_LANG/" /etc/rpm/macros
	fi
fi
