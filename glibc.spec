# RH 2.2.4-20, SuSE 2.3.1-32
%define name		%{cross_prefix}glibc

# <version>-<release> tags for glibc main package
%define glibccvsversion	2.4.90
%define glibcversion	2.6.1
%define _glibcrelease	4
%if %{mdkversion} >= 200700
# XXX core_mkrel
%define glibcrelease	%mkrel %{_glibcrelease}
%else
%define glibcrelease	%{_glibcrelease}mdk
%endif
%define glibcepoch	6
# <version>-<release> tags from kernel package where headers were
# actually extracted from
%define kheaders_ver	2.6.22
%define kheaders_rel	3mdv

# CVS snapshots of glibc
%define RELEASE		1
%if %{RELEASE}
%define source_package	glibc-%{glibcversion}
%define source_dir	glibc-%{glibcversion}
%else
%define snapshot	20060510
%define source_package	glibc-%{glibccvsversion}-%{snapshot}
%define source_dir	glibc-%{glibccvsversion}
%endif

# Define "cross" to an architecture to which glibc is to be
# cross-compiled
%define build_cross		0
%{expand: %{?cross:		%%global build_cross 1}}

%if %{build_cross}
%define target_cpu	%{cross}
%define cross_prefix	cross-%{target_cpu}-
%define _prefix		/usr/%{target_cpu}-linux
%define _lib		lib
%define _slibdir	%{_prefix}/%{_lib}
%define _slibdir32	%{_prefix}/lib
%else
%define target_cpu	%{_target_cpu}
%define cross_prefix	%{nil}
%define _slibdir	/%{_lib}
%define _slibdir32	/lib
%endif

# Define target (base) architecture
%define arch		%(echo %{target_cpu}|sed -e "s/\\(i.86\\|athlon\\)/i386/" -e "s/amd64/x86_64/" -e "s/\\(sun4.*\\|sparcv[89]\\)/sparc/")
%define isarch()	%(case " %* " in (*" %{arch} "*) echo 1;; (*) echo 0;; esac)

# Define Xen arches to build with -mno-tls-direct-direct-seg-refs
%if %{mdkversion} >= 200600
%define xenarches	%{ix86} x86_64
%else
%define xenarches	noarch
%endif

# Define to build nscd with selinux support
%define build_selinux	0

# Flag for build_pdf_doc:
# 1	build glibc with PDF documentation
# 0	don't build PDF glibc documentation (e.g. for bootstrap build)
%define build_pdf_doc	1

# Enable checking by default for arches where we know tests all pass
%define build_check	1

# Allow make check to fail only when running kernels where we know
# tests must pass (no missing features or bugs in the kernel)
%define check_min_kver 2.6.21

# Define to build a biarch package
%define build_biarch	0
%if %isarch sparc64 x86_64 ppc64
%define build_biarch	1
%endif

# Define to build glibc-debug package
%define build_debug	1
%if %{mdkversion} >= 920
%define _enable_debug_packages 1
%endif
%if "%{_enable_debug_packages}" == "1"
%define build_debug	0
%endif

# Define to bootstrap new glibc
%define build_bootstrap	0
%{expand: %{!?build_cross_bootstrap: %global build_cross_bootstrap 0}}

%define build_profile	1
%define build_nscd	1
%define build_doc	1
%define build_utils	1
%define build_i18ndata	1
%define build_timezone	0

# Disable a few defaults when cross-compiling a glibc
%if %{build_cross}
%define build_doc	0
%define build_pdf_doc	0
%define build_biarch	0
%define build_check	0
%define build_debug	0
%define build_nscd	0
%define build_profile	0
%define build_utils	0
%define build_i18ndata	0
%define build_timezone	0
%endif

# Allow --with[out] <feature> at rpm command line build
%{expand: %{?_without_PDF:	%%global build_pdf_doc 0}}
%{expand: %{?_without_CHECK:	%%global build_check 0}}
%{expand: %{?_without_UTILS:	%%global build_utils 0}}
%{expand: %{?_without_BOOTSTRAP:%%global build_bootstrap 0}}
%{expand: %{?_with_PDF:		%%global build_pdf_doc 1}}
%{expand: %{?_with_CHECK:	%%global build_check 1}}
%{expand: %{?_with_UTILS:	%%global build_utils 1}}
%{expand: %{?_with_BOOTSTRAP:	%%global build_bootstrap 1}}

Summary:	The GNU libc libraries
Name:		%{name}
Version:	%{glibcversion}
Release:	%{glibcrelease}
Epoch:		%{glibcepoch}
License:	LGPL
Group:		System/Libraries
Url:		http://www.gnu.org/software/libc/

# FSF source
Source0:	http://ftp.gnu.org/gnu/glibc/%{source_package}.tar.bz2
Source1:	http://ftp.gnu.org/gnu/glibc/%{source_package}.tar.bz2.sig

# Red Hat tarball
Source2:	glibc-redhat.tar.bz2
Source3:	glibc-manpages.tar.bz2
Source4:	glibc-find-requires.sh
Source5:	glibc-check.sh

# If using official FSF release we must get also libidn
%if %{RELEASE}
Source6:	http://ftp.gnu.org/gnu/glibc/glibc-libidn-%{glibcversion}.tar.bz2
Source7:	http://ftp.gnu.org/gnu/glibc/glibc-libidn-%{glibcversion}.tar.bz2.sig
%endif

# kernel-headers tarball generated from mandriva kernel in svn with:
# make INSTALL_HDR_PATH=<path> headers_install_all
Source10:	kernel-headers-%{kheaders_ver}.%{kheaders_rel}.tar.bz2
Source11:	make_versionh.sh
Source12:	create_asm_headers.sh

# Warning message about glibc updates
Source13:	README.upgrade.urpmi

# wrapper to avoid rpm circular dependencies
Source14:	glibc-post-wrapper.c

# <http://penguinppc.org/dev/glibc/glibc-powerpc-cpu-addon.html>
# NOTE: this check is weak. The rationale is: Cell PPU optimized by
# default for MDV 2007.0, power5 et al. on Corporate side
%define powerpc_cpu_list noarch
%if "%{?distsuffix:%{distsuffix}}" == "mlcs4"
%define powerpc_cpu_list power5
%endif
Source15:	glibc-powerpc-cpu-addon-v0.03.tar.bz2

Buildroot:	%{_tmppath}/glibc-%{PACKAGE_VERSION}-root
%if %{build_cross}
Autoreq:	false
Autoprov:	false
%else
Obsoletes:	zoneinfo, libc-static, libc-devel, libc-profile, libc-headers,
Obsoletes: 	linuxthreads, gencat, locale, glibc-localedata
Provides:	glibc-localedata
%if %isarch %{xenarches}
Obsoletes:	%{name}-xen
Provides:	%{name}-xen
%endif
# The dynamic linker supports DT_GNU_HASH
Provides: rtld(GNU_HASH)
Autoreq:	false
%endif
BuildRequires:	patch, gettext, perl
%if %{build_selinux}
BuildRequires:	libselinux-devel >= 1.17.10
%endif
# we need suitable linker for -Wl,--hash-style=both
%define binutils_version 2.16.91.0.7-%{mkrel 6}
BuildRequires:	%{cross_prefix}binutils >= %{binutils_version}
# we need the static ash
%if %{mdkversion} >= 200600
%define ash_bin		/bin/ash
Requires(pre):		ash >= 0.3.8-7mdk
Requires(post):		ash >= 0.3.8-7mdk
%else
%define ash_bin		/bin/ash.static
Requires(pre):		ash-static
Requires(post):		ash-static
%endif
# we need an rpm with correct db4 lib
Conflicts:		rpm < 4.2.2
# we need an ldconfig with TLS support
%if %{build_cross}
BuildRequires:	%{cross_prefix}gcc >= 3.2.2-4mdk
%endif
%ifarch %{ix86} alpha
BuildRequires:	%{cross_prefix}gcc >= 2.96-0.50mdk
%endif
%ifarch ia64
BuildRequires:	%{cross_prefix}gcc >= 3.2.3-1mdk
%endif
%ifarch x86_64
BuildRequires:	%{cross_prefix}gcc >= 3.1.1-0.5mdk
%endif
%if %{mdkversion} >= 200600
BuildRequires:	%{cross_prefix}gcc >= 4.0.1-2mdk
%endif
%if !%{build_cross}
%ifarch alpha
Provides:	ld.so.2
%endif
%ifarch ppc
Provides:	ld.so.1
%endif
%ifarch sparc
Obsoletes:	libc
%endif
%endif

Conflicts:	rpm <= 4.0-0.65
Conflicts:	%{name}-devel < 2.2.3
# We need initscripts recent enough to not restart service dm
Conflicts:	initscripts < 6.91-18mdk
# Ease Conectiva upgrades
Conflicts:	%{name}-base <= 2.3.4

BuildRequires:	texinfo
%if %{build_pdf_doc}
BuildRequires:	tetex, tetex-latex
%endif
%if %{build_utils}
BuildRequires:	gd-devel
%endif
BuildRequires:	autoconf2.5

Patch1:		glibc-2.2.2-fhs.patch
Patch2:		glibc-2.3.4-ldd-non-exec.patch
Patch3:		glibc-2.1.95-string2-pointer-arith.patch
Patch4:		glibc-2.2-nss-upgrade.patch
Patch5:		glibc-2.2.5-ldconfig-exit-during-install.patch
Patch6:		glibc-2.2.5-share-locale.patch
Patch7:		glibc-2.3.6-nsswitch.conf.patch
Patch8:		glibc-2.6-new-charsets.patch
Patch9:		glibc-2.2.4-xterm-xvt.patch
Patch10:	glibc-2.2.4-hack-includes.patch
Patch11:	glibc-2.4.90-compat-EUR-currencies.patch
Patch12:	glibc-2.3.6-ppc-build-lddlibc4.patch
Patch13:	glibc-2.3.3-nscd-enable.patch
Patch14:	glibc-2.3.2-config-amd64-alias.patch
Patch15:	glibc-2.2.5-nscd-no-host-cache.patch
Patch16:	glibc-2.3.1-quota.patch
Patch17:	glibc-2.4.90-i386-hwcapinfo.patch
Patch18:	glibc-2.4.90-x86_64-new-libm.patch
Patch19:	glibc-2.4.90-amd64-fix-ceil.patch
Patch20:	glibc-2.3.4-nscd-fixes.patch
Patch21:	glibc-2.6-nscd_HUP.patch
Patch22:	glibc-2.3.2-tcsetattr-kernel-bug-workaround.patch
Patch23:	glibc-2.3.4-timezone.patch
Patch24:	glibc-2.4.90-biarch-cpp-defines.patch
Patch25:	glibc-2.3.4-run-test-program-prefix.patch
Patch26:	glibc-2.6-nice_fix.patch
Patch27:	glibc-2.3.6-ENOTTY-fr-translation.patch
Patch28:	glibc-2.4.90-gcc4-fortify.patch
Patch29:	glibc-2.3.5-biarch-utils.patch
Patch30:	glibc-2.6-multiarch.patch
Patch31:	glibc-2.4.90-i586-hptiming.patch
Patch32:	glibc-2.3.4-i586-if-no-cmov.patch
Patch33:	glibc-2.3.6-pt_BR-i18nfixes.patch
Patch34:	glibc-2.4.90-testsuite-ldbl-bits.patch
Patch37:	glibc-2.4.90-powerpc-no-clock_gettime-vdso.patch
Patch38:	glibc-2.4.90-testsuite-rt-notparallel.patch
Patch39:	glibc-2.6-texi_buildpdf_fix.patch
Patch40:	glibc-2.6-revert-pl_PL-LC_TIME-change.patch

# Upstream patch to speed up ldconfig (diff from suse)
Patch49:	glibc-2.5-ldconfig-old-cache.diff

# Additional patches from 2.6-branch/trunk
Patch50:	glibc-cvs-nscd_dont_cache_ttl0.patch
Patch51:	glibc-cvs-utimensat.patch
Patch52:	glibc-bz4599.patch
Patch53:	glibc-bz4125.patch
Patch54:	glibc-cvs-gcc_init_fini.patch
Patch55:	glibc-bz4647.patch
Patch56:	glibc-bz4773.patch
Patch57:	glibc-_nl_explode_name_segfault_fix.patch
Patch58:	glibc-bz4776.patch
Patch59:	glibc-bz4775.patch
Patch60:	glibc-cvs-popen_bug_fix.patch
Patch61:	glibc-bz4792.patch
Patch62:	glibc-cvs-_cs_posix_v6_width_restricted_envs.patch
Patch63:	glibc-bz4813.patch
Patch64:	glibc-bz4812.patch
Patch65:	glibc-bz4772.patch
Patch66:	glibc-cvs-warning_patrol_fixes.patch
Patch67:	glibc-cvs-getconf_add_missing_lvl4_cache_linesize.patch
Patch68:	glibc-cvs-libc_texinfo_update.patch
Patch69:	glibc-cvs-ix86_rwlock_fixes.patch
Patch70:	glibc-cvs-gettext_memleak_fixes.patch
Patch71:	glibc-cvs-strtod_handle_minuszero.patch
Patch72:	glibc-cvs-ar_SA-dz_BT-LC_TIME-fixes.patch
Patch73:	glibc-cvs-po_updates.patch
Patch74:	glibc-cvs-rh250492.patch

# Patches for kernel-headers
Patch100:	kernel-headers-gnu-extensions.patch
Patch101:	kernel-headers-dvb-video-fix-includes.patch

# Determine minium kernel versions
%define		enablekernel 2.6.9
%if %isarch ppc ppc64
# waitid syscall is available in 2.6.12+ there
%define		enablekernel 2.6.12
%endif
Conflicts:	kernel < %{enablekernel}

# People changed location of rpm scripts...
%if %{mdkversion} >= 200600
%define rpmscripts	/usr/lib/rpm/mandriva
%else
%define rpmscripts	/usr/lib/rpm
%endif

# Don't try to explicitly provide GLIBC_PRIVATE versioned libraries
%define __find_provides	%{_builddir}/%{source_dir}/find_provides.sh
%define __find_requires %{_builddir}/%{source_dir}/find_requires.sh

%if !%{build_cross}
Obsoletes:	ld.so
Provides:	ld.so
%endif

Obsoletes:	ldconfig
Provides:	ldconfig = %{glibcepoch}:%{glibcversion}-%{glibcrelease} /sbin/ldconfig

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.  The glibc package also contains
national language (locale) support.

This package now also provides ldconfig which was package seperately in
the past. Ldconfig is a basic system program which determines run-time
link bindings between ld.so and shared libraries. Ldconfig scans a running
system and sets up the symbolic links that are used to load shared
libraries properly. It also creates a cache (/etc/ld.so.cache) which
speeds the loading of programs which use shared libraries.

%package devel
Summary:	Header and object files for development using standard C libraries
Group:		Development/C
Conflicts:	texinfo < 3.11
Requires(post):	  info-install
Requires(preun):  info-install
Requires(post):   coreutils
Requires(postun): coreutils, awk
Obsoletes:	libc-debug, libc-headers, libc-devel, linuxthreads-devel, nptl-devel
%if !%{build_debug}
Obsoletes:	%{name}-debug < 6:2.3.2-15mdk
%endif
Requires:	%{name} = %{glibcepoch}:%{glibcversion}-%{glibcrelease}
%if !%{build_cross}
Obsoletes:	kernel-headers
Provides:	kernel-headers = 1:%{kheaders_ver}
%endif
%if !%isarch ppc
Conflicts:	%{cross_prefix}gcc < 2.96-0.50mdk
%endif
%if %{mdkversion} >= 200600
# needs a gcc4 fortify capable compiler
Conflicts:	gcc4.0 < 4.0.1-2mdk
%endif
%if %{build_cross}
Autoreq:	false
Autoprov:	false
%else
Autoreq:	true
%endif

%description devel
The glibc-devel package contains the header and object files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard header and object files available in order to create the
executables.

This package also includes the C header files for the Linux kernel.
The header files define structures and constants that are needed for
building most standard programs. The header files are also needed for
rebuilding the kernel.

Install glibc-devel if you are going to develop programs which will
use the standard C libraries.

%package static-devel
Summary:	Static libraries for GNU C library
Group:		Development/C
Requires:	%{name}-devel = %{glibcepoch}:%{glibcversion}-%{glibcrelease}

%description static-devel
The glibc-static-devel package contains the static libraries necessary
for developing programs which use the standard C libraries. Install
glibc-static-devel if you need to statically link your program or
library.

%package profile
Summary:	The GNU libc libraries, including support for gprof profiling
Group:		Development/C
Obsoletes:	libc-profile
Provides:	libc-profile = %{glibcversion}-%{glibcrelease}
Autoreq:	true

%description profile
The glibc-profile package includes the GNU libc libraries and support
for profiling using the gprof program.  Profiling is analyzing a
program's functions to see how much CPU time they use and determining
which functions are calling other functions during execution.  To use
gprof to profile a program, your program needs to use the GNU libc
libraries included in glibc-profile (instead of the standard GNU libc
libraries included in the glibc package).

If you are going to use the gprof program to profile a program, you'll
need to install the glibc-profile program.

%package -n nscd
Summary:	A Name Service Caching Daemon (nscd)
Group:		System/Servers
Conflicts:	kernel < 2.2.0
Requires(pre):	  rpm-helper
Requires(preun):  rpm-helper
Requires(post):   rpm-helper
Requires(postun): rpm-helper
Autoreq:	true

%description -n nscd
Nscd caches name service lookups and can dramatically improve
performance with NIS+, and may help with DNS as well. Note that you
can't use nscd with 2.0 kernels because of bugs in the kernel-side
thread support. Unfortunately, nscd happens to hit these bugs
particularly hard.

Install nscd if you need a name service lookup caching daemon, and
you're not using a version 2.0 kernel.

%if %{build_debug}
%package	debug
Summary:	Shared standard C libraries with debugging information
Group:		System/Libraries
Requires:	%{name} = %{glibcepoch}:%{glibcversion}-%{glibcrelease}
Autoreq:	false

%description debug
The glibc-debug package contains shared standard C libraries with
debugging information. You need this only if you want to step into C
library routines during debugging.

To use these libraries, you need to add %{_libdir}/debug to your
LD_LIBRARY_PATH variable prior to starting the debugger.
%endif

%package utils
Summary:	Development utilities from GNU C library
Group:		Development/Other
Requires:	%{name} = %{glibcepoch}:%{glibcversion}-%{glibcrelease}

%description utils
The glibc-utils package contains memusage, a memory usage profiler,
mtrace, a memory leak tracer and xtrace, a function call tracer which
can be helpful during program debugging.

If unsure if you need this, don't install this package.

%package i18ndata
Summary:	Database sources for 'locale'
Group:		System/Libraries

%description i18ndata
This package contains the data needed to build the locale data files
to use the internationalization features of the GNU libc.

%package -n timezone
Summary:	Time zone descriptions
Group:		System/Base
Conflicts:	glibc < 2.2.5-6mdk

%description -n timezone
These are configuration files that describe possible
time zones.

%package doc
Summary:	GNU C library documentation
Group:		Development/Other

%description doc
The glibc-doc package contains documentation for the GNU C library in
info format.

%if %{build_pdf_doc}
%package doc-pdf
Summary:	GNU C library documentation
Group:		Development/Other

%description doc-pdf
The glibc-doc-pdf package contains the printable documentation for the
GNU C library in PDF format.
%endif

%prep
%setup -q -n %{source_dir} -a 10 -a 3 -a 2 -a 15
%if %{RELEASE}
tar -jxf %{_sourcedir}/glibc-libidn-%{glibcversion}.tar.bz2
mv glibc-libidn-%{glibcversion} libidn
%endif

cp %{_sourcedir}/README.upgrade.urpmi .

%patch1 -p1 -b .fhs
%patch2 -p1 -b .ldd-non-exec
%patch3 -p1 -b .string2-pointer-arith
%patch4 -p1 -b .nss-upgrade
%patch5 -p1 -b .ldconfig-exit-during-install
%patch6 -p1 -b .share-locale
%patch7 -p1 -b .nsswitch.conf
%patch8 -p1 -b .new-charsets
%patch9 -p1 -b .xterm-xvt
%patch10 -p1 -b .hack-includes
%patch11 -p1 -b .compat-EUR-currencies
%patch12 -p1 -b .ppc-lddlibc4
%patch13 -p1 -b .nscd-enable
%patch14 -p1 -b .config-amd64-alias
%patch15 -p1 -b .nscd-no-host-cache
%patch16 -p1 -b .quota
%patch17 -p1 -b .i386-hwcapinfo
#patch18 -p0 -b .x86_64-new-libm -E
# remove duplicates (XXX merge into patch18)
#rm -f sysdeps/x86_64/fpu/s_sincos.S
#patch19 -p1 -b .amd64-fix-ceil
%patch20 -p1 -b .nscd-fixes
%patch21 -p1 -b .nscd_HUP
%patch22 -p1 -b .tcsetattr-kernel-bug-workaround
%patch23 -p1 -b .timezone
%patch24 -p1 -b .biarch-cpp-defines
%patch25 -p1 -b .run-test-program-prefix
%patch26 -p1 -b .nice-fix
%patch27 -p1 -b .ENOTTY-fr-translation
%if %{mdkversion} >= 200600
%patch28 -p1 -b .gcc4-fortify
%endif
%patch29 -p1 -b .biarch-utils
%patch30 -p1 -b .multiarch-check
%patch31 -p1 -b .i586-hptiming
%patch32 -p1 -b .i586-if-no-cmov
%patch33 -p1 -b .pt_BR-i18nfixes
%patch34 -p1 -b .testsuite-ldbl-bits
%patch37 -p1 -b .powerpc-no-clock_gettime-vdso
%patch38 -p1 -b .testsuite-rt-notparallel
%patch39 -p1 -b .texi_buildpdf_fix
%patch40 -p1 -b .revert-pl_PL-LC_TIME-change
%patch49 -p1 -b .ldconfig-old-cache

%patch50 -p1 -b .nscd_dont_cache_ttl0
%patch51 -p1 -b .utimensat
%patch52 -p1 -b .bz4599
%patch53 -p1 -b .bz4125
%patch54 -p1 -b .gcc_init_fini
%patch55 -p1 -b .bz4647
%patch56 -p1 -b .bz4773
%patch57 -p1 -b ._nl_explode_name_segfault_fix
%patch58 -p1 -b .bz4776
%patch59 -p1 -b .bz4775
%patch60 -p1 -b .popen_bug_fix
%patch61 -p1 -b .bz4792
%patch62 -p1 -b ._cs_posix_v6_width_restricted_envs
%patch63 -p1 -b .bz4813
%patch64 -p1 -b .bz4812
%patch65 -p1 -b .bz4772
%patch66 -p1 -b .warning_patrol_fixes
%patch67 -p1 -b .getconf_add_missing_lvl4_cache_linesize
%patch68 -p1 -b .libc_texinfo_update
%patch69 -p1 -b .ix86_rwlock_fixes
%patch70 -p1 -b .gettext_memleak_fixes
%patch71 -p1 -b .strtod_handle_minuszero
%patch72 -p1 -b .ar_SA-dz_BT-LC_TIME-fixes
%patch73 -p1 -b .po_updates
%patch74 -p1 -b .rh250492

pushd kernel-headers/
TARGET=%{target_cpu}
%patch100 -p1
%patch101 -p1
%{expand:%(%__cat %{SOURCE11} 2>/dev/null)}
%{expand:%(%__cat %{SOURCE12} 2>/dev/null)}
popd

%if %{build_selinux}
# XXX kludge to build nscd with selinux support as it added -nostdinc
# so /usr/include/selinux is not found
ln -s %{_includedir}/selinux selinux
%endif

find . -type f -size 0 -o -name "*.orig" -exec rm -f {} \;

cat > find_provides.sh << EOF
#!/bin/sh
%{rpmscripts}/find-provides | grep -v GLIBC_PRIVATE
exit 0
EOF
chmod +x find_provides.sh

cat > find_requires.bootstrap.sh << EOF
/bin/sh %{SOURCE4} %{buildroot} %{_target_cpu} | grep -v "\(GLIBC_PRIVATE\|linux-gate\|linux-vdso\)"
exit 0
EOF
chmod +x find_requires.bootstrap.sh

# XXX: use better way later to avoid LD_LIBRARY_PATH issue
cat %{rpmscripts}/find-requires | sed '/.*LD_LIBRARY_PATH.*/d;' > find_requires
chmod +x find_requires
cat > find_requires.noprivate.sh << EOF
%{_builddir}/%{source_dir}/find_requires %{buildroot} %{_target_cpu} | \
	grep -v GLIBC_PRIVATE
exit 0
EOF
chmod +x find_requires.noprivate.sh

# FIXME: fix system rpm find-requires to use the prefix cross version
%if %{build_bootstrap} || "%{_target_cpu}" != "%{target_cpu}"
ln -s find_requires.bootstrap.sh find_requires.sh
%else
ln -s find_requires.noprivate.sh find_requires.sh
%endif

%build
# Prepare test matrix in the next function
CheckList=$PWD/Check.list
rm -f $CheckList
touch $CheckList

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

  # PowerPC CPU add-on
  case $arch in
    cpu-addon,*)
      cpu=` echo "$arch" | sed -n "/.*,\([^,]*\),.*$/s//\1/p"`
      arch=`echo "$arch" | sed -n "/.*,.*,\([^,]*\)$/s//\1/p"`
      ;;
    *)
      cpu=$arch
      ;;
  esac

  # Select optimization flags and compiler to use
  BuildAltArch="no"
  BuildCompFlags=""
  BuildFlags=""
  case $arch in
    i[3456]86 | athlon)
      BuildFlags="-march=$arch -mtune=generic"
      if [[ "`uname -m`" = "x86_64" ]]; then
        BuildAltArch="yes"
        BuildCompFlags="-m32"
      fi
      ;;
    x86_64)
      BuildFlags="-mtune=generic"
      ;;
    ppc)
      if [[ "`uname -m`" = "ppc64" ]]; then
        BuildAltArch="yes"
        BuildCompFlags="-m32"
        # 64-bit processors we support do support power4+ ISA (2.01)
        if [[ "$cpu" != "$arch" ]]; then
          BuildFlags="-mcpu=$cpu"
        else
          BuildFlags="-mcpu=power4 -mtune=cell"
        fi
      fi
      ;;
    ppc64)
      if [[ "$cpu" != "$arch" ]]; then
        BuildFlags="-mcpu=$cpu"
      else
        BuildFlags="-mcpu=power4 -mtune=cell"
      fi
      ;;
    alphaev6)
      BuildFlags="-mcpu=ev6"
      ;;
    sparc)
      BuildFlags="-fcall-used-g6"
      BuildCompFlags="-m32"
      ;;
    sparcv9)
      BuildFlags="-mcpu=ultrasparc -fcall-used-g6"
      BuildCompFlags="-m32"
      ;;
    sparc64)
      BuildFlags="-mcpu=ultrasparc -mvis -fcall-used-g6"
      BuildCompFlags="-m64 -mcpu=ultrasparc"
      ;;
  esac

  # Determine C & C++ compilers
  BuildCC="%{__cc} $BuildCompFlags"
  BuildCXX="%{__cxx} $BuildCompFlags"

  # Are we supposed to cross-compile?
  if [[ "%{target_cpu}" != "%{_target_cpu}" ]]; then
    BuildCC="%{target_cpu}-linux-$BuildCC"
    BuildCXX="%{target_cpu}-linux-$BuildCXX"
    BuildCross="--build=%{_target_platform}"
    export libc_cv_forced_unwind=yes libc_cv_c_cleanup=yes
  fi

  BuildFlags="$BuildFlags -DNDEBUG=1 -O2 -finline-functions -g"
  if $BuildCC -v 2>&1 | grep -q 'gcc version 3.0'; then
    # gcc3.0 had really poor inlining heuristics causing problems in
    # resulting ld.so
    BuildFlags="$BuildFlags -finline-limit=2000"
  fi

  # Do not use direct references against %gs when accessing tls data
  # XXX make it the default in GCC? (for other non glibc specific usage)
  case $arch in
    i[3456]86 | x86_64)
      BuildFlags="$BuildFlags -mno-tls-direct-seg-refs"
      ;;
  esac

  # Disable fortify for glibc builds
  BuildFlags="$BuildFlags -U_FORTIFY_SOURCE"

  # Arch specific compilation flags
  if [[ "$arch" = "ppc64" ]]; then
    BuildFlags="$BuildFlags -fno-inline-functions -mno-minimal-toc"
  fi

  # Extra configure flags
  ExtraFlags=
  if [[ "%{build_profile}" != "0" ]]; then
    ExtraFlags="$ExtraFlags --enable-profile"
  fi

  # NPTL+TLS are now the default
  Pthreads="nptl"
  TlsFlags="--with-tls --with-__thread"

  # Add-ons
  AddOns="$Pthreads,libidn"
  if [[ "$cpu" != "$arch" ]]; then
    AddOns="$AddOns,powerpc-cpu"
    BuildFlags="$BuildFlags -mcpu=$cpu"
    ExtraFlags="$ExtraFlags --with-cpu=$cpu"
  fi

  # Build with selinux support?
%if %{build_selinux}
  SElinuxFlags="--with-selinux"
%else
  SElinuxFlags="--without-selinux"
%endif

  # Kernel headers directory
  KernelHeaders=$PWD/kernel-headers

  # Determine library name
  glibc_cv_cc_64bit_output=no
  if echo ".text" | $BuildCC -c -o test.o -xassembler -; then
    case `/usr/bin/file test.o` in
    *"ELF 64"*)
      glibc_cv_cc_64bit_output=yes
      ;;
    esac
  fi
  rm -f test.o

  # Force a separate and clean object dir
  rm -rf build-$cpu-linux
  mkdir  build-$cpu-linux
  pushd  build-$cpu-linux
  [[ "$BuildAltArch" = "yes" ]] && touch ".alt" || touch ".main"
  CC="$BuildCC" CXX="$BuildCXX" CFLAGS="$BuildFlags" ../configure \
    $arch-mandriva-linux-gnu $BuildCross \
    --prefix=%{_prefix} \
    --libexecdir=%{_prefix}/lib \
    --infodir=%{_infodir} \
    --enable-add-ons=$AddOns --without-cvs \
    $TlsFlags $ExtraFlags $SElinuxFlags \
    --enable-kernel=%{enablekernel} --with-headers=$KernelHeaders ${1+"$@"}
  %make -r PARALLELMFLAGS=-s
  popd

  # All tests are expected to pass on certain platforms, depending also
  # on the version of the kernel running
  case $arch in
  i[3456]86 | athlon | x86_64 | ia64 | ppc | ppc64)
    if [ "`CompareKver %{check_min_kver}`" -lt 0 ]; then
      check_flags=""
    else
      check_flags="-k"
    fi
    ;;
  *)
    check_flags="-k"
    ;;
  esac

  # Generate test matrix
  [[ -d "build-$arch-linux" ]] || {
    echo "ERROR: PrepareGlibcTest: build-$arch-linux does not exist!"
    return 1
  }
  local BuildJobs="-j`getconf _NPROCESSORS_ONLN`"
  echo "$BuildJobs -d build-$arch-linux $check_flags" >> $CheckList

  case $cpu in
  i686|athlon)	base_arch=i586;;
  power*)	base_arch=$arch;;
  *)		base_arch=none;;
  esac

  [[ -d "build-$base_arch-linux" ]] && {
    check_flags="$check_flags -l build-$base_arch-linux/elf/ld.so"
    echo "$BuildJobs -d build-$arch-linux $check_flags" >> $CheckList
  }
  return 0
}

# Build main glibc
BuildGlibc %{target_cpu}

%if %{build_biarch}
%if %isarch sparc64
BuildGlibc sparcv9
%endif
%if %isarch x86_64
BuildGlibc i686
%endif
%if %isarch ppc64
BuildGlibc ppc
%endif
%endif

%if %isarch ppc ppc64
for cpu in %{powerpc_cpu_list}; do
  [[ "$cpu" = "noarch" ]] && continue
  BuildGlibc cpu-addon,$cpu,%{_arch} --disable-profile
done
%endif

# Build i686 libraries if not already building for i686/athlon
case %{target_cpu} in
  i686 | athlon)
    ;;
  i[3-6]86)
    BuildGlibc i686 --disable-profile
    ;;
esac

%if %{build_check}
export TMPDIR=/tmp
export TIMEOUTFACTOR=16
Check="$PWD/glibc-check.sh"
cat %{SOURCE5} > $Check
chmod +x $Check
while read arglist; do
  $Check $arglist || exit 1
done < $CheckList
%endif

%install
rm -rf $RPM_BUILD_ROOT

# force use of _NPROCESSORS_ONLN jobs since RPM_BUILD_NCPUS could be
# greater for icecream
BuildJobs="-j`getconf _NPROCESSORS_ONLN`"

make install_root=$RPM_BUILD_ROOT install -C build-%{target_cpu}-linux
%if %{build_i18ndata}
(cd build-%{target_cpu}-linux;
  make $BuildJobs -C ../localedata objdir=`pwd` \
	install_root=$RPM_BUILD_ROOT \
	install-locales
)
%endif
sh manpages/Script.sh

# Empty filelist for non i686/athlon targets
> extralibs.filelist

# Install biarch libraries
%if %{build_biarch}
%if %isarch sparc64
ALT_ARCH=sparcv9-linux
%endif
%if %isarch x86_64
ALT_ARCH=i686-linux
%endif
%if %isarch ppc64
ALT_ARCH=ppc-linux
%endif
mkdir -p $RPM_BUILD_ROOT/$ALT_ARCH
make install_root=$RPM_BUILD_ROOT/$ALT_ARCH install -C build-$ALT_ARCH

# Dispatch */lib only
mv $RPM_BUILD_ROOT/$ALT_ARCH/lib $RPM_BUILD_ROOT/
rm -f  $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/pt_chown
mv     $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/getconf/* $RPM_BUILD_ROOT%{_prefix}/lib/getconf/
rmdir  $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/getconf
mv     $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/* $RPM_BUILD_ROOT%{_prefix}/lib/
# We want 32-bit binaries on sparc64
%if %isarch sparc64
mv -f    $RPM_BUILD_ROOT/$ALT_ARCH/sbin/* $RPM_BUILD_ROOT/sbin
mv -f    $RPM_BUILD_ROOT/$ALT_ARCH/%{_bindir}/* $RPM_BUILD_ROOT%{_bindir}
mv -f    $RPM_BUILD_ROOT/$ALT_ARCH/%{_sbindir}/* $RPM_BUILD_ROOT%{_sbindir}
%endif
rm -rf $RPM_BUILD_ROOT/$ALT_ARCH
# XXX Dispatch 32-bit stubs
(sed '/^@/d' include/stubs-prologue.h; LC_ALL=C sort $(find build-$ALT_ARCH -name stubs)) \
> $RPM_BUILD_ROOT%{_includedir}/gnu/stubs-32.h
%endif

# Install extra glibc libraries
function InstallGlibc() {
  local BuildDir="$1"
  local SubDir="$2"
  local LibDir="$3"

  case $BuildDir in
  *)      Pthreads=nptl         ;;
  esac

  [[ -z "$LibDir" ]] && LibDir="%{_slibdir}"

  pushd $BuildDir
  mkdir -p $RPM_BUILD_ROOT$LibDir/$SubDir/
  install -m755 libc.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libc-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libc-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libc.so.*`
  install -m755 math/libm.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libm-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libm-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libm.so.*`
  install -m755 $Pthreads/libpthread.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libpthread-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libpthread-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libpthread.so.*`
  install -m755 ${Pthreads}_db/libthread_db.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libthread_db-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libthread_db-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libthread_db.so.*`
  install -m755 rt/librt.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/librt-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/librt-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/librt.so.*`
  echo "%dir $LibDir/$SubDir" >> ../extralibs.filelist
  find $RPM_BUILD_ROOT$LibDir/$SubDir -maxdepth 1  -type f -o -type l | sed -e "s|$RPM_BUILD_ROOT||" >> ../extralibs.filelist
  popd
}

# Install arch-specific optimized libraries
%if %isarch %{ix86}
case %{target_cpu} in
i[3-5]86)
  InstallGlibc build-i686-linux i686
  ;;
esac
%endif
%if %isarch ppc ppc64
for cpu in %{powerpc_cpu_list}; do
  [[ "$cpu" = "noarch" ]] && continue
  InstallGlibc build-$cpu-linux $cpu
done
# Use hardlinks, not symlinks
# see upper NOTE if you really want dedicated power5+ hwcap...
[[ -d "$RPM_BUILD_ROOT/%{_lib}/power5" ]] && {
  mkdir -p $RPM_BUILD_ROOT/%{_lib}/power5+
  ln -v	$RPM_BUILD_ROOT/%{_lib}/power5/*.so \
	$RPM_BUILD_ROOT/%{_lib}/power5+/
  $RPM_BUILD_ROOT/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_lib}/power5+/
  echo "%dir /%{_lib}/power5+" >> extralibs.filelist
  find $RPM_BUILD_ROOT$LibDir/%{_lib}/power5+/ -maxdepth 1  -type f -o -type l | sed -e "s|$RPM_BUILD_ROOT||" >> extralibs.filelist
}
%endif

# NPTL <bits/stdio-lock.h> is not usable outside of glibc, so include
# the generic one (RH#162634)
install -m644 bits/stdio-lock.h $RPM_BUILD_ROOT%{_includedir}/bits/stdio-lock.h

# Compatibility hack: this locale has vanished from glibc, but some other
# programs are still using it. Normally we would handle it in the %pre
# section but with glibc that is simply not an option
mkdir -p $RPM_BUILD_ROOT%{_datadir}/locale/ru_RU/LC_MESSAGES

# Remove the files we don't want to distribute
rm -f $RPM_BUILD_ROOT%{_libdir}/libNoVersion*
rm -f $RPM_BUILD_ROOT%{_slibdir}/libNoVersion*

ln -sf libbsd-compat.a $RPM_BUILD_ROOT%{_libdir}/libbsd.a
%if %{build_biarch}
ln -sf libbsd-compat.a $RPM_BUILD_ROOT%{_prefix}/lib/libbsd.a
%endif

%if "%{name}" == "glibc"
install -m 644 mandriva/nsswitch.conf $RPM_BUILD_ROOT%{_sysconfdir}/nsswitch.conf
%endif

# Take care of setuids
# -- new security review sez that this shouldn't be needed anymore
#chmod 755 $RPM_BUILD_ROOT%{_libdir}/pt_chown

# This is for ncsd - in glibc 2.2
%if %{build_nscd}
install -m 644 nscd/nscd.conf $RPM_BUILD_ROOT%{_sysconfdir}
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
install -m 755 nscd/nscd.init $RPM_BUILD_ROOT%{_initrddir}/nscd
%endif

# Useless and takes place
rm -rf %buildroot/%{_datadir}/zoneinfo/{posix,right}

# Include ld.so.conf
%if "%{name}" == "glibc"
echo "include ld.so.conf.d/*.conf" > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf
chmod 644 $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf
mkdir -p  $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d
%endif

# ldconfig cache
mkdir -p $RPM_BUILD_ROOT%{_var}/cache/ldconfig
touch $RPM_BUILD_ROOT%{_var}/cache/ldconfig/aux-cache

# Include %{_libdir}/gconv/gconv-modules.cache
> $RPM_BUILD_ROOT%{_libdir}/gconv/gconv-modules.cache
chmod 644 $RPM_BUILD_ROOT%{_libdir}/gconv/gconv-modules.cache

# Add libraries to debug sub-package
%if %{build_debug}
mkdir $RPM_BUILD_ROOT%{_libdir}/debug
#cp -a $RPM_BUILD_ROOT%{_libdir}/*.a $RPM_BUILD_ROOT%{_libdir}/debug/
#rm -f $RPM_BUILD_ROOT%{_libdir}/debug/*_p.a
cp -a $RPM_BUILD_ROOT%{_slibdir}/lib*.so* $RPM_BUILD_ROOT%{_libdir}/debug/

pushd $RPM_BUILD_ROOT%{_libdir}/debug
for lib in *.so*; do
  [[ -f "$lib" ]] && DEBUG_LIBS="$DEBUG_LIBS %{_libdir}/debug/$lib"
done
popd
%endif

# Are we cross-compiling?
Strip="strip"
if [[ "%{_target_cpu}" != "%{target_cpu}" ]]; then
  Strip="%{target_cpu}-linux-$Strip"
fi

# Strip libpthread but keep some symbols
find $RPM_BUILD_ROOT%{_slibdir} -type f -name "libpthread-*.so" | \
     xargs $Strip -g -R .comment

%if %{build_biarch}
find $RPM_BUILD_ROOT/lib -type f -name "libpthread-*.so" | \
     xargs $Strip -g -R .comment
%endif

# Strip debugging info from all static libraries
pushd $RPM_BUILD_ROOT%{_libdir}
for i in *.a; do
  if [ -f "$i" ]; then
    case "$i" in
    *_p.a) ;;
    *) $Strip -g -R .comment $i ;;
    esac
  fi
done
popd

# post install wrapper
%__cc -Os -DSLIBDIR="\"%{_slibdir}\"" -DASH_BIN="\"%{ash_bin}\"" %{SOURCE14} -static \
	-L $RPM_BUILD_ROOT%{_libdir}/ \
	-o $RPM_BUILD_ROOT%{_sbindir}/glibc-post-wrapper
chmod 700 $RPM_BUILD_ROOT%{_sbindir}/glibc-post-wrapper

# rquota.x and rquota.h are now provided by quota
rm -f $RPM_BUILD_ROOT%{_includedir}/rpcsvc/rquota.[hx]

# Hardlink identical locale files together
%if %{build_i18ndata}
gcc -O2 -o build-%{_target_cpu}-linux/hardlink redhat/hardlink.c
build-%{_target_cpu}-linux/hardlink -vc $RPM_BUILD_ROOT%{_datadir}/locale
%endif

rm -rf $RPM_BUILD_ROOT%{_includedir}/netatalk/

# Build file list for devel package
find $RPM_BUILD_ROOT%{_includedir} -type f -or -type l > devel.filelist
find $RPM_BUILD_ROOT%{_includedir} -type d  | sed "s/^/%dir /" | \
  grep -v "%{_libdir}/libnss1.*.so$" | \
  grep -v "%{_includedir}$" | >> devel.filelist
find $RPM_BUILD_ROOT%{_libdir} -maxdepth 1 -name "*.so" -o -name "*.o" | egrep -v "(libmemusage.so|libpcprofile.so)" >> devel.filelist
# biarch libs
%if %{build_biarch}
find $RPM_BUILD_ROOT%{_prefix}/lib -maxdepth 1 -name "*.so" -o -name "*.o" | egrep -v "(libmemusage.so|libpcprofile.so)" >> devel.filelist
%endif
perl -pi -e "s|$RPM_BUILD_ROOT||" devel.filelist

%if %{build_utils}
if [[ "%{_slibdir}" != "%{_libdir}" ]]; then
mkdir -p $RPM_BUILD_ROOT%{_libdir}
mv -f $RPM_BUILD_ROOT%{_slibdir}/lib{pcprofile,memusage}.so $RPM_BUILD_ROOT%{_libdir}
[[ -f $RPM_BUILD_ROOT/lib/libmemusage.so ]] &&
mv -f $RPM_BUILD_ROOT/lib/lib{pcprofile,memusage}.so $RPM_BUILD_ROOT%{_prefix}/lib/
for i in $RPM_BUILD_ROOT%{_prefix}/bin/{xtrace,memusage}; do
  cp -a $i $i.tmp
  sed -e 's~=%{_slibdir}/libpcprofile.so~=%{_libdir}/libpcprofile.so~' \
      -e 's~=%{_slibdir}/libmemusage.so~=%{_libdir}/libmemusage.so~' \
    $i.tmp > $i
  chmod 755 $i; rm -f $i.tmp
done
fi
%endif

# /etc/localtime - we're proud of our timezone #Well we(mdk) may put Paris
%if %{build_timezone}
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/localtime
cp -f $RPM_BUILD_ROOT%{_datadir}/zoneinfo/US/Eastern $RPM_BUILD_ROOT%{_sysconfdir}/localtime
#ln -sf ..%{_datadir}/zoneinfo/US/Eastern $RPM_BUILD_ROOT%{_sysconfdir}/localtime
%endif

# [gg] build PDF documentation
%if %{build_pdf_doc}
(cd manual; texi2dvi -p -t @afourpaper -t @finalout libc.texinfo)
%endif

# Copy Kernel-Headers
mkdir -p $RPM_BUILD_ROOT%{_includedir}
mkdir -p $RPM_BUILD_ROOT/boot/
cp -avrf kernel-headers/* $RPM_BUILD_ROOT%{_includedir}
echo "#if 0" > $RPM_BUILD_ROOT/boot/kernel.h-%{kheaders_ver}

# the last bit: more documentation
rm -rf documentation
mkdir documentation
cp timezone/README documentation/README.timezone
cp ChangeLog* documentation
gzip -9 documentation/ChangeLog*

# Generate final rpm filelist, with localized libc.mo files
rm -f rpm.filelist
%if "%{name}" == "glibc"
%find_lang libc
perl -ne '/^\s*$/ or print' libc.lang > rpm.filelist
%endif
cat extralibs.filelist >> rpm.filelist

# Remove unpackaged files
rm -f  $RPM_BUILD_ROOT%{_infodir}/dir.old*
rm -f  $RPM_BUILD_ROOT%{_prefix}/lib/pt_chown
rm -rf $RPM_BUILD_ROOT%{_includedir}/asm-*/mach-*/
rm -f  $RPM_BUILD_ROOT%{_datadir}/locale/locale-archive*

%if !%{build_utils}
rm -f  $RPM_BUILD_ROOT%{_libdir}/libmemusage.so
rm -f  $RPM_BUILD_ROOT%{_libdir}/libpcprofile.so
rm -f  $RPM_BUILD_ROOT%{_bindir}/memusage
rm -f  $RPM_BUILD_ROOT%{_bindir}/memusagestat
rm -f  $RPM_BUILD_ROOT%{_bindir}/mtrace
rm -f  $RPM_BUILD_ROOT%{_bindir}/pcprofiledump
rm -f  $RPM_BUILD_ROOT%{_bindir}/xtrace
%endif

%if !%{build_timezone}
rm -f  $RPM_BUILD_ROOT%{_sysconfdir}/localtime
rm -f  $RPM_BUILD_ROOT%{_sbindir}/zdump
rm -f  $RPM_BUILD_ROOT%{_sbindir}/zic
rm -f  $RPM_BUILD_ROOT%{_mandir}/man1/zdump.1*
rm -rf $RPM_BUILD_ROOT%{_datadir}/zoneinfo
%endif

%if !%{build_i18ndata}
rm -rf $RPM_BUILD_ROOT%{_datadir}/i18n
%endif

%if "%{name}" != "glibc"
rm -rf $RPM_BUILD_ROOT/boot
rm -rf $RPM_BUILD_ROOT/sbin
rm -rf $RPM_BUILD_ROOT/usr/share
rm -rf $RPM_BUILD_ROOT%{_bindir}
rm -rf $RPM_BUILD_ROOT%{_sbindir}
rm -rf $RPM_BUILD_ROOT%{_datadir}
rm -rf $RPM_BUILD_ROOT%{_mandir}
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -rf $RPM_BUILD_ROOT%{_prefix}/etc
rm -rf $RPM_BUILD_ROOT%{_libdir}/gconv
%endif

# In case we are cross-compiling, don't bother to remake symlinks and
# fool spec-helper when stripping files
%if "%{name}" != "glibc"
export DONT_SYMLINK_LIBS=1
export PATH=%{_bindir}:$PATH
%endif

EXCLUDE_FROM_STRIP="ld-%{glibcversion}.so libpthread $DEBUG_LIBS"
export EXCLUDE_FROM_STRIP

%if "%{name}" == "glibc"
%define upgradestamp %{_slibdir}/glibc.upgraded
%define broken_link %{_slibdir}/libnss_nis.so.1 %{_slibdir}/libnss_files.so.1 %{_slibdir}/libnss_dns.so.1 %{_slibdir}/libnss_compat.so.1

%pre -p %{ash_bin}
# test(1) and echo(1) are built-ins
if [ -d %{_slibdir} ] && [ ! -f %{_slibdir}/libnss_files-%{glibcversion}.so ]; then
  echo > %{upgradestamp}
fi

%post -p %{_sbindir}/glibc-post-wrapper
export LC_ALL=C

if [ "$1" -gt 1 ]; then
  # migrate /etc/ld.so.conf to include the new /etc/ld.so.conf.d/
  # without external commands but for removing the temporary file
  ldso_conf=/etc/ld.so.conf
  while read i; do
    [ "$i" = "include ld.so.conf.d/*.conf" ] && keep=1
    echo $i
  done < $ldso_conf > $ldso_conf-
  if [ -z "$keep" ]; then
    echo "include ld.so.conf.d/*.conf" > $ldso_conf
    while read i; do
      echo $i
    done < $ldso_conf- >> $ldso_conf
  fi
  [ -x /bin/rm ] && /bin/rm -f $ldso_conf-
fi
/sbin/ldconfig

if [ "$1" -gt 1 ]; then
  # On upgrade the services doesn't work because libnss couldn't be
  # loaded anymore.
  if [ -f %{upgradestamp} ]; then
    if /usr/bin/readlink /proc/1/exe >/dev/null && \
       /usr/bin/readlink /proc/1/root >/dev/null; then
       if [ -x /sbin/telinit -a -p /dev/initctl ]; then
         /sbin/telinit u
       fi
       if [ -x /etc/init.d/sshd -a \
            -x /usr/sbin/sshd -a \
            -x /bin/bash ]; then
         /etc/init.d/sshd condrestart
       fi
    fi
  fi
  if [ -f /bin/rm ]; then
    for i in %broken_link; do
      if [ -e $i ] && [ ! -L $i ]; then
        /bin/rm -f $i
      fi
    done
  fi
fi
[ -x /bin/rm ] && /bin/rm -f %{upgradestamp}

# always generate the gconv-modules.cache
%{_sbindir}/iconvconfig -o %{_libdir}/gconv/gconv-modules.cache --nostdlib %{_libdir}/gconv

%postun -p /sbin/ldconfig
%endif

%pre devel
if [ -L %{_includedir}/scsi ]; then
  rm -f %{_includedir}/scsi
fi
if [ -L %{_includedir}/sound ]; then
  rm -f %{_includedir}/sound
fi
if [ -L %{_includedir}/linux ]; then
  rm -f %{_includedir}/linux
fi
if [ -L %{_includedir}/asm ]; then
  rm -f %{_includedir}/asm
fi
if [ -L %{_includedir}/asm-generic ]; then
  rm -f %{_includedir}/asm-generic
fi
%if %isarch x86_64
if [ -L %{_includedir}/asm-x86_64 ]; then
  rm -f %{_includedir}/asm-x86_64
fi
if [ -L %{_includedir}/asm-i386 ]; then
  rm -f %{_includedir}/asm-i386
fi
%endif
%if %isarch ppc64
if [ -L %{_includedir}/asm-ppc64 ]; then
  rm -f %{_includedir}/asm-ppc64
fi
if [ -L %{_includedir}/asm-ppc ]; then
  rm -f %{_includedir}/asm-ppc
fi
%endif
%if %isarch sparc64
if [ -L %{_includedir}/asm-sparc64 ]; then
  rm -f %{_includedir}/asm-sparc64
fi
if [ -L %{_includedir}/asm-sparc ]; then
  rm -f %{_includedir}/asm-sparc
fi
%endif
exit 0

%if "%{name}" == "glibc"
%post devel
cd /boot
rm -f kernel.h
ln -snf kernel.h-%{kheaders_ver} kernel.h
/sbin/service kheader start 2>/dev/null >/dev/null || :
exit 0

%postun devel
if [ $1 = 0 ];then
  if [ -L /boot/kernel.h -a `ls -l /boot/kernel.h 2>/dev/null| awk '{ print $11 }'` = "kernel.h-%{kheader}" ]; then
    rm -f /boot/kernel.h
  fi
fi
exit 0
%endif

%if %{build_doc}
%post doc
%_install_info libc.info

%preun doc
%_remove_install_info libc.info
%endif

%if %{build_utils}
%post utils -p /sbin/ldconfig
%postun utils -p /sbin/ldconfig
%endif

%if %{build_nscd}
%pre -n nscd
%_pre_useradd nscd / /bin/false

%post -n nscd
%_post_service nscd

%preun -n nscd
%_preun_service nscd

%postun -n nscd
%_postun_userdel nscd

if [ "$1" -ge "1" ]; then
  /sbin/service nscd condrestart > /dev/null 2>&1 || :
fi
%endif

%clean
#rm -rf "$RPM_BUILD_ROOT"
#rm -f *.filelist*

#
# glibc
#
%files -f rpm.filelist
%defattr(-,root,root)
%if "%{name}" == "glibc"
%if %{build_timezone}
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/localtime
%endif
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/nsswitch.conf
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/ld.so.conf
%dir %{_sysconfdir}/ld.so.conf.d
%config(noreplace) %{_sysconfdir}/rpc
%doc README.upgrade.urpmi
%doc posix/gai.conf
%{_mandir}/man1/*
%{_mandir}/man8/rpcinfo.8*
%{_mandir}/man8/ld.so*
%{_datadir}/locale/locale.alias
/sbin/sln
%dir %{_prefix}/lib/getconf
%{_prefix}/lib/getconf/*
%endif
%{_slibdir}/ld-%{glibcversion}.so
%if %isarch i386 alpha sparc sparc64
%{_slibdir}/ld-linux.so.2
%endif
%if %isarch ppc
%{_slibdir}/ld.so.1
%endif
%if %isarch ppc64
%{_slibdir}/ld64.so.1
%endif
%if %isarch ia64
%{_slibdir}/ld-linux-ia64.so.2
%endif
%if %isarch x86_64
%{_slibdir}/ld-linux-x86-64.so.2
%endif
%if %isarch m68k
%{_slibdir}/ld.so.1
%endif
%{_slibdir}/lib*-[.0-9]*.so
%{_slibdir}/lib*.so.[0-9]*
%{_slibdir}/libSegFault.so
%if "%{name}" == "glibc"
%dir %{_libdir}/gconv
%{_libdir}/gconv/*
# Don't package pt_chown. It is only needed if devpts is not used. But
# since we are running kernel 2.4+, that's fine without.
# (and it never actually worked, aka was not setuid, nor executable)
#%{_libdir}/pt_chown
%{_bindir}/catchsegv
%{_bindir}/gencat
%{_bindir}/getconf
%{_bindir}/getent
#%{_bindir}/glibcbug
%{_bindir}/iconv
%{_bindir}/ldd
%if %isarch i386 ppc sparc sparc64
%{_bindir}/lddlibc4
%endif
%{_bindir}/locale
%{_bindir}/localedef
%{_bindir}/rpcgen
%{_bindir}/sprof
%{_bindir}/tzselect
%{_sbindir}/rpcinfo
%{_sbindir}/iconvconfig
%{_sbindir}/glibc-post-wrapper
%endif

%if %{build_biarch}
%{_slibdir32}/ld-%{glibcversion}.so
%if %isarch ppc64
%{_slibdir32}/ld.so.1
%else
%{_slibdir32}/ld-linux*.so.2
%endif
%{_slibdir32}/lib*-[.0-9]*.so
%{_slibdir32}/lib*.so.[0-9]*
%{_slibdir32}/libSegFault.so
%dir %{_prefix}/lib/gconv
%{_prefix}/lib/gconv/*
%endif
#
# ldconfig
#
%if "%{name}" == "glibc"
%defattr(-,root,root)
/sbin/ldconfig
%{_mandir}/man8/ldconfig*
%ghost %{_sysconfdir}/ld.so.cache
%dir %{_var}/cache/ldconfig
%ghost %{_var}/cache/ldconfig/aux-cache
%endif

#
# glibc-devel
#
%files devel -f devel.filelist
%defattr(-,root,root)
%doc README NEWS INSTALL FAQ BUGS NOTES PROJECTS CONFORMANCE
%doc COPYING COPYING.LIB
%doc documentation/* README.libm
%doc hesiod/README.hesiod
%{_libdir}/libbsd-compat.a
%{_libdir}/libbsd.a
%{_libdir}/libc_nonshared.a
%{_libdir}/libg.a
%{_libdir}/libieee.a
%{_libdir}/libmcheck.a
%{_libdir}/libpthread_nonshared.a
%if "%{name}" == "glibc"
%{_libdir}/librpcsvc.a
%endif
%if %isarch ppc ppc64 sparc
%{_libdir}/libnldbl_nonshared.a
%endif

%{_includedir}/linux
%{_includedir}/asm
%{_includedir}/asm-generic
%{_includedir}/mtd
%{_includedir}/rdma
%{_includedir}/sound
%{_includedir}/video
%if %isarch x86_64
%dir %{_includedir}/asm-i386
%{_includedir}/asm-i386/*.h
%dir %{_includedir}/asm-x86_64
%{_includedir}/asm-x86_64/*.h
%endif
%if %isarch ppc64
%dir %{_includedir}/asm-ppc
%{_includedir}/asm-ppc/*.h
%dir %{_includedir}/asm-ppc64
%{_includedir}/asm-ppc64/*.h
%dir %{_includedir}/asm-ppc64/iseries
%{_includedir}/asm-ppc64/iseries/*.h
%endif
%if %isarch sparc64
%dir %{_includedir}/asm-sparc
%{_includedir}/asm-sparc/*.h
%dir %{_includedir}/asm-sparc64
%{_includedir}/asm-sparc64/*.h
%endif
%if "%{name}" == "glibc"
/boot/kernel.h-%{kheaders_ver}
%endif

%if %{build_biarch}
%{_prefix}/lib/libbsd-compat.a
%{_prefix}/lib/libbsd.a
%{_prefix}/lib/libc_nonshared.a
%{_prefix}/lib/libg.a
%{_prefix}/lib/libieee.a
%{_prefix}/lib/libmcheck.a
%{_prefix}/lib/libpthread_nonshared.a
%{_prefix}/lib/librpcsvc.a
%if %isarch ppc64 sparc64
%{_prefix}/lib/libnldbl_nonshared.a
%endif
%endif

#
# glibc-static-devel
#
%files static-devel
%defattr(-,root,root)
%doc COPYING COPYING.LIB
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

%if %{build_biarch}
%{_prefix}/lib/libBrokenLocale.a
%{_prefix}/lib/libanl.a
%{_prefix}/lib/libc.a
%{_prefix}/lib/libcrypt.a
%{_prefix}/lib/libdl.a
%{_prefix}/lib/libm.a
%{_prefix}/lib/libnsl.a
%{_prefix}/lib/libpthread.a
%{_prefix}/lib/libresolv.a
%{_prefix}/lib/librt.a
%{_prefix}/lib/libutil.a
%endif

#
# glibc-doc
#
%if %{build_doc}
%files doc
%defattr(-,root,root)
%{_infodir}/libc.info*
%endif

#
# glibc-doc-pdf
#
%if %{build_pdf_doc}
%files doc-pdf
%defattr(-,root,root)
%doc manual/libc.pdf
%endif

#
# glibc-debug
#
%if %{build_debug}
%files debug
%defattr(-,root,root)
%dir %{_libdir}/debug
%{_libdir}/debug/*.so
%{_libdir}/debug/*.so.*
%endif

#
# glibc-profile
#
%if %{build_profile}
%files profile
%defattr(-,root,root)
%{_libdir}/lib*_p.a
%if %{build_biarch}
%{_prefix}/lib/lib*_p.a
%endif
%endif

#
# glibc-utils
#
%if %{build_utils}
%files utils
%defattr(-,root,root)
%if %{build_biarch}
%{_prefix}/lib/libmemusage.so
%{_prefix}/lib/libpcprofile.so
%endif
%{_libdir}/libmemusage.so
%{_libdir}/libpcprofile.so
%{_bindir}/memusage
%{_bindir}/memusagestat
%{_bindir}/mtrace
%{_bindir}/pcprofiledump
%{_bindir}/xtrace
%endif

#
# nscd
#
%if %{build_nscd}
%files -n nscd
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/nscd.conf
%config(noreplace) %{_initrddir}/nscd
%{_sbindir}/nscd
%endif

#
# timezone
#
%if %{build_timezone}
%files -n timezone
%defattr(-,root,root)
%{_sbindir}/zdump
%{_sbindir}/zic
%{_mandir}/man1/zdump.1*
%dir %{_datadir}/zoneinfo
%{_datadir}/zoneinfo/*
%endif

#
# glibc-i18ndata
#
%if %{build_i18ndata}
%files i18ndata
%defattr(-,root,root)
%dir %{_datadir}/i18n
%dir %{_datadir}/i18n/charmaps
%{_datadir}/i18n/charmaps/*
%dir %{_datadir}/i18n/locales
%{_datadir}/i18n/locales/*
%endif


