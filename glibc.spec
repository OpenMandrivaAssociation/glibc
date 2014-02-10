%define svn 0
%if 0%{svn}
%define glibcsrcdir	%{name}-%{version}-%{svn}
%else
%define glibcsrcdir	%{name}-%{version}
%endif

%define	checklist	%{_builddir}/%{glibcsrcdir}/Check.list

# crypt blowfish support
%define crypt_bf_ver	1.2

%define _slibdir	/%{_lib}
%define _slibdir32	/lib
%define _libdir32	%{_prefix}/lib

%define	major		6
%define	libc		%mklibname c %{major}
%define	devname		%mklibname -d c
%define	statname	%mklibname -d -s c
%define	multilibc	libc%{major}

%define	_disable_ld_no_undefined	1
%undefine _fortify_cflags

%ifarch %{arm}
%define _gnu		-gnueabi
%endif

# Define Xen arches to build with -mno-tls-direct-seg-refs
%define xenarches	%{ix86}

# Define to build nscd with selinux support
%bcond_with selinux

# Allow make check to fail only when running kernels where we know
# tests must pass (no missing features or bugs in the kernel)
%define check_min_kver 2.6.21

# Define to build a biarch package
%define build_multiarch	0
%ifarch x86_64
%define build_multiarch	1
%endif

%bcond_without nscd
%bcond_without i18ndata
%bcond_with timezone
%bcond_without nsscrypt

%ifarch %{ix86} x86_64
%bcond_without systap
%else
%bcond_with systap
%endif

# build documentation by default
%bcond_without		doc
%bcond_with		pdf
# enable utils by default
%bcond_without		utils

#-----------------------------------------------------------------------
Summary:	The GNU libc libraries
Name:		glibc
Epoch:		6
Version:	2.19
%if 0%{svn}
Release:	0.%{svn}.1
# Packaged from svn repository at svn://svn.eglibc.org/
Source0:	e%{name}-%{version}-%{svn}.tar.xz
%else
Release:	1
Source0:	http://ftp.gnu.org/gnu/glibc/%{glibcsrcdir}.tar.xz
%endif
License:	LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
Group:		System/Libraries
Url:		http://www.eglibc.org/

%if ! 0%{svn}
Source1:	http://ftp.gnu.org/gnu/glibc/%{glibcsrcdir}.tar.xz.sig
%endif

# From Fedora
Source2:	glibc_post_upgrade.c
Source3:	glibc-manpages.tar.bz2
Source5:	glibc-check.sh
Source10:	libc-lock.h

# Blowfish support
Source50:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz
Source51:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz.sign
Source52:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.c
Source53:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.h

Source100:	%{name}.rpmlintrc

#-----------------------------------------------------------------------
# fedora patches
#
# Patches that are highly unlikely to ever be accepated upstream.
#

# Configuration twiddle, not sure there's a good case to get upstream to
# change this.
Patch0: 	glibc-fedora-nscd.patch

# Build info files in the source tree, then move to the build
# tree so that they're identical for multilib builds
Patch4:		glibc-rh825061.patch

# Horrible hack, never to be upstreamed.  Can go away once the world
# has been rebuilt to use the new ld.so path.
Patch5:		glibc-arm-hardfloat-3.patch

# Needs to be sent upstream
Patch6:		glibc-rh697421.patch

# Needs to be sent upstream
Patch10:	glibc-rh841318.patch

# All these were from the glibc-fedora.patch mega-patch and need another
# round of reviewing.  Ideally they'll either be submitted upstream or
# dropped.

Patch11:	glibc-fedora-uname-getrlimit.patch
Patch12:	glibc-fedora-__libc_multiple_libcs.patch
Patch14:	glibc-fedora-elf-ORIGIN.patch
Patch15:	glibc-fedora-elf-init-hidden_undef.patch
Patch16:	glibc-fedora-elf-rh737223.patch
Patch18:	eglibc-fedora-test-debug-gnuc-hack.patch
Patch20:	glibc-fedora-getrlimit-PLT.patch
Patch21:	glibc-fedora-i386-tls-direct-seg-refs.patch
Patch22:	eglibc-fedora-pt_chown.patch
Patch23:	glibc-fedora-include-bits-ldbl.patch
Patch24:	glibc-fedora-ldd.patch
Patch25:	glibc-fedora-linux-tcsetattr.patch
Patch26:	eglibc-fedora-locale-euro.patch
Patch27:	eglibc-fedora-localedata-locales-fixes.patch
# We disagree with
#		glibc-fedora-streams-rh436349.patch
# Therefore we don't package/apply it.
Patch29:	glibc-fedora-localedata-rh61908.patch
Patch30:	glibc-fedora-localedef.patch
Patch31:	glibc-fedora-locarchive.patch
Patch32:	glibc-fedora-manual-dircategory.patch
Patch33:	glibc-fedora-nis-rh188246.patch
Patch34:	glibc-fedora-nptl-linklibc.patch
Patch35:	glibc-fedora-ppc-unwind.patch
Patch37:	eglibc-fedora-strict-aliasing.patch

#
# Patches from upstream
#

#
# Patches submitted, but not yet approved upstream.
# Each should be associated with a BZ.
# Obviously we're not there right now, but that's the goal
#

Patch38:	glibc-rh757881.patch
Patch40:	glibc-rh741105.patch
# Upstream BZ 13818
Patch49:	glibc-rh800224.patch
# Upstream BZ 14247
Patch50:	glibc-rh827510.patch
# Upstream BZ 14185
Patch54:	glibc-rh819430.patch
Patch55:	glibc-rh911307.patch
Patch51:	glibc-rh952799.patch

#-----------------------------------------------------------------------
# mandriva patches
Patch56:	eglibc-mandriva-localedef-archive-follow-symlinks.patch
Patch57:	eglibc-mandriva-fix-dns-with-broken-routers.patch
Patch58:	eglibc-mandriva-nss-upgrade.patch
Patch59:	eglibc-mandriva-share-locale.patch
Patch60:	eglibc-mandriva-nsswitch.conf.patch
Patch61:	eglibc-mandriva-xterm-xvt.patch
Patch62:	eglibc-mandriva-nscd-enable.patch
Patch63:	eglibc-mandriva-nscd-no-host-cache.patch
Patch64:	eglibc-mandriva-i386-hwcapinfo.patch
Patch65:	eglibc-mandriva-nscd-init-should-start.patch
Patch66:	eglibc-mandriva-timezone.patch
Patch67:	eglibc-mandriva-biarch-cpp-defines.patch
Patch68:	eglibc-mandriva-ENOTTY-fr-translation.patch
Patch69:	eglibc-mandriva-biarch-utils.patch
Patch70:	eglibc-mandriva-multiarch.patch
Patch71:	eglibc-mandriva-i586-hptiming.patch
Patch72:	eglibc-mandriva-i586-if-no-cmov.patch
Patch73:	eglibc-mandriva-pt_BR-i18nfixes.patch
Patch74:	eglibc-mandriva-testsuite-ldbl-bits.patch
Patch75:	eglibc-mandriva-testsuite-rt-notparallel.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=638477#c275
# https://bugzilla.redhat.com/show_bug.cgi?id=696096
# https://bugzilla.redhat.com/attachment.cgi?id=491198
Patch77:	eglibc-mandriva-fix-for-new-memcpy-behavior.patch
Patch79:	eglibc-mandriva-no-leaf-attribute.patch
Patch80:	eglibc-mandriva-string-format-fixes.patch
Patch81:	eglibc-mandriva-mdv-avx-owl-crypt.patch
Patch82:	eglibc-mandriva-mdv-owl-crypt_freesec.patch
Patch83:	eglibc-mandriva-avx-relocate_fcrypt.patch
Patch84:	eglibc-mandriva-avx-increase_BF_FRAME.patch
Patch85:	eglibc-mandriva-mdv-wrapper_handle_sha.patch
# Reverts a part of eglibc-fedora-uname-getrlimit.patch that breaks the build
Patch86:	nptl-getrlimit-compile.patch
Patch87:	eglibc-2.17-bo-locale-buildfix.patch
# http://sourceware.org/bugzilla/show_bug.cgi?id=14995
# http://sourceware.org/bugzilla/attachment.cgi?id=6795
Patch88:	glibc-2.17-gold.patch
# Crypt-blowfish patches
Patch100:	crypt_blowfish-arm.patch

BuildRequires:	autoconf2.5
BuildRequires:	gettext
BuildRequires:	kernel-headers
BuildRequires:	patch
BuildRequires:	perl
BuildRequires:	cap-devel
%if %{with selinux}
BuildRequires:	libselinux-devel >= 1.17.10
%endif
BuildRequires:	texinfo
%if %{with pdf}
BuildRequires:	texlive
%endif
%if %{with utils}
BuildRequires:	gd-devel
%endif
%if %{with systap}
BuildRequires:	systemtap-devel
%endif
%if %{with nsscrypt}
BuildRequires:	nss-devel >= 3.15.1-2
%endif
# we'll be the only package requiring this, avoiding any other package
# dependencies on '/bin/sh' or 'bash'
Requires:	bash
Requires:	filesystem
%ifarch %{xenarches}
%rename		%{name}-xen
%endif
# The dynamic linker supports DT_GNU_HASH
Provides:	rtld(GNU_HASH)
Provides:	glibc-crypt_blowfish = %{crypt_bf_ver}
Provides:	eglibc-crypt_blowfish = %{crypt_bf_ver}
Provides:	should-restart = system
Obsoletes:	glibc-profile
# Old prelink versions breaks the system with glibc 2.11
Conflicts:	prelink < 1:0.4.2-1.20091104.1mdv2010.1
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

%files -f libc.lang
%if %{with timezone}
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
%ifarch armv7l
%{_slibdir}/ld-linux.so.3
%endif
%ifarch armv7hl armv6j
%{_slibdir}/ld-linux-armhf.so.3
%endif
%ifarch aarch64
%{_slibdir}/ld-linux-aarch64.so.1
%{_slibdir32}/ld-linux-aarch64.so.1
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
# %attr(4755,root,root) %{_prefix}/libexec/pt_chown
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
Provides:	eglibc-crypt_blowfish-devel = %{crypt_bf_ver}
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
%{_libdir}/libc_nonshared.a
%{_libdir}/libg.a
%{_libdir}/libieee.a
%{_libdir}/libmcheck.a
%{_libdir}/libpthread_nonshared.a
%{_libdir}/librpcsvc.a
%if %{build_multiarch}
%{_libdir32}/*.o
%{_libdir32}/*.so
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
%if %{with nscd}
#-----------------------------------------------------------------------
%package -n	nscd
Summary:	A Name Service Caching Daemon (nscd)
Group:		System/Servers
Conflicts:	kernel < 2.2.0
Requires(post):	systemd
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
# with nscd
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
%if %{with i18ndata}
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
# with i18ndata
%endif

########################################################################
%if %{with timezone}
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
# with timezone
%endif

########################################################################
%prep
%if 0%{svn}
%setup -q -n e%{name}-%{version}-%{svn}
%else
%setup -q
%endif

tar xf %SOURCE3
tar xf %SOURCE50

%patch00 -p1
%patch04 -p1
%patch05 -p1
%patch06 -p1
%patch10 -p1 -b .rh841318~
%patch11 -p1
%patch12 -p1 -b .multiple~
%patch14 -p1 -b .elfORIGIN~
%patch15 -p1
%patch16 -p1 -b .rh737223~
%patch18 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1 -b .curr~
%patch27 -p1
%patch29 -p1 -b .locales~
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch37 -p1 -b .aliasing~
%patch40 -p1
%patch49 -p1 -b .rh800224~
%patch50 -p1
%patch54 -p1
%patch55 -p1
%patch51 -p1
%patch56 -p1
%patch57 -p1
%patch58 -p1 -b .nssUpgrade~
%patch59 -p1
%patch60 -p1
%patch61 -p1
%patch62 -p1
%patch63 -p1
%patch64 -p1 -b .hwcap~
%patch65 -p1
%patch66 -p1
%patch67 -p1
%patch68 -p1
%patch69 -p1
%patch70 -p1 -b .multiarch~
%patch71 -p1 -b .hpt~
%patch72 -p1
%patch73 -p1
%patch74 -p1 -b .ldbl~
%patch75 -p1 -b .tsp~
%patch79 -p1
%patch80 -p1

# copy freesec source
cp %{SOURCE52} %{SOURCE53} crypt/
echo "Applying crypt_blowfish patch:"
%patch81 -p1 -b .owlCrypt~
mv crypt/crypt.h crypt/gnu-crypt.h
chmod 0644 crypt_blowfish-%{crypt_bf_ver}/*.[chS]
cp -a crypt_blowfish-%{crypt_bf_ver}/*.[chS] crypt/

## FreeSec support for extended/new-style/BSDI hashes in crypt(3)
%patch82 -p1 -b .freesec~
%patch83 -p1 -b .relocateFcrypt~
%patch84 -p0
# add sha256-crypt and sha512-crypt support to the Openwall wrapper
%patch85 -p1

%patch86 -p1 -b .compile~

%patch87 -p1 -b .boLocale~

%patch88 -p1 -b .gold~

%patch100 -p1 -b .blowfish_nonx86~

%if %{with selinux}
    # XXX kludge to build nscd with selinux support as it added -nostdinc
    # so /usr/include/selinux is not found
    ln -s %{_includedir}/selinux selinux
%endif

find . -type f -size 0 -o -name "*.orig" -exec rm -f {} \;

# Remove patch backups from files we ship in glibc packages
rm -f ChangeLog.[^0-9]*
rm -f localedata/locales/{???_??,??_??}.*
rm -f localedata/locales/[a-z_]*.*

# Regenerate autoconf files, some of our patches touch them
# Remove the autoconf 2.68 hardcode...
sed -i -e "s,2.68,`autoconf --version |head -n1 |cut -d' ' -f4`," aclocal.m4
# fix nss headers location
sed -i -e 's@<hasht.h>@<nss/hasht.h>@g' -e 's@<nsslowhash.h>@<nss/nsslowhash.h>@g' configure*

aclocal
autoconf

#-----------------------------------------------------------------------
%build
# ...
[ -d ports ] || ln -s ../ports .
mkdir bin
ln -sf %{_bindir}/ld.bfd bin/ld
export PATH=$PWD/bin:$PATH

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
    armv6*)
      BuildFlags="-march=armv6"
      BuildCompFlags="-march=armv6"
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
%if %{with nsscrypt} || %{with systap}
   if [[ "$BuildAltArch" = "no" ]]; then
%if %{with nsscrypt}
   ExtraFlags="$ExtraFlags --enable-nss-crypt"
%endif
%if %{with systap}
   ExtraFlags="$ExtraFlags --enable-systemtap"
%endif
   fi
%endif

  # NPTL+TLS are now the default
  Pthreads="nptl"

  # Add-ons
  AddOns="$Pthreads,ports,libidn"

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
    --localedir=%{_localedir} \
    --enable-add-ons=$AddOns \
    --disable-profile \
    --enable-static \
%if %{with selinux}
    --with-selinux \
%else
    --without-selinux \
%endif
    --enable-bind-now \
    $ExtraFlags \
    $MultiArchFlags \
    --enable-kernel=%{enablekernel} \
    --with-headers=%{_includedir} ${1+"$@"}
    # (tpg) now only errors got logged
  %make -r -s
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
gcc -static -Lbuild-%{_target_cpu}-linux %{optflags} -Os %{SOURCE2} -o build-%{_target_cpu}-linux/glibc_post_upgrade \
  '-DLIBTLS="/%{_lib}/tls/"' \
  '-DGCONV_MODULES_DIR="%{_libdir}/gconv"' \
  '-DLD_SO_CONF="/etc/ld.so.conf"' \
  '-DICONVCONFIG="%{_sbindir}/iconvconfig"'

#-----------------------------------------------------------------------
%check
# ...
export PATH=$PWD/bin:$PATH

export TMPDIR=/tmp
export TIMEOUTFACTOR=16
while read arglist; do
    sh %{SOURCE5} $arglist || exit 1
done < %{checklist}

#-----------------------------------------------------------------------
%install
# ...
export PATH=$PWD/bin:$PATH

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
install -m644 %{SOURCE10} -D %{buildroot}%{_includedir}/bits/libc-lock.h

# Compatibility hack: this locale has vanished from glibc, but some other
# programs are still using it. Normally we would handle it in the %pre
# section but with glibc that is simply not an option
mkdir -p %{buildroot}%{_localedir}/ru_RU/LC_MESSAGES

# Remove the files we don't want to distribute
rm -f %{buildroot}%{_libdir}/libNoVersion*
rm -f %{buildroot}%{_slibdir}/libNoVersion*


# (tpg) workaround for aarch64 ?
%ifarch aarch64
ls -sf %{_slibdir}/ld-linux-aarch64.so.1 %{buildroot}%{_slibdir32}/ld-linux-aarch64.so.1
%endif

install -m 644 mandriva/nsswitch.conf %{buildroot}%{_sysconfdir}/nsswitch.conf

# This is for ncsd - in glibc 2.2
%if %{with nscd}
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

%if %{with i18ndata}
    install -m644 localedata/SUPPORTED %{buildroot}%{_datadir}/i18n/
%endif

rm -rf %{buildroot}%{_includedir}/netatalk/

# /etc/localtime - we're proud of our timezone #Well we(mdk) may put Paris
%if %{with timezone}
    rm -f %{buildroot}%{_sysconfdir}/localtime
    cp -f %{buildroot}%{_datadir}/zoneinfo/US/Eastern %{buildroot}%{_sysconfdir}/localtime
    #ln -sf ..%{_datadir}/zoneinfo/US/Eastern %{buildroot}%{_sysconfdir}/localtime
%endif

# Documentation
install -m 755 -d %{buildroot}%{_docdir}/glibc
    pushd build-%{_target_cpu}-linux html
%if %{with doc}
	make html
	cp -fpar manual/libc %{buildroot}%{_docdir}/glibc/html
%endif
%if %{with pdf}
	make pdf
	install -m644 -D manual/libc.pdf %{buildroot}%{_docdir}/glibc/libc.pdf
%endif
    popd
install -m 644 COPYING COPYING.LIB README NEWS INSTALL BUGS		\
    PROJECTS CONFORMANCE hesiod/README.hesiod				\
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

rm %{buildroot}%{_bindir}/rpcgen %{buildroot}%{_mandir}/man1/rpcgen.1*

# XXX: verify
find %{buildroot}%{_localedir} -type f -name LC_\* -o -name SYS_LC_\* |xargs rm -f

%if !%{with nscd}
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

%if !%{with timezone}
    rm -f  %{buildroot}%{_sysconfdir}/localtime
    rm -f  %{buildroot}%{_sbindir}/zdump
    rm -f  %{buildroot}%{_sbindir}/zic
    rm -f  %{buildroot}%{_mandir}/man1/zdump.1*
    rm -rf %{buildroot}%{_datadir}/zoneinfo
%endif

%if !%{with i18ndata}
    rm -rf %{buildroot}%{_datadir}/i18n
%endif

# This will make the '-g' argument to be passed to eu-strip for these libraries, so that
# some info is kept that's required to make valgrind work without depending on glibc-debug
# package to be installed.
export EXCLUDE_FROM_FULL_STRIP="ld-%{version}.so libpthread libc-%{version}.so libm-%{version}.so"
