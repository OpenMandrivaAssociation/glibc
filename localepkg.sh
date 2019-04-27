#!/bin/sh
langname="$1"
shift
locale="$1"
shift

cat <<EOF
%package -n    locales-$locale
Summary:	Base files for localization ($langname)
Group:		System/Internationalization
Obsoletes:	locales < 6:2.19-13
Requires(pre):	locales = %{EVRD}
Requires(post,preun):	sed
Requires(post,preun):	grep
EOF

isonames=""
for i in "$@"; do
	if echo "$i" |grep -qE '^r:'; then
		cat <<EOF
%rename locales-$(echo $i |cut -b3-)
EOF
	else
		isonames="$isonames $i"
	fi
done
isonames="$(echo $isonames)" # Get rid of leading whitespace

cat <<EOF

%description -n locales-$locale
These are the base files for $langname language
localization; you need it to correctly display
non-ASCII $langname characters, and for proper
alphabetical sorting, and representation of
dates and numbers according to
$langname language conventions.

%post -n locales-$locale
%{_bindir}/locale_install.sh $isonames

%preun -n locales-$locale
if [ "\$1" = "0" ]; then
	%{_bindir}/locale_uninstall.sh $isonames
fi

%files -n locales-$locale
EOF

for isoname in $isonames; do
	cat <<EOF
%optional %{_localedir}/$isoname
%optional %{_localedir}/$isoname.*
%optional %{_localedir}/$isoname@*
%exclude %{_localedir}/*/LC_MESSAGES/libc.mo
EOF
done
