# CVS snapshots of glibc
%define RELEASE		0
%if %{RELEASE}
%define glibcsrcdir	glibc-%{version}
%define glibcportsdir	glibc-%{version}
%else
%define glibcsrcdir	glibc-2.14-394-g8f3b1ff
%define glibcportsdir	glibc-ports-2.14-25-gd3d9bde
%endif

%define	checklist	%{_builddir}/%{glibcsrcdir}/Check.list

# crypt blowfish support
%define crypt_bf_ver	1.2

%define _slibdir	/%{_lib}
%define _slibdir32	/lib
%define _libdir32	%{_prefix}/lib

%define	_disable_ld_no_undefined	1
%undefine _fortify_cflags

# for added ports support for arches like arm
%define build_ports	0
# add ports arches here
%ifarch %{arm} %{mipsx}
%define build_ports	1
%endif

%ifarch %{arm}
%define _gnu		-gnueabi
%endif

# Define Xen arches to build with -mno-tls-direct-seg-refs
%define xenarches	%{ix86}

# Define to build nscd with selinux support
%define build_selinux	0

# Allow make check to fail only when running kernels where we know
# tests must pass (no missing features or bugs in the kernel)
%define check_min_kver 2.6.21

# Define to build a biarch package
%define build_multiarch	0
%ifarch x86_64
%define build_multiarch	1
%endif

%define build_nscd	1
%define build_i18ndata	1
%define build_timezone	0

%define enable_nsscrypt	1
%ifarch %{ix86} x86_64
%define enable_systap	1
%else
%define enable_systap	0
%endif

# build documentation by default
%bcond_without		doc
%bcond_without		pdf
# enable utils by default
%bcond_without		utils

#-----------------------------------------------------------------------
Summary:	The GNU libc libraries
Name:		glibc
Version:	2.14.90
Release:	12
Epoch:		6
License:	LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
Group:		System/Libraries
Url:		http://www.gnu.org/software/libc/

# FSF source
Source0:	http://ftp.gnu.org/gnu/glibc/%{glibcsrcdir}.tar.xz
%if %{RELEASE}
Source1:	http://ftp.gnu.org/gnu/glibc/%{glibcsrcdir}.tar.xz.sig
%endif

# Fedora tarball
Source2:	%{glibcsrcdir}-fedora.tar.xz
Source3:	glibc-manpages.tar.bz2
Source5:	glibc-check.sh

Source8:	http://ftp.gnu.org/gnu/glibc/%{glibcportsdir}.tar.xz
%if %{RELEASE}
Source9:	http://ftp.gnu.org/gnu/glibc/%{glibcportsdir}.tar.xz.sig
%endif

# Blowfish support
Source50:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz
Source51:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz.sign
Source52:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.c
Source53:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.h

Obsoletes:	glibc-profile
Provides:	glibc-crypt_blowfish = %{crypt_bf_ver}
Provides:	should-restart = system
# we'll be the only package requiring this, avoiding any other package
# dependencies on '/bin/sh' or 'bash'
Requires:	bash
%ifarch %{xenarches}
%rename		%{name}-xen
%endif
# The dynamic linker supports DT_GNU_HASH
Provides:	rtld(GNU_HASH)
BuildRequires:	patch, gettext, perl
BuildRequires:	kernel-headers
%if %{build_selinux}
BuildRequires:	libselinux-devel >= 1.17.10
%endif
# need linker for -Wl,--hash-style=both (>= 2.16.91.0.7-%{mkrel 6})
# need gnu indirect function for multiarch (>= 2.19.51.0.14-1mnb2)
%define binutils_version 2.19.51.0.14-1mnb2
BuildRequires:	binutils >= %{binutils_version}

# Old prelink versions breaks the system with glibc 2.11
Conflicts:	prelink < 1:0.4.2-1.20091104.1mdv2010.1

BuildRequires:	texinfo
%if %{with pdf}
BuildRequires:	texlive
%endif
%if %{with utils}
BuildRequires:	gd-devel
%endif
%if %{enable_systap}
BuildRequires:	systemtap
%endif
%if %{enable_nsscrypt}
BuildRequires:	nss-devel
%endif
BuildRequires:	autoconf2.5
BuildRequires:	libcap-devel
BuildRequires:	rpm-mandriva-setup-build >= 1.133
BuildRequires:	rpm >= 1:5.4.4-20
BuildRequires:	spec-helper >= 0.31.2

Patch00:	glibc-fedora.patch
Patch01:	glibc-2.11.1-localedef-archive-follow-symlinks.patch
Patch04:	glibc-2.14.90-nss-upgrade.patch
Patch06:	glibc-2.9-share-locale.patch
Patch07:	glibc-2.3.6-nsswitch.conf.patch
Patch09:	glibc-2.2.4-xterm-xvt.patch
Patch13:	glibc-2.3.3-nscd-enable.patch
Patch14:	glibc-2.9-nscd-no-host-cache.patch
Patch17:	glibc-2.4.90-i386-hwcapinfo.patch
Patch18:	glibc-2.7-provide_CFI_for_the_outermost_function.patch
Patch19:	glibc-2.8-nscd-init-should-start.patch
Patch23:	glibc-2.3.4-timezone.patch
Patch24:	glibc-2.10.1-biarch-cpp-defines.patch
Patch27:	glibc-2.8-ENOTTY-fr-translation.patch
Patch29:	glibc-2.3.5-biarch-utils.patch
Patch30:	glibc-2.14.90-multiarch.patch
Patch31:	glibc-2.4.90-i586-hptiming.patch
Patch32:	glibc-2.3.4-i586-if-no-cmov.patch
Patch33:	glibc-2.3.6-pt_BR-i18nfixes.patch
Patch34:	glibc-2.4.90-testsuite-ldbl-bits.patch
Patch38:	glibc-2.4.90-testsuite-rt-notparallel.patch
Patch39:	glibc-2.10.1-mdv-owl-crypt_freesec.patch
Patch40:	glibc-2.9-avx-relocate_fcrypt.patch
Patch41:	glibc-2.3.6-avx-increase_BF_FRAME.patch
Patch42:	glibc-2.10.1-mdv-avx-owl-crypt.patch
Patch43:	glibc-2.7-mdv-wrapper_handle_sha.patch
Patch47:	glibc-2.13-fix-compile-error.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=638477#c275
# https://bugzilla.redhat.com/show_bug.cgi?id=696096
# https://bugzilla.redhat.com/attachment.cgi?id=491198
Patch49:	0001-x86_64-fix-for-new-memcpy-behavior.patch

# odd, for some reason the fedora patch applied earlier removes install of
# streams header.. just add them back for now :|
Patch50:	glibc-2.14.90-revert-fedora-not-installing-stream-headers.patch

# Requires to link thumb mode build
Patch51:	glibc-2.14-arm-thumb.patch

# http://sourceware.org/ml/libc-ports/2011-08/msg00000.html
Patch52:	glibc-2.14.90-arm-hardfp.patch
Patch53:	glibc-no-leaf-attribute.patch
Patch54:	glibc-2.14-394-g8f3b1ff-string-format-fixes.patch
Patch55:	glibc-localegrouping.patch
Patch56:	glibc-arenalock.patch
Patch57:	glibc-rh757881.patch
Patch58:	glibc-rh750858.patch
Patch59:	glibc-rh757887.patch

# Determine minimum kernel versions (rhbz#619538)
%define		enablekernel 2.6.32
Conflicts:	kernel < %{enablekernel}

# Don't try to explicitly provide GLIBC_PRIVATE versioned libraries
%define _provides_exceptions GLIBC_PRIVATE
%define _requires_exceptions GLIBC_PRIVATE

Obsoletes:	ld.so
Provides:	ld.so

%rename		ldconfig
Provides:	/sbin/ldconfig
Obsoletes:	nss_db

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

%if 0
%pre
#TODO: bail out if kernel < %{enablekernel}
%endif

%post -p %{_sbindir}/glibc_post_upgrade

%files		-f libc.lang
%if %{build_timezone}
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/localtime
%endif
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/nsswitch.conf
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/ld.so.conf
%dir %{_sysconfdir}/ld.so.conf.d
%config(noreplace) %{_sysconfdir}/rpc
%doc %dir %{_docdir}/glibc
%doc %{_docdir}/glibc/nss
%doc %{_docdir}/glibc/gai.conf
%doc %{_docdir}/glibc/COPYING
%doc %{_docdir}/glibc/COPYING.LIB
%{_mandir}/man1/*
%{_mandir}/man8/rpcinfo.8*
%{_mandir}/man8/ld.so*
%{_localedir}/locale.alias
/sbin/sln
%dir %{_prefix}/libexec/getconf
%{_prefix}/libexec/getconf/*
%{_slibdir}/ld-%{version}.so
%ifarch %{ix86}
%{_slibdir}/ld-linux.so.2
%{_slibdir}/i686
%endif
%ifarch x86_64
%{_slibdir}/ld-linux-x86-64.so.2
%endif
%ifarch %{arm}
%{_slibdir}/ld-linux.so.3
%endif
%{_slibdir}/lib*-[.0-9]*.so
%{_slibdir}/lib*.so.[0-9]*
%{_slibdir}/libSegFault.so
%dir %{_libdir}/audit
%{_libdir}/audit/sotruss-lib.so
%dir %{_libdir}/gconv
%{_libdir}/gconv/*.so
%{_libdir}/gconv/gconv-modules
%ghost %{_libdir}/gconv/gconv-modules.cache
%attr(4755,root,root) %{_prefix}/libexec/pt_chown
%{_bindir}/catchsegv
%{_bindir}/gencat
%{_bindir}/getconf
%{_bindir}/getent
%{_bindir}/iconv
%{_bindir}/ldd
%ifarch %{ix86} x86_64
%{_bindir}/lddlibc4
%endif
%{_bindir}/locale
%{_bindir}/localedef
%{_bindir}/makedb
%{_bindir}/pldd
%{_bindir}/rpcgen
%{_bindir}/sotruss
%{_bindir}/sprof
%{_bindir}/tzselect
%{_sbindir}/iconvconfig
%{_sbindir}/glibc_post_upgrade
%if %{build_multiarch}
%{_slibdir32}/ld-%{version}.so
%{_slibdir32}/ld-linux*.so.2
%{_slibdir32}/lib*-[.0-9]*.so
%{_slibdir32}/lib*.so.[0-9]*
%{_slibdir32}/libSegFault.so
%dir %{_libdir32}/audit
%{_libdir32}/audit/sotruss-lib.so
%dir %{_libdir32}/gconv
%{_libdir32}/gconv/*.so
%{_libdir32}/gconv/gconv-modules
%endif
/sbin/ldconfig
%{_mandir}/man8/ldconfig*
%ghost %{_sysconfdir}/ld.so.cache
%dir %{_var}/cache/ldconfig
%ghost %{_var}/cache/ldconfig/aux-cache
%{_var}/lib/rpm/filetriggers/ldconfig.*
%{_var}/db/Makefile

#-----------------------------------------------------------------------
%package	devel
Summary:	Header and object files for development using standard C libraries
Group:		Development/C
Requires(post):	info-install
Requires(preun):info-install
Requires(post):	coreutils
Requires(postun):coreutils, awk
Requires:	%{name} = %{EVRD}
Requires:	kernel-headers
Provides:	glibc-crypt_blowfish-devel = %{crypt_bf_ver}
%rename		glibc-doc
%if %{with pdf}
%rename		glibc-doc-pdf
%endif

%description	devel
The glibc-devel package contains the header and object files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard header and object files available in order to create the
executables.

%post		devel
    %_install_info libc.info

%preun		devel
    %_remove_install_info libc.info

%files		devel
%{_includedir}/*
%{_libdir}/*.o
%{_libdir}/*.so
%{_libdir}/libbsd-compat.a
%{_libdir}/libbsd.a
%{_libdir}/libc_nonshared.a
%{_libdir}/libg.a
%{_libdir}/libieee.a
%{_libdir}/libmcheck.a
%{_libdir}/libpthread_nonshared.a
%{_libdir}/librpcsvc.a
%if %{build_multiarch}
%{_libdir32}/*.o
%{_libdir32}/*.so
%{_libdir32}/libbsd-compat.a
%{_libdir32}/libbsd.a
%{_libdir32}/libc_nonshared.a
%{_libdir32}/libg.a
%{_libdir32}/libieee.a
%{_libdir32}/libmcheck.a
%{_libdir32}/libpthread_nonshared.a
%{_libdir32}/librpcsvc.a
%endif
%{_mandir}/man3/*
%{_infodir}/libc.info*
%doc %{_docdir}/glibc/*
%exclude %{_docdir}/glibc/nss
%exclude %{_docdir}/glibc/gai.conf
%exclude %{_docdir}/glibc/COPYING
%exclude %{_docdir}/glibc/COPYING.LIB

#-----------------------------------------------------------------------
%package	static-devel
Summary:	Static libraries for GNU C library
Group:		Development/C
Requires:	%{name}-devel = %{EVRD}

%description	static-devel
The glibc-static-devel package contains the static libraries necessary
for developing programs which use the standard C libraries. Install
glibc-static-devel if you need to statically link your program or
library.

%files		static-devel
%{_libdir}/libBrokenLocale.a
%{_libdir}/libanl.a
%{_libdir}/libc.a
%{_libdir}/libcrypt.a
%{_libdir}/libdl.a
%{_libdir}/libm.a
%{_libdir}/libnsl.a
%{_libdir}/libpthread.a
%{_libdir}/libresolv.a
%{_libdir}/librt.a
%{_libdir}/libutil.a
%if %{build_multiarch}
%{_libdir32}/libBrokenLocale.a
%{_libdir32}/libanl.a
%{_libdir32}/libc.a
%{_libdir32}/libcrypt.a
%{_libdir32}/libdl.a
%{_libdir32}/libm.a
%{_libdir32}/libnsl.a
%{_libdir32}/libpthread.a
%{_libdir32}/libresolv.a
%{_libdir32}/librt.a
%{_libdir32}/libutil.a
%endif

########################################################################
%if %{build_nscd}
#-----------------------------------------------------------------------
%package	-n nscd
Summary:	A Name Service Caching Daemon (nscd)
Group:		System/Servers
Conflicts:	kernel < 2.2.0
Requires(pre):	rpm-helper
Requires(preun):rpm-helper
Requires(post):	rpm-helper
Requires(postun):rpm-helper

%description	-n nscd
Nscd caches name service lookups and can dramatically improve
performance with NIS+, and may help with DNS as well.

%pre -n nscd
    %_pre_useradd nscd / /sbin/nologin

%post -n nscd
    %_post_service nscd

%preun -n nscd
    %_preun_service nscd

%postun -n nscd
    %_postun_userdel nscd
    if [ "$1" -ge "1" ]; then
	/sbin/service nscd condrestart > /dev/null 2>&1 || :
    fi

%files		-n nscd
%config(noreplace) %{_sysconfdir}/nscd.conf
%config(noreplace) %{_initrddir}/nscd
%{_sbindir}/nscd
#-----------------------------------------------------------------------
# build_nscd
%endif

########################################################################
%if %{with utils}
#-----------------------------------------------------------------------
%package	utils
Summary:	Development utilities from GNU C library
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description	utils
The glibc-utils package contains memusage, a memory usage profiler,
mtrace, a memory leak tracer and xtrace, a function call tracer which
can be helpful during program debugging.

If unsure if you need this, don't install this package.

%files		utils
%{_bindir}/memusage
%{_bindir}/memusagestat
%{_bindir}/mtrace
%{_bindir}/pcprofiledump
%{_bindir}/xtrace
%{_slibdir}/libmemusage.so
%{_slibdir}/libpcprofile.so
%if %{build_multiarch}
%{_slibdir32}/libmemusage.so
%{_slibdir32}/libpcprofile.so
%endif
#-----------------------------------------------------------------------
# with utils
%endif

########################################################################
%if %{build_i18ndata}
#-----------------------------------------------------------------------
%package	i18ndata
Summary:	Database sources for 'locale'
Group:		System/Libraries
%rename		glibc-localedata

%description	i18ndata
This package contains the data needed to build the locale data files
to use the internationalization features of the GNU libc.

%files		i18ndata
%dir %{_datadir}/i18n
%dir %{_datadir}/i18n/charmaps
%{_datadir}/i18n/charmaps/*
%dir %{_datadir}/i18n/locales
%{_datadir}/i18n/locales/*
%{_datadir}/i18n/SUPPORTED
#-----------------------------------------------------------------------
# build_i18ndata
%endif

########################################################################
%if %{build_timezone}
#-----------------------------------------------------------------------
%package	-n timezone
Summary:	Time zone descriptions
Group:		System/Base
Obsoletes:	zoneinfo

%description	-n timezone
These are configuration files that describe possible time zones.

%files		-n timezone
%{_sbindir}/zdump
%{_sbindir}/zic
%{_mandir}/man1/zdump.1*
%{_datadir}/zoneinfo
#-----------------------------------------------------------------------
# build_timezone
%endif

########################################################################
%prep
%setup -q -n %{glibcsrcdir} -b 2 -a 3 -a 50
%if %{build_ports}
tar -xf %{SOURCE8}
mv %{glibcportsdir} ports
%patch51 -p1
%ifarch armv7hl
%patch52 -p1
%endif
%endif

%patch00 -p1 -b .fedora~
%patch01 -p1 -b .localedef-archive-follow-symlinks
%patch04 -p1 -b .nss-upgrade
%patch06 -p1 -b .share-locale
%patch07 -p1 -b .nsswitch.conf
%patch09 -p1 -b .xterm-xvt
%patch13 -p1 -b .nscd-enable
%patch14 -p1 -b .nscd-no-host-cache
%patch17 -p1 -b .i386-hwcapinfo
%patch18 -p0 -R -b .provide_CFI_for_the_outermost_function
%patch19 -p1 -b .nscd-init-should-start
%patch23 -p1 -b .timezone
%patch24 -p1 -b .biarch-cpp-defines
%patch27 -p1 -b .ENOTTY-fr-translation
%patch29 -p1 -b .biarch-utils
%patch30 -p1 -b .multiarch-check
%patch31 -p1 -b .i586-hptiming
%patch32 -p1 -b .i586-if-no-cmov
%patch33 -p1 -b .pt_BR-i18nfixes
%patch34 -p1 -b .testsuite-ldbl-bits
%patch38 -p1 -b .testsuite-rt-notparallel
%patch47 -p0 -b .fix-compile-error
%patch49 -p1 -b .memcpy
%patch50 -p1 -b .fed_streams~
%patch53 -p1 -b .leaf~
%patch54 -p1 -b .str_fmt~
%patch55 -p1 -b .localegrouping~
%patch56 -p1 -b .arenalock~
%patch57 -p1 -b .rh757881~
%patch58 -p1 -b .rh750858~
%patch59 -p1 -b .rh757887~

# copy freesec source
cp %{_sourcedir}/crypt_freesec.[ch] crypt/
echo "Applying crypt_blowfish patch:"
%patch42 -p1 -b .mdv-avx-owl-crypt
#patch -p1 -s < crypt_blowfish-%{crypt_bf_ver}/glibc-2.3.2-crypt.diff
mv crypt/crypt.h crypt/gnu-crypt.h
cp -a crypt_blowfish-%{crypt_bf_ver}/*.[chS] crypt/

## FreeSec support for extended/new-style/BSDI hashes in crypt(3)
%patch39 -p1 -b .mdv-owl-crypt_freesec
%patch40 -p1 -b .avx-relocate_fcrypt
%patch41 -p0 -b .avx-increase_BF_FRAME
# add sha256-crypt and sha512-crypt support to the Openwall wrapper
%patch43 -p1 -b .mdv-wrapper_handle_sha

%if %{build_selinux}
    # XXX kludge to build nscd with selinux support as it added -nostdinc
    # so /usr/include/selinux is not found
    ln -s %{_includedir}/selinux selinux
%endif

find . -type f -size 0 -o -name "*.orig" -exec rm -f {} \;

# Remove patch backups from files we ship in glibc packages
rm -f ChangeLog.[^0-9]*
rm -f localedata/locales/{???_??,??_??}.*
rm -f localedata/locales/[a-z_]*.*

#-----------------------------------------------------------------------
%build
# Prepare test matrix in the next function
> %{checklist}

#
# CompareKver <kernel version>
# function to compare the desired kernel version with running kernel
# version (package releases not taken into account in comparison). The
# function returns:
# -1 = <kernel version> is lesser than current running kernel
#  0 = <kernel version> is equal to the current running kernel
#  1 = <kernel version> is greater than current running kernel
#
function CompareKver() {
  v1=`echo $1 | sed 's/\.\?$/./'`
  v2=`uname -r | sed 's/[^.0-9].*//' | sed 's/\.\?$/./'`
  n=1
  s=0
  while true; do
    c1=`echo "$v1" | cut -d "." -f $n`
    c2=`echo "$v2" | cut -d "." -f $n`
    if [ -z "$c1" -a -z "$c2" ]; then
      break
    elif [ -z "$c1" ]; then
      s=-1
      break
    elif [ -z "$c2" ]; then
      s=1
      break
    elif [ "$c1" -gt "$c2" ]; then
      s=1
      break
    elif [ "$c2" -gt "$c1" ]; then
      s=-1
      break
    fi
    n=$((n + 1))
  done
  echo $s
}

#
# BuildGlibc <arch> [<extra_configure_options>+]
#
function BuildGlibc() {
  arch="$1"
  shift 1

  # Select optimization flags and compiler to use
  BuildAltArch="no"
  BuildCompFlags=""
  BuildFlags=""
  case $arch in
    i[3-6]86)
%ifarch x86_64
	BuildFlags="-march=pentium4 -mtune=generic"
	BuildAltArch="yes"
	BuildCompFlags="-m32"
%else
	BuildFlags="-march=$arch -mtune=generic"
%endif
      ;;
    x86_64)
      BuildFlags="-mtune=generic"
      ;;
    armv5t*)
      BuildFlags="-march=armv5t"
      BuildCompFlags="-march=armv5t"
      ;;
    # to check
    armv7*)
      BuildFlags="-march=armv7-a"
      BuildCompFlags="-march=armv7-a"
      ;;
  esac

  # Choose multiarch support
  MultiArchFlags=
  case $arch in
    i686 | x86_64)
      MultiArchFlags="--enable-multi-arch"
      ;;
  esac

  # Determine C & C++ compilers
  BuildCC="%{__cc} $BuildCompFlags"
  BuildCXX="%{__cxx} $BuildCompFlags"

  BuildFlags="$BuildFlags -DNDEBUG=1 %{__common_cflags} -O3"

  # XXX: -frecord-gcc-switches makes gold abort with assertion error and gcc segfault :|
  BuildFlags="$(echo $BuildFlags |sed -e 's#-frecord-gcc-switches##g')"


  # Do not use direct references against %gs when accessing tls data
  # XXX make it the default in GCC? (for other non glibc specific usage)
%ifarch %{xenarches}
  BuildFlags="$BuildFlags -mno-tls-direct-seg-refs"
%endif

  # Extra configure flags
  ExtraFlags=

   # We'll be having issues with biarch builds of these two as longs as their
   # build dependencies aren't provided as biarch packages as well.
   # But as the alternate arch is less likely to make any use of the
   # functionality and that we might just ditch biarch packaging completely,
   # we just enable it on the main arch for now.
%if %{enable_nsscrypt} || %{enable_systap}
   if [[ "$BuildAltArch" = "no" ]]; then
%if %{enable_nsscrypt}
   ExtraFlags="$ExtraFlags --enable-nss-crypt"
%endif
%if %{enable_systap}
   ExtraFlags="$ExtraFlags --enable-systemtap"
%endif
   fi
%endif

  # NPTL+TLS are now the default
%if %{build_ports}
  Pthreads="ports,nptl"
%else
  Pthreads="nptl"
%endif

  # Add-ons
  AddOns="$Pthreads,libidn"

  # Force a separate and clean object dir
  rm -rf build-$arch-linux
  mkdir  build-$arch-linux
  pushd  build-$arch-linux
  [[ "$BuildAltArch" = "yes" ]] && touch ".alt" || touch ".main"
  CC="$BuildCC" CXX="$BuildCXX" CFLAGS="$BuildFlags" LDFLAGS="%{ldflags}" ../configure \
    $arch-%{_target_vendor}-%{_target_os}%{?_gnu} \
    --prefix=%{_prefix} \
    --libexecdir=%{_prefix}/libexec \
    --infodir=%{_infodir} \
    --enable-add-ons=$AddOns \
    --disable-profile \
%if %{build_selinux}
    --with-selinux \
%else
    --without-selinux \
%endif
    --enable-bind-now \
    $ExtraFlags \
    $MultiArchFlags \
    --enable-kernel=%{enablekernel} \
    --with-headers=%{_includedir} ${1+"$@"}
  %make -r
  popd

  check_flags="-k"

  # Generate test matrix
  [[ -d "build-$arch-linux" ]] || {
    echo "ERROR: PrepareGlibcTest: build-$arch-linux does not exist!"
    return 1
  }
  local BuildJobs="-j`getconf _NPROCESSORS_ONLN`"
  echo "$BuildJobs -d build-$arch-linux $check_flags" >> %{checklist}

  case $arch in
  i686)		base_arch=i586;;
  *)		base_arch=none;;
  esac

  [[ -d "build-$base_arch-linux" ]] && {
    check_flags="$check_flags -l build-$base_arch-linux/elf/ld.so"
    echo "$BuildJobs -d build-$arch-linux $check_flags" >> %{checklist}
  }
  return 0
}

# Build main glibc
BuildGlibc %{_target_cpu}

%if %{build_multiarch}
    %ifarch x86_64
	BuildGlibc i686
    %endif
%else
    # Build i686 libraries if not already building for i686
    case %{_target_cpu} in
    i686)
	;;
    i[3-5]86)
	BuildGlibc i686
	;;
    esac
%endif

make -C crypt_blowfish-%{crypt_bf_ver} man

# post install wrapper
gcc -static -Lbuild-%{_target_cpu}-linux %{optflags} -Os fedora/glibc_post_upgrade.c -o build-%{_target_cpu}-linux/glibc_post_upgrade \
  '-DLIBTLS="/%{_lib}/tls/"' \
  '-DGCONV_MODULES_DIR="%{_libdir}/gconv"' \
  '-DLD_SO_CONF="/etc/ld.so.conf"' \
  '-DICONVCONFIG="%{_sbindir}/iconvconfig"'

#-----------------------------------------------------------------------
%check
export TMPDIR=/tmp
export TIMEOUTFACTOR=16
while read arglist; do
  %{SOURCE5} $arglist || exit 1
done < %{checklist}

#-----------------------------------------------------------------------
%install
%if %{build_multiarch}
    %ifarch x86_64
	ALT_ARCH=i686
    %endif
    %make install install_root=%{buildroot} -C build-${ALT_ARCH}-linux
%endif
%make install install_root=%{buildroot} -C build-%{_target_cpu}-linux

install -m700 build-%{_target_cpu}-linux/glibc_post_upgrade -D %{buildroot}%{_sbindir}/glibc_post_upgrade
sh manpages/Script.sh

# Install extra glibc libraries
function InstallGlibc() {
  local BuildDir="$1"
  local SubDir="$2"
  local LibDir="$3"

  [[ -z "$LibDir" ]] && LibDir="%{_slibdir}"

  pushd $BuildDir
  mkdir -p %{buildroot}$LibDir/$SubDir/
  install -m755 libc.so %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libc-*.so`
  ln -sf `basename %{buildroot}$LibDir/libc-*.so` %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libc.so.*`
  install -m755 math/libm.so %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libm-*.so`
  ln -sf `basename %{buildroot}$LibDir/libm-*.so` %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libm.so.*`
  install -m755 nptl/libpthread.so %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libpthread-*.so`
  ln -sf `basename %{buildroot}$LibDir/libpthread-*.so` %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libpthread.so.*`
  install -m755 nptl_db/libthread_db.so %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libthread_db-*.so`
  ln -sf `basename %{buildroot}$LibDir/libthread_db-*.so` %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/libthread_db.so.*`
  install -m755 rt/librt.so %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/librt-*.so`
  ln -sf `basename %{buildroot}$LibDir/librt-*.so` %{buildroot}$LibDir/$SubDir/`basename %{buildroot}$LibDir/librt.so.*`
  popd
}

# Install arch-specific optimized libraries
case %{_target_cpu} in
i[3-5]86)
  InstallGlibc build-i686-linux i686
  ;;
esac

# NPTL <bits/stdio-lock.h> is not usable outside of glibc, so include
# the generic one (RH#162634)
install -m644 bits/stdio-lock.h -D %{buildroot}%{_includedir}/bits/stdio-lock.h
# And <bits/libc-lock.h> needs sanitizing as well.
install -m644 fedora/libc-lock.h -D %{buildroot}%{_includedir}/bits/libc-lock.h

# Compatibility hack: this locale has vanished from glibc, but some other
# programs are still using it. Normally we would handle it in the %pre
# section but with glibc that is simply not an option
mkdir -p %{buildroot}%{_localedir}/ru_RU/LC_MESSAGES

# Remove the files we don't want to distribute
rm -f %{buildroot}%{_libdir}/libNoVersion*
rm -f %{buildroot}%{_slibdir}/libNoVersion*

ln -sf libbsd-compat.a %{buildroot}%{_libdir}/libbsd.a
%if %{build_multiarch}
    ln -sf libbsd-compat.a %{buildroot}%{_libdir32}/libbsd.a
%endif

install -m 644 mandriva/nsswitch.conf %{buildroot}%{_sysconfdir}/nsswitch.conf

# This is for ncsd - in glibc 2.2
%if %{build_nscd}
    install -m 644 nscd/nscd.conf %{buildroot}%{_sysconfdir}
    mkdir -p %{buildroot}%{_initrddir}
    install -m 755 nscd/nscd.init %{buildroot}%{_initrddir}/nscd
%endif

# These man pages require special attention
mkdir -p %{buildroot}%{_mandir}/man3
install -p -m 0644 crypt_blowfish-%{crypt_bf_ver}/*.3 %{buildroot}%{_mandir}/man3/

# Useless and takes place
rm -rf %{buildroot}/%{_datadir}/zoneinfo/{posix,right}

# Include ld.so.conf
echo "include /etc/ld.so.conf.d/*.conf" > %{buildroot}%{_sysconfdir}/ld.so.conf
chmod 644 %{buildroot}%{_sysconfdir}/ld.so.conf
mkdir -p  %{buildroot}%{_sysconfdir}/ld.so.conf.d

# ldconfig cache
mkdir -p %{buildroot}%{_var}/cache/ldconfig
touch %{buildroot}%{_var}/cache/ldconfig/aux-cache

# automatic ldconfig cache update on rpm installs/removals
# (see http://wiki.mandriva.com/en/Rpm_filetriggers)
install -d %{buildroot}%{_var}/lib/rpm/filetriggers
cat > %{buildroot}%{_var}/lib/rpm/filetriggers/ldconfig.filter << EOF
^.((/lib|/usr/lib)(64)?/[^/]*\.so\.|/etc/ld.so.conf.d/[^/]*\.conf)
EOF
cat > %{buildroot}%{_var}/lib/rpm/filetriggers/ldconfig.script << EOF
#!/bin/sh
ldconfig -X
EOF
chmod 755 %{buildroot}%{_var}/lib/rpm/filetriggers/ldconfig.script

# Include %{_libdir}/gconv/gconv-modules.cache
touch %{buildroot}%{_libdir}/gconv/gconv-modules.cache
chmod 644 %{buildroot}%{_libdir}/gconv/gconv-modules.cache

touch %{buildroot}%{_sysconfdir}/ld.so.cache

# Strip debugging info from all static libraries
pushd %{buildroot}%{_libdir}
    for i in *.a; do
	if [ -f "$i" ]; then
	    strip -g -R .comment -R .GCC.command.line $i
	fi
    done
popd

# rquota.x and rquota.h are now provided by quota
rm -f %{buildroot}%{_includedir}/rpcsvc/rquota.[hx]

%if %{build_i18ndata}
    install -m644 localedata/SUPPORTED %{buildroot}%{_datadir}/i18n/
%endif

rm -rf %{buildroot}%{_includedir}/netatalk/

# /etc/localtime - we're proud of our timezone #Well we(mdk) may put Paris
%if %{build_timezone}
    rm -f %{buildroot}%{_sysconfdir}/localtime
    cp -f %{buildroot}%{_datadir}/zoneinfo/US/Eastern %{buildroot}%{_sysconfdir}/localtime
    #ln -sf ..%{_datadir}/zoneinfo/US/Eastern %{buildroot}%{_sysconfdir}/localtime
%endif

install -m 755 -d %{buildroot}%{_docdir}/glibc
%if %{with doc}
    make -C build-%{_target_cpu}-linux html
    cp -fpar manual/libc %{buildroot}%{_docdir}/glibc/html
%endif
%if %{with pdf}
    make -C build-%{_target_cpu}-linux pdf
    install -m644 -D manual/libc.pdf %{buildroot}%{_docdir}/glibc/libc.pdf
%endif

# the last bit: more documentation
install -m 644 COPYING COPYING.LIB README NEWS INSTALL FAQ BUGS		\
    NOTES PROJECTS CONFORMANCE README.libm hesiod/README.hesiod		\
    ChangeLog* crypt/README.ufc-crypt nis/nss posix/gai.conf		\
    %{buildroot}%{_docdir}/glibc
xz -0 --text %{buildroot}%{_docdir}/glibc/ChangeLog*
install -m 644 timezone/README %{buildroot}%{_docdir}/glibc/README.timezone
install -m 755 -d %{buildroot}%{_docdir}/glibc/crypt_blowfish
install -m 644 crypt_blowfish-%{crypt_bf_ver}/{README,LINKS,PERFORMANCE} \
    %{buildroot}%{_docdir}/glibc/crypt_blowfish

# Generate localized libc.mo files list
%find_lang libc

# Remove unpackaged files
rm -f  %{buildroot}%{_infodir}/dir.old*
rm -rf %{buildroot}%{_includedir}/asm-*/mach-*/
rm -f  %{buildroot}%{_localedir}/locale-archive*
# XXX: verify
find %{buildroot}%{_localedir} -type f -name LC_\* -o -name SYS_LC_\* |xargs rm -f

%if !%{build_nscd}
    rm -f %{buildroot}%{_sbindir}/nscd
%endif

rm -f %{buildroot}%{_infodir}/dir

%if %{without utils}
    rm -f  %{buildroot}%{_bindir}/memusage
    rm -f  %{buildroot}%{_bindir}/memusagestat
    rm -f  %{buildroot}%{_bindir}/mtrace
    rm -f  %{buildroot}%{_bindir}/pcprofiledump
    rm -f  %{buildroot}%{_bindir}/xtrace
    rm -f  %{buildroot}%{_slibdir}/libmemusage.so
    rm -f  %{buildroot}%{_slibdir}/libpcprofile.so
    %if %{build_multiarch}
	rm -f  %{buildroot}%{_slibdir32}/libmemusage.so
	rm -f  %{buildroot}%{_slibdir32}/libpcprofile.so
    %endif
%endif

%if !%{build_timezone}
    rm -f  %{buildroot}%{_sysconfdir}/localtime
    rm -f  %{buildroot}%{_sbindir}/zdump
    rm -f  %{buildroot}%{_sbindir}/zic
    rm -f  %{buildroot}%{_mandir}/man1/zdump.1*
    rm -rf %{buildroot}%{_datadir}/zoneinfo
%endif

%if !%{build_i18ndata}
    rm -rf %{buildroot}%{_datadir}/i18n
%endif

# This will make the '-g' argument to be passed to eu-strip for these libraries, so that
# some info is kept that's required to make valgrind work without depending on glibc-debug
# package to be installed.
export EXCLUDE_FROM_FULL_STRIP="ld-%{version}.so libpthread libc-%{version}.so"
