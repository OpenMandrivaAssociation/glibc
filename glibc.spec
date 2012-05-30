# CVS snapshots of glibc
%define RELEASE		0
%if %{RELEASE}
%define glibcsrcdir	glibc-%{version}
%define glibcportsdir	glibc-%{version}
%else
%define glibcsrcdir	glibc-2.15-a316c1f
%define glibcportsdir	glibc-ports-2.15-ad8ae7d
%endif

%define	checklist	%{_builddir}/%{glibcsrcdir}/Check.list

# crypt blowfish support
%define crypt_bf_ver	1.2

%define _slibdir	/%{_lib}
%define _slibdir32	/lib
%define _libdir32	%{_prefix}/lib

%define		libc_major		6
%define		libc			%mklibname c %{libc_major}
%define		libc_devel		%mklibname -d c
%define		libc_static_devel	%mklibname -d -s c
%define		multilibc		libc%{libc_major}

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
Version:	2.15
Release:	3
Epoch:		6
License:	LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
Group:		System/Libraries
Url:		http://www.gnu.org/software/libc/

# FSF source
Source0:	http://ftp.gnu.org/gnu/glibc/%{glibcsrcdir}.tar.gz
%if %{RELEASE}
Source1:	http://ftp.gnu.org/gnu/glibc/%{glibcsrcdir}.tar.gz.sig
%endif

# Fedora tarball
Source2:	%{glibcsrcdir}-fedora.tar.gz
Source3:	glibc-manpages.tar.bz2
Source5:	glibc-check.sh

Source8:	http://ftp.gnu.org/gnu/glibc/%{glibcportsdir}.tar.gz
%if %{RELEASE}
Source9:	http://ftp.gnu.org/gnu/glibc/%{glibcportsdir}.tar.gz.sig
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
BuildRequires:	cap-devel

#-----------------------------------------------------------------------
# from fedora glibc.spec
Patch00:	glibc-fedora.patch
Patch01:	glibc-stap.patch

#-----------------------------------------------------------------------
# mandriva patches
Patch02:	glibc-2.11.1-localedef-archive-follow-symlinks.patch
Patch03:	glibc-2.15-fix-dns-with-broken-routers.patch
Patch04:	glibc-2.14.90-nss-upgrade.patch
Patch05:	glibc-2.9-share-locale.patch
Patch06:	glibc-2.3.6-nsswitch.conf.patch
Patch07:	glibc-2.2.4-xterm-xvt.patch
Patch08:	glibc-2.3.3-nscd-enable.patch
Patch09:	glibc-2.9-nscd-no-host-cache.patch
Patch10:	glibc-2.4.90-i386-hwcapinfo.patch
Patch11:	glibc-2.8-nscd-init-should-start.patch
Patch12:	glibc-2.3.4-timezone.patch
Patch13:	glibc-2.10.1-biarch-cpp-defines.patch
Patch14:	glibc-2.8-ENOTTY-fr-translation.patch
Patch15:	glibc-2.3.5-biarch-utils.patch
Patch16:	glibc-2.15-multiarch.patch
Patch17:	glibc-2.4.90-i586-hptiming.patch
Patch18:	glibc-2.3.4-i586-if-no-cmov.patch
Patch19:	glibc-2.3.6-pt_BR-i18nfixes.patch
Patch20:	glibc-2.4.90-testsuite-ldbl-bits.patch
Patch21:	glibc-2.4.90-testsuite-rt-notparallel.patch
Patch22:	glibc-2.13-fix-compile-error.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=638477#c275
# https://bugzilla.redhat.com/show_bug.cgi?id=696096
# https://bugzilla.redhat.com/attachment.cgi?id=491198
Patch23:	0001-x86_64-fix-for-new-memcpy-behavior.patch

# odd, for some reason the fedora patch applied earlier removes install of
# streams header.. just add them back for now :|
Patch24:	glibc-2.14.90-revert-fedora-not-installing-stream-headers.patch

Patch25:	glibc-no-leaf-attribute.patch
Patch26:	glibc-2.14-394-g8f3b1ff-string-format-fixes.patch

#-----------------------------------------------------------------------
# from fedora glibc.spec
# Uli wants to see this undergo more analyis (what happens when thread B calls into malloc when
# thread A has unlocked on the error path
# There's an alternate approach using mmap after detecting an error that needs discussion
Patch27:	glibc-rh757881.patch
# From upstream.
Patch28:	glibc-rh740506.patch
# Not sure of upstream status
Patch29:	glibc-rh730856.patch
# Follow-on to 552960's original patch to avoid losing wakeups
Patch30:	glibc-rh552960-2.patch
Patch31: 	glibc-rh729661.patch
Patch32: 	glibc-rh446078.patch
Patch33: 	glibc-rh454629.patch
Patch34: 	glibc-rh784402.patch
Patch35: 	glibc-rh622499.patch
# Depends on systemtap infrastructure, so can't go upstream
Patch36: 	glibc-rh179072.patch
Patch37: 	glibc-rh697421.patch
Patch38: 	glibc-rh740682.patch
Patch39: 	glibc-sw13618.patch
# Fix bogus sorting code which was copied from dl-deps.
Patch40: 	glibc-sw13618-2.patch
Patch41: 	glibc-rh783979.patch
# Needs to go upstream
Patch42: 	glibc-rh657588.patch
Patch43:	glibc-rh787201.patch
# Sent upstream, awaiting feedback
Patch44: 	glibc-rh741105.patch
# Sent upstream, awaiting feedback
Patch45: 	glibc-rh770869.patch
# Sent upstream, awaiting feedback
Patch46: 	glibc-rh691912.patch
# Not necessary to send upstream
Patch47: 	glibc-rh688948.patch
# Rakesh & Pravin will send upstream
Patch48: 	glibc-rh770439.patch
# Sent upstream
Patch49: 	glibc-rh789209.patch
# Was acked in the upstream BZ, but patch never got installed
Patch50: 	glibc-rh624296.patch
# Needs to be sent upstream
Patch51: 	glibc-rh564528.patch

#-----------------------------------------------------------------------
# mandriva patches
Patch52:	glibc-2.10.1-mdv-avx-owl-crypt.patch
Patch53:	glibc-2.10.1-mdv-owl-crypt_freesec.patch

Patch54:	glibc-2.9-avx-relocate_fcrypt.patch
Patch55:	glibc-2.3.6-avx-increase_BF_FRAME.patch
Patch56:	glibc-2.7-mdv-wrapper_handle_sha.patch

# Requires to link thumb mode build
Patch57:	glibc-2.14-arm-thumb.patch

# FIXME this patch is hackish but corrects the problem for me
# in upstream bugreport, what others apparently did was to
# revert 3a2c02424d9824f5cdea4ebd32ff929b2b1f49c6
# http://sourceware.org/bugzilla/show_bug.cgi?id=13594
Patch58:	glibc-2.15-chromium-browser-crash.patch

# Determine minimum kernel versions (rhbz#619538)
%define		enablekernel 2.6.32
Conflicts:	kernel < %{enablekernel}

# Don't try to explicitly provide GLIBC_PRIVATE versioned libraries
%define _filter_GLIBC_PRIVATE 1

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

%post -p %{_sbindir}/glibc_post_upgrade

%files -f	libc.lang
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
%{_prefix}/libexec/getconf
%ifarch x86_64
%exclude %{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFF32
%exclude %{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFFBIG
%exclude %{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFF32
%exclude %{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFFBIG
%exclude %{_prefix}/libexec/getconf/XBS5_ILP32_OFF32
%exclude %{_prefix}/libexec/getconf/XBS5_ILP32_OFFBIG
%endif
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
%ifarch %{ix86}
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
/sbin/ldconfig
%{_mandir}/man8/ldconfig*
%ghost %{_sysconfdir}/ld.so.cache
%dir %{_var}/cache/ldconfig
%ghost %{_var}/cache/ldconfig/aux-cache
%{_var}/lib/rpm/filetriggers/ldconfig.*
%{_var}/db/Makefile

########################################################################
%if %{build_multiarch}
#-----------------------------------------------------------------------
%package -n	%{multilibc}
Summary:	The GNU libc libraries
Group:		System/Libraries
Conflicts:	glibc < 6:2.14.90-13

%post -n	%{multilibc}
    %{_sbindir}/iconvconfig %{_libdir32}/gconv -o %{_libdir32}/gconv/gconv-modules.cache

%description -n	%{multilibc}
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

%files -n	%{multilibc}
%{_slibdir32}/ld-%{version}.so
%{_slibdir32}/ld-linux*.so.2
%{_slibdir32}/lib*-[.0-9]*.so
%{_slibdir32}/lib*.so.[0-9]*
%{_slibdir32}/libSegFault.so
%dir %{_libdir32}/audit
%{_libdir32}/audit/sotruss-lib.so
%{_libdir32}/gconv/*.so
%{_libdir32}/gconv/gconv-modules
%ghost %{_libdir32}/gconv/gconv-modules.cache
%{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFF32
%{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFFBIG
%{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFF32
%{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFFBIG
%{_prefix}/libexec/getconf/XBS5_ILP32_OFF32
%{_prefix}/libexec/getconf/XBS5_ILP32_OFFBIG
#-----------------------------------------------------------------------
# build_multiarch
%endif

#-----------------------------------------------------------------------
%package	devel
Summary:	Header and object files for development using standard C libraries
Group:		Development/C
Requires:	%{name} = %{EVRD}
%if %{build_multiarch}
Requires:	%{multilibc} = %{EVRD}
%endif
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

%files		devel
%{_mandir}/man3/*
%{_infodir}/libc.info*
%doc %{_docdir}/glibc/*
%exclude %{_docdir}/glibc/nss
%exclude %{_docdir}/glibc/gai.conf
%exclude %{_docdir}/glibc/COPYING
%exclude %{_docdir}/glibc/COPYING.LIB
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
%package -n	nscd
Summary:	A Name Service Caching Daemon (nscd)
Group:		System/Servers
Conflicts:	kernel < 2.2.0
Requires(pre):	rpm-helper
Requires(preun):rpm-helper
Requires(post):	rpm-helper
Requires(postun):rpm-helper

%description -n	nscd
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

%files -n 	nscd
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
%package -n	timezone
Summary:	Time zone descriptions
Group:		System/Base
Obsoletes:	zoneinfo

%description -n	timezone
These are configuration files that describe possible time zones.

%files -n	timezone
%{_sbindir}/zdump
%{_sbindir}/zic
%{_mandir}/man1/zdump.1*
%{_datadir}/zoneinfo
#-----------------------------------------------------------------------
# build_timezone
%endif

########################################################################
%prep
%setup -q -n %{glibcsrcdir} -b 2 -a 3 -a 8 -a 50

%patch00 -p1
%patch01 -p1
%patch02 -p1
%patch03 -p1
%patch04 -p1
%patch05 -p1
%patch06 -p1
%patch07 -p1
%patch08 -p1
%patch09 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p0
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1
%patch27 -p1
%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1
%patch38 -p1
%patch39 -p1
%patch40 -p1
%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1
%patch46 -p1
%patch47 -p1
%patch48 -p1
%patch49 -p1
%patch50 -p1
%patch51 -p1

# copy freesec source
cp %{SOURCE52} %{SOURCE53} crypt/
echo "Applying crypt_blowfish patch:"
%patch52 -p1
mv crypt/crypt.h crypt/gnu-crypt.h
cp -a crypt_blowfish-%{crypt_bf_ver}/*.[chS] crypt/

## FreeSec support for extended/new-style/BSDI hashes in crypt(3)
%patch53 -p1
%patch54 -p1
%patch55 -p0
# add sha256-crypt and sha512-crypt support to the Openwall wrapper
%patch56 -p1

%if %{build_selinux}
    # XXX kludge to build nscd with selinux support as it added -nostdinc
    # so /usr/include/selinux is not found
    ln -s %{_includedir}/selinux selinux
%endif

%if %{build_ports}
    mv %{glibcportsdir} ports
%patch57 -p1
%endif

%patch58 -p1

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
    sh %{SOURCE5} $arglist || exit 1
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
%if %{build_multiarch}
    %ifarch x86_64
	rm -f %{buildroot}%{_bindir}/lddlibc4
    %endif
%endif

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

# gconv-modules.cache
touch %{buildroot}%{_libdir}/gconv/gconv-modules.cache
chmod 644 %{buildroot}%{_libdir}/gconv/gconv-modules.cache
%if %{build_multiarch}
    touch %{buildroot}%{_libdir32}/gconv/gconv-modules.cache
    chmod 644 %{buildroot}%{_libdir32}/gconv/gconv-modules.cache
%endif

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

# Documentation
install -m 755 -d %{buildroot}%{_docdir}/glibc
%if %{with doc}
    make -C build-%{_target_cpu}-linux html
    cp -fpar manual/libc %{buildroot}%{_docdir}/glibc/html
%endif
%if %{with pdf}
    make -C build-%{_target_cpu}-linux pdf
    install -m644 -D manual/libc.pdf %{buildroot}%{_docdir}/glibc/libc.pdf
%endif
install -m 644 COPYING COPYING.LIB README NEWS INSTALL FAQ BUGS		\
    NOTES PROJECTS CONFORMANCE README.libm hesiod/README.hesiod		\
    ChangeLog* crypt/README.ufc-crypt nis/nss posix/gai.conf		\
    %{buildroot}%{_docdir}/glibc
xz -0 --text %{buildroot}%{_docdir}/glibc/ChangeLog*
install -m 644 timezone/README %{buildroot}%{_docdir}/glibc/README.timezone
install -m 755 -d %{buildroot}%{_docdir}/glibc/crypt_blowfish
install -m 644 crypt_blowfish-%{crypt_bf_ver}/{README,LINKS,PERFORMANCE} \
    %{buildroot}%{_docdir}/glibc/crypt_blowfish

# Localization
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
export EXCLUDE_FROM_FULL_STRIP="ld-%{version}.so libpthread libc-%{version}.so libm-%{version}.so"
