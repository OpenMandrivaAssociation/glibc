#!/bin/sh
##
## Glibc "make check" helper script
##

while [[ $# -gt 0 ]]; do
	opt=$1
	shift 1
	optarg=$1
	case $opt in
		-d) DIR=$optarg; shift 1;;
		-k) K=$opt;;
		-l) LDSO=$optarg; shift 1;;
		-j) JOBS=-j$optarg; shift 1;;
		-j[0-9]*) JOBS=$opt;;
	esac
done

[[ -n "$DIR" ]] || {
	echo "ERROR: check dir not specified"
	exit 1
}

function CMD() {
	echo + ${1+"$@"}
	${1+"$@"} || return $?
}

echo "########################################################################"
echo "##"
echo "##    Testing in $DIR with ${LDSO:-default ld.so}"
echo "##"
echo "########################################################################"

[[ -n "$LDSO" ]] && {
	CMD mv -f $DIR/elf/ld.so $DIR/elf/ld.so.orig
	CMD cp -a $LDSO $DIR/elf/ld.so
	CMD find $DIR -name \*.out -exec mv -f '{}' '{}'.origldso \;
}

CMD make $JOBS -C $DIR check $K PARALLELMFLAGS=-s
rc=$?
if [[ $rc -eq 0 ]]; then
	STATUS="PASS"
else
	STATUS="FAIL"
	if [[ -n "$K" ]]; then
		rc=0
	fi
fi

[[ -n "$LDSO" ]] && {
	CMD mv -f $DIR/elf/ld.so.orig $DIR/elf/ld.so
}

echo "##"
echo "##    Result: $STATUS"
echo "##"
exit $rc
