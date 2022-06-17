#!/bin/bash

# this script is to be called when a locale is installed for first time;
# it gets the locale name(s) as parameter, and does the needed steps
# so that the new locale can be used by the system

# the list of languages that rpm installs their translations
if [ -r /etc/rpm/macros ]; then
	RPM_INSTALL_LANG="$(grep '^%_install_langs' /etc/rpm/macros | cut -d' ' -f2-)"
fi
[ -z "$RPM_INSTALL_LANG" ] && RPM_INSTALL_LANG=C
OLD_RPM_INSTALL_LANG="$RPM_INSTALL_LANG"

# remove/update locale-archive based on system wide configuration
[ -r /etc/sysconfig/locales ] && . /etc/sysconfig/locales
case "$USE_LOCARCHIVE" in
	yes|true|1)
		update_locarchive=1
		;;
	*)
		update_locarchive=0
		rm -f /usr/share/locale/locale-archive
		;;
esac

for i in "$@"; do
	langs="$i"
	for j in /usr/share/locale/$i.*; do
		[ -d "$j" ] || continue
		lng="$(basename $j)"
		# sanity check
		echo "$lng" | grep -q "$i" || continue
		langs="$langs $lng"
	done
	for k in $langs; do
		if [ -r "/usr/share/locale/$k/LC_CTYPE" ]; then
			# maintain updated locale-archive file
			[ "$update_locarchive" -eq 0 ] || \
				localedef \
				 --replace \
				 --add-to-archive "/usr/share/locale/$k" \
				> /dev/null
		fi
	done

	# make the installed locale known to rpm (so translations in that
	# language are installed), and the menu system
	if [ "$RPM_INSTALL_LANG" != "all" ]; then
		RPM_INSTALL_LANG="$(echo "$i":$RPM_INSTALL_LANG |tr ':' '\n' |sort |tr '\n' ':' |sed -e 's,:$,,')"
	fi
done

if [ "$OLD_RPM_INSTALL_LANG" != "$RPM_INSTALL_LANG" ]; then
	# update /etc/rpm/macros file
	if [ -w /etc/rpm/macros ]; then
		sed -i -e "s/^%_install_langs .*/%_install_langs $RPM_INSTALL_LANG/" /etc/rpm/macros
	fi
fi
