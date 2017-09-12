# crypt blowfish support
%define crypt_bf_ver	1.3

%define _libdir32	%{_prefix}/lib
%define _libdirn32	%{_prefix}/lib32

%define ver		2.26
%define linaro		%{nil}

%define	oname		glibc
%define	major		6
%if "%{linaro}" != ""
%define	fullver		%{ver}-%{linaro}
%define source_dir	glibc-linaro-%{fullver}
%else
%define	fullver		%{ver}
%define	source_dir	%{oname}-%{ver}
%endif
%define	checklist	%{_builddir}/%{source_dir}/Check.list
%define	libc		%mklibname c %{major}
%define	devname		%mklibname -d c
%define	statname	%mklibname -d -s c
%define	multilibc	libc%{major}

%define _disable_rebuild_configure 1
%define _disable_lto 1
%define	_disable_ld_no_undefined	1

# Define "cross" to an architecture to which glibc is to be
# cross-compiled
%define	build_cross		0
%{expand: %{?cross:		%%global build_cross 1}}

%if %{build_cross}
%define	_srcrpmfilename	%{oname}-%{fullver}-%{release}.src.rpm
%define	_build_pkgcheck_set /usr/bin/rpmlint -T -f %{SOURCE100}
%define	_build_pkgcheck_srpm /usr/bin/rpmlint -T -f %{SOURCE100}
%define target_cpu	%{cross}
%define cross_prefix	cross-%{target_cpu}-
%global	platform	%(rpm --macros %%{_usrlibrpm}/macros:%%{_usrlibrpm}/platform/%{target_cpu}-%{_target_os}/macros --target=%{target_cpu} -E %%{_target_vendor}-%%{_target_os}%%{?_gnu})
%global	target_platform	%(rpm --macros %%{_usrlibrpm}/macros:%%{_usrlibrpm}/platform/%{target_cpu}-%{_target_os}/macros --target=%{target_cpu} -E %%{_target_platform})
%global	target_arch	%(rpm --macros %%{_usrlibrpm}/macros:%%{_usrlibrpm}/platform/%{target_cpu}-%{_target_os}/macros --target=%{target_cpu} -E %%{_arch})
%global	_lib		%(rpm --macros %%{_usrlibrpm}/macros:%%{_usrlibrpm}/platform/%{target_cpu}-%{_target_os}/macros --target=%{target_cpu} -E %%{_lib})
%define _prefix		/usr/%{target_platform}
%define cross_program_prefix	%{target_platform}-
%define _exec_prefix	%{_prefix}
# brain damage alert: should not be needed imho
# overriding _prefix and _exec_prefix should be enough
%define _bindir		%{_exec_prefix}/bin
%define _sbindir	%{_exec_prefix}/sbin
%define _libexecdir	%{_exec_prefix}/libexec
%define _datadir	%{_prefix}/share
%define _sharedstatedir	%{_prefix}/com
%define _localstatedir	%{_prefix}/var
%define _libdir		%{_exec_prefix}/%{_lib}
%define _slibdir	%{_exec_prefix}/%{_lib}
%define _slibdir32	%{_exec_prefix}/lib
%define _slibdirn32	%{_exec_prefix}/lib32
%define _includedir	%{_prefix}/include
%else
%global	platform	%{_target_vendor}-%{_target_os}%{?_gnu}
%global	target_cpu	%{_target_cpu}
%global	target_platform	%{_target_platform}
%global	target_arch	%{_arch}
%define cross_prefix	%{nil}
%define cross_program_prefix	%{nil}
%define _slibdir	/%{_lib}
%define _slibdir32	/lib
%endif

# Define target (base) architecture
%define arch		%(echo %{target_cpu}|sed -e "s/\\(i.86\\|athlon\\)/i386/" -e "s/amd64/x86_64/")
%define isarch()	%(case " %* " in (*" %{arch} "*) echo 1;; (*) echo 0;; esac)

# Define Xen arches to build with -mno-tls-direct-seg-refs
%define xenarches	%{ix86}

# Define to build nscd with selinux support
%bcond_with selinux

# Allow make check to fail only when running kernels where we know
# tests must pass (no missing features or bugs in the kernel)
%define check_min_kver 2.6.21

# Define to build a biarch package
%define build_biarch	0
%if %isarch x86_64 mips64 mips64el mips mipsel
%define build_biarch	1
%endif



%if !%{build_cross}
%bcond_without	nscd
%bcond_without	i18ndata
%bcond_with	timezone
%bcond_without	nsscrypt
%bcond_without	locales


%if %isarch %{ix86} x86_64
%bcond_without	systap
%else
%bcond_with	systap
%endif

# build documentation by default
%bcond_without	doc
%bcond_with	pdf
# enable utils by default
%bcond_without	utils

%else
# Disable a few defaults when cross-compiling a glibc

%bcond_with	doc
%bcond_with	pdf
%bcond_with	nscd
%bcond_with	timezone
%bcond_with	i18ndata
%bcond_with	locales
%bcond_with	systap
%bcond_with	utils
%bcond_with	nsscrypt
%endif

#-----------------------------------------------------------------------
Summary:	The GNU libc libraries
Name:		%{cross_prefix}%{oname}
Epoch:		6
%if "%{linaro}" != ""
Version:	%{ver}_%{linaro}
Source0:	http://cbuild.validation.linaro.org/snapshots/glibc-linaro-%{fullver}.tar.xz
%else
Version:	%{ver}
Source0:	http://ftp.gnu.org/gnu/glibc/%{oname}-%{ver}.tar.xz
%if %(test $(echo %{version}.0 |cut -d. -f3) -lt 90 && echo 1 || echo 0)
Source1:	http://ftp.gnu.org/gnu/glibc/%{oname}-%{ver}.tar.xz.sig
%endif
Release:	5
License:	LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
Group:		System/Libraries
Url:		http://www.gnu.org/software/libc/

# From Fedora
Source2:	glibc_post_upgrade.c
Source3:	glibc-manpages.tar.bz2
Source5:	glibc-check.sh
Source10:	libc-lock.h

# Locales
Source20:	Makefile.locales

# Blowfish support
Source50:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz
Source51:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz.sign
Source52:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.c
Source53:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.h

Source100:	%{oname}.rpmlintrc

Source1000:	localepkg.py
Source1001:	locale_install.sh
Source1002:	locale_uninstall.sh
Source1003:	locales.sysconfig
Source1004:	locales-hardlink.pl
Source1005:	locales-softlink.pl

#-----------------------------------------------------------------------
# fedora patches
Patch21:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-i386-tls-direct-seg-refs.patch
Patch23:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-include-bits-ldbl.patch
Patch24:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-ldd.patch
Patch25:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-linux-tcsetattr.patch
Patch26:	eglibc-fedora-locale-euro.patch
Patch27:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-localedata-rh61908.patch
# We disagree with
#		http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-streams-rh436349.patch
# Therefore we don't package/apply it.
Patch30:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-localedef.patch
Patch31:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-locarchive.patch
Patch32:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-manual-dircategory.patch
Patch33:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-nis-rh188246.patch
Patch34:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-nptl-linklibc.patch
Patch35:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-ppc-unwind.patch
Patch36:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-aarch64-tls-fixes.patch
Patch37:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-aarch64-workaround-nzcv-clobber-in-tlsdesc.patch
Patch38:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-arm-hardfloat-3.patch
Patch40:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-c-utf8-locale.patch
Patch41:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-cs-path.patch
# We disagree with http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-disable-rwlock-elision.patch
# Patch 131 is a much nicer solution that disables rwlock elision only on CPUs that can't handle it.
Patch44:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-__libc_multiple_libcs.patch
Patch45:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-elf-ORIGIN.patch
Patch46:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-nscd.patch
Patch47:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-gcc-PR69537.patch
Patch50:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-nscd-sysconfig.patch
Patch52:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh1009145.patch
Patch54:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh1070416.patch
#Patch55:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh1315108.patch
Patch58:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh1324623.patch
#Patch59:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh1335011.patch
Patch61:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh697421.patch
Patch62:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh741105.patch
Patch63:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh819430.patch
Patch64:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh825061.patch
Patch65:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh827510.patch
Patch66:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-rh952799.patch

#-----------------------------------------------------------------------
# Clear Linux patches
Patch80:	fma.patch
Patch81:	fma-expf.patch
Patch82:	fma-expf-fix.patch
Patch83:	alternate_trim.patch
Patch84:	large-page-huge-page.patch
Patch85:	ldconfig-format-new.patch
Patch86:	madvise-bss.patch
Patch87:	malloc-assert-3.patch
Patch88:	mathlto.patch
Patch89:	use_madv_free.patch

#
# Patches from upstream
#

#-----------------------------------------------------------------------
# OpenMandriva patches
Patch100:	eglibc-mandriva-localedef-archive-follow-symlinks.patch
Patch101:	eglibc-mandriva-fix-dns-with-broken-routers.patch
Patch102:	eglibc-mandriva-nss-upgrade.patch
Patch103:	eglibc-mandriva-share-locale.patch
Patch104:	eglibc-mandriva-nsswitch.conf.patch
Patch105:	eglibc-mandriva-xterm-xvt.patch
Patch106:	eglibc-mandriva-nscd-enable.patch
Patch107:	eglibc-mandriva-nscd-no-host-cache.patch
Patch108:	glibc-2.25.90-Float128-clang.patch
Patch109:	eglibc-mandriva-nscd-init-should-start.patch
Patch110:	eglibc-mandriva-timezone.patch
Patch111:	eglibc-mandriva-biarch-cpp-defines.patch
Patch112:	eglibc-mandriva-ENOTTY-fr-translation.patch
Patch113:	eglibc-mandriva-biarch-utils.patch
Patch114:	eglibc-mandriva-multiarch.patch
Patch117:	eglibc-mandriva-pt_BR-i18nfixes.patch
Patch118:	eglibc-mandriva-testsuite-ldbl-bits.patch
Patch119:	eglibc-mandriva-testsuite-rt-notparallel.patch
Patch120:	glibc-2.19-no-__builtin_va_arg_pack-with-clang.patch
#Patch121:	eglibc-mandriva-no-leaf-attribute.patch
Patch122:	eglibc-mandriva-mdv-avx-owl-crypt.patch
Patch123:	eglibc-mandriva-mdv-owl-crypt_freesec.patch
Patch124:	eglibc-mandriva-avx-relocate_fcrypt.patch
Patch125:	eglibc-mandriva-avx-increase_BF_FRAME.patch
Patch126:	eglibc-mandriva-mdv-wrapper_handle_sha.patch
# Reverts a part of eglibc-fedora-uname-getrlimit.patch that breaks the build
#Patch127:	nptl-getrlimit-compile.patch
# http://sourceware.org/bugzilla/show_bug.cgi?id=14995
# http://sourceware.org/bugzilla/attachment.cgi?id=6795
Patch129:	glibc-2.19-nscd-socket-and-pid-moved-from-varrun-to-run.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1162810
Patch130:	glibc-dso_deps.patch
# http://thread.gmane.org/gmane.linux.kernel/1790211
#Patch131:	glibc-2.22-blacklist-CPUs-from-lock-elision.patch
Patch132:	glibc-2.25-fix-warnings.patch
Patch133:	glibc-2.25-force-use-ld-bfd.patch
# Crypt-blowfish patches
Patch200:	crypt_blowfish-arm.patch

BuildRequires:	autoconf2.5
BuildRequires:	%{cross_prefix}binutils
BuildRequires:	%{cross_prefix}gcc
BuildRequires:	gettext
BuildRequires:	%{?cross:cross-}kernel-headers
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
Requires:	filesystem
Requires(post):	filesystem
%if %isarch %{xenarches}
%rename		%{name}-xen
%endif
# The dynamic linker supports DT_GNU_HASH
%if %{build_cross}
Autoreq:	false
Autoprov:	false
%else
Provides:	rtld(GNU_HASH)
Provides:	glibc-crypt_blowfish = %{crypt_bf_ver}
Provides:	eglibc-crypt_blowfish = %{crypt_bf_ver}
Provides:	should-restart = system
Obsoletes:	glibc-profile
# Old prelink versions breaks the system with glibc 2.11
Conflicts:	prelink < 1:0.4.2-1.20091104.1mdv2010.1
%endif
# Determine minimum kernel versions (rhbz#619538)
%if %isarch armv7hl
# currently using 3.0.35 kernel with wandboard
%define		enablekernel 3.0.35
%else
%define		enablekernel 3.4.0
%endif
Conflicts:	kernel < %{enablekernel}

# Don't try to explicitly provide GLIBC_PRIVATE versioned libraries
%define _filter_GLIBC_PRIVATE 1

%if !%{build_cross}

Obsoletes:	ld.so
Provides:	ld.so
%ifarch %{mips} %{mipsel}
Provides:	ld.so.1
%endif

%rename		ldconfig
%define		nssfilesmajor   2
%define		libnssfiles     %mklibname nss_files %{nssfilesmajor}
%rename		%{libnssfiles}
Provides:	/sbin/ldconfig
Obsoletes:	nss_db
%endif

%if %{build_biarch}
Requires:	%{multilibc} = %{EVRD}
%endif

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

%if "%{name}" == "glibc"
%post -p %{_sbindir}/glibc_post_upgrade
%endif

%if %{with locales}
%package -n locales
Summary:	Base files for localization
Group:		System/Internationalization
Obsoletes:	locales <= 2.18.90-2
Obsoletes:	locales < 6:2.19-13
Requires(post,preun):	bash grep sed coreutils glibc rpm

%description -n locales
These are the base files for language localization.
You also need to install the specific locales-?? for the
language(s) you want. Then the user need to set the
LANG variable to their preferred language in their
~/.profile configuration file.

%{python:import sys; sys.path.append(rpm.expandMacro("%{_sourcedir}"))}
%{python:from localepkg import pkg}

# Locale specifc packages
%{python:pkg("Afar", "aa", ["aa_DJ", "aa_ER", "aa_ET"])}
%{python:pkg("Afrikaans", "af", ["af_ZA"])}
%{python:pkg("Aguaruna", "agr", ["agr_PE"])}
%{python:pkg("Amharic", "am", ["am_ET", "byn_ER", "gez_ER", "gez_ET", "om_ET", "om_KE", "sid_ET", "ti_ER", "ti_ET", "tig_ER", "wal_ET"])}
%{python:pkg("Akan", "ak", ["ak_GH"])}
%{python:pkg("Angika", "anp", ["anp_IN"])}
%{python:pkg("Arabic", "ar", ["ar_AE", "ar_BH", "ar_DZ", "ar_EG", "ar_IN", "ar_IQ", "ar_JO", "ar_KW", "ar_LB", "ar_LY", "ar_MA", "ar_OM", "ar_QA", "ar_SA", "ar_SD", "ar_SS", "ar_SY", "ar_TN", "ar_YE"])}
%{python:pkg("Assamese", "as", ["as_IN"])}
%{python:pkg("Asturian", "ast", ["ast_ES"])}
%{python:pkg("Aymara", "ayc", ["ayc_PE"])}
%{python:pkg("Azeri", "az", ["az_AZ", "az_IR"])}
%{python:pkg("Belarusian", "be", ["be_BY"])}
%{python:pkg("Bemba", "bem", ["bem_ZM"])}
%{python:pkg("Berber", "ber", ["ber_DZ", "ber_MA"])}
%{python:pkg("Bulgarian", "bg", ["bg_BG"])}
%{python:pkg("Bhili", "bhb", ["bhb_IN"])}
%{python:pkg("Bislama", "bi", ["bi_VU"])}
%{python:pkg("Bengali", "bn", ["bn_BD", "bn_IN"])}
%{python:pkg("Tibetan", "bo", ["bo_CN", "bo_IN"])}
%{python:pkg("Breton", "br", ["br_FR"])}
%{python:pkg("Bosnian", "bs", ["bs_BA"])}
%{python:pkg("Catalan", "ca", ["ca_AD", "ca_ES", "ca_FR", "ca_IT"])}
%{python:pkg("Chechen", "ce", ["ce_RU"])}
%{python:pkg("Cherokee", "chr", ["chr_US"])}
%{python:pkg("Crimean Tatar", "crh", ["crh_UA"])}
%{python:pkg("Czech", "cs", ["cs_CZ"])}
%{python:pkg("Chuvash", "cv", ["cv_RU"])}
%{python:pkg("Welsh", "cy", ["cy_GB"])}
%{python:pkg("Danish", "da", ["da_DK"])}
%{python:pkg("German", "de", ["de_AT", "de_BE", "de_CH", "de_DE", "de_LU", "de_IT", "de_LI"])}
%{python:pkg("Dogri", "doi", ["doi_IN"])}
%{python:pkg("Dhivehi", "dv", ["dv_MV"])}
%{python:pkg("Dzongkha", "dz", ["dz_BT"])}
%{python:pkg("Greek", "el", ["r:gr", "el_CY", "el_GR"])}
%{python:pkg("English", "en", ["C", "en_AG", "en_AU", "en_BW", "en_CA", "en_DK", "en_GB", "en_HK", "en_IE", "en_IL", "en_IN", "en_NG", "en_NZ", "en_PH", "en_SG", "en_US", "en_ZA", "en_ZM", "en_ZW"])}
%{python:pkg("Esperanto", "eo", ["eo", "eo_XX"])}
# Potentially unhandled: es@tradicional?, an = Aragonese
%{python:pkg("Spanish", "es", ["an_ES", "es_AR", "es_BO", "es_CL", "es_CO", "es_CR", "es_CU", "es_DO", "es_EC", "es_ES", "es_GT", "es_HN", "es_MX", "es_NI", "es_PA", "es_PE", "es_PR", "es_PY", "es_SV", "es_US", "es_UY", "es_VE"])}
%{python:pkg("Estonian", "et", ["et_EE"])}
%{python:pkg("Basque", "eu", ["eu_ES"])}
%{python:pkg("Farsi", "fa", ["fa_IR"])}
%{python:pkg("Finnish", "fi", ["fi_FI"])}
%{python:pkg("Fulah", "ff", ["ff_SN"])}
%{python:pkg("Faroese", "fo", ["fo_FO"])}
%{python:pkg("French", "fr", ["fr_BE", "fr_CA", "fr_CH", "fr_FR", "fr_LU"])}
%{python:pkg("Friulan", "fur", ["fur_IT"])}
%{python:pkg("Frisian", "fy", ["fy_DE", "fy_NL"])}
%{python:pkg("Irish", "ga", ["ga_IE"])}
%{python:pkg("Scottish Gaelic", "gd", ["gd_GB"])}
%{python:pkg("Galician", "gl", ["gl_ES"])}
%{python:pkg("Gujarati", "gu", ["gu_IN"])}
%{python:pkg("Manx Gaelic", "gv", ["gv_GB"])}
%{python:pkg("Hausa", "ha", ["ha_NG"])}
%{python:pkg("Hebrew", "he", ["he_IL", "iw_IL"])}
%{python:pkg("Hindi", "hi", ["bho_IN", "brx_IN", "hi_IN", "ur_IN"])}
%{python:pkg("Fiji Hindi", "hif", ["hif_FJ"])}
%{python:pkg("Chhattisgarhi", "hne", ["hne_IN"])}
%{python:pkg("Croatian", "hr", ["hr_HR"])}
%{python:pkg("Upper Sorbian", "hsb", ["hsb_DE"])}
%{python:pkg("Breyol", "ht", ["ht_HT"])}
%{python:pkg("Hungarian", "hu", ["hu_HU"])}
%{python:pkg("Armenian", "hy", ["hy_AM"])}
%{python:pkg("Interlingua", "ia", ["ia_FR"])}
%{python:pkg("Indonesian", "id", ["id_ID"])}
%{python:pkg("Igbo", "ig", ["ig_NG"])}
%{python:pkg("Inupiaq", "ik", ["ik_CA"])}
%{python:pkg("Icelandic", "is", ["is_IS"])}
%{python:pkg("Italian", "it", ["it_CH", "it_IT"])}
%{python:pkg("Inuktitut", "iu", ["iu_CA"])}
%{python:pkg("Japanese", "ja", ["ja", "ja_JP"])}
%{python:pkg("Georgian", "ka", ["ka_GE"])}
%{python:pkg("Kazakh", "kk", ["kk_KZ"])}
%{python:pkg("Greenlandic", "kl", ["kl_GL"])}
%{python:pkg("Khmer", "km", ["km_KH"])}
%{python:pkg("Kannada", "kn", ["kn_IN"])}
%{python:pkg("Korean", "ko", ["ko_KR"])}
%{python:pkg("Konkani", "kok", ["kok_IN"])}
%{python:pkg("Kashmiri", "ks", ["ks_IN"])}
%{python:pkg("Kurdish", "ku", ["ku_TR"])}
%{python:pkg("Cornish", "kw", ["kw_GB"])}
%{python:pkg("Kyrgyz", "ky", ["ky_KG"])}
%{python:pkg("Luxembourgish", "lb", ["lb_LU"])}
%{python:pkg("Luganda", "lg", ["lg_UG"])}
%{python:pkg("Limburguish", "li", ["li_BE", "li_NL"])}
%{python:pkg("Ligurian", "lij", ["lij_IT"])}
%{python:pkg("Lingala", "ln", ["ln_CD"])}
%{python:pkg("Laotian", "lo", ["lo_LA"])}
%{python:pkg("Lithuanian", "lt", ["lt_LT"])}
%{python:pkg("Latvian", "lv", ["lv_LV"])}
%{python:pkg("Magahi", "mag", ["mag_IN"])}
%{python:pkg("Maithili", "mai", ["mai_IN", "mai_NP"])}
%{python:pkg("Malagasy", "mg", ["mg_MG"])}
%{python:pkg("Mari", "mhr", ["mhr_RU"])}
%{python:pkg("Maori", "mi", ["mi_NZ"])}
%{python:pkg("Macedonian", "mk", ["mk_MK"])}
%{python:pkg("Malayalam", "ml", ["ml_IN"])}
%{python:pkg("Mongolian", "mn", ["mn_MN"])}
%{python:pkg("Manipuri", "mni", ["mni_IN"])}
%{python:pkg("Marathi", "mr", ["mr_IN"])}
%{python:pkg("Malay", "ms", ["ms_MY"])}
%{python:pkg("Maltese", "mt", ["mt_MT"])}
%{python:pkg("Burmese", "my", ["my_MM"])}
%{python:pkg("Lower Saxon", "nds", ["nds_DE", "nds_NL"])}
%{python:pkg("Nepali", "ne", ["ne_NP"])}
%{python:pkg("Nahuatl", "nhn", ["nhn_MX"])}
%{python:pkg("Niuean", "niu", ["niu_NU", "niu_NZ"])}
%{python:pkg("Dutch", "nl", ["nl_AW", "nl_BE", "nl_NL"])}
%{python:pkg("Norwegian", "no", ["r:nb", "r:nn", "nb_NO", "nn_NO"])}
%{python:pkg("Ndebele", "nr", ["nr_ZA"])}
%{python:pkg("Northern Sotho", "nso", ["nso_ZA"])}
%{python:pkg("Occitan", "oc", ["oc_FR"])}
%{python:pkg("Oriya", "or", ["or_IN"])}
%{python:pkg("Ossetian", "os", ["os_RU"])}
%{python:pkg("Punjabi", "pa", ["pa_IN", "pa_PK"])}
%{python:pkg("Papiamento", "pap", ["r:pp", "pap_AN", "pap_AW", "pap_CW"])}
%{python:pkg("Polish", "pl", ["csb_PL", "pl_PL"])}
%{python:pkg("Pashto", "ps", ["ps_AF"])}
%{python:pkg("Portuguese", "pt", ["pt_BR", "pt_PT"])}
%{python:pkg("Quechua", "quz", ["quz_PE"])}
%{python:pkg("Rajasthani", "raj", ["raj_IN"])}
%{python:pkg("Romanian", "ro", ["ro_RO"])}
%{python:pkg("Russian", "ru", ["ru_RU", "ru_UA"])}
%{python:pkg("Kinyarwanda", "rw", ["rw_RW"])}
%{python:pkg("Sanskrit", "sa", ["sa_IN"])}
%{python:pkg("Santali", "sat", ["sat_IN"])}
%{python:pkg("Sardinian", "sc", ["sc_IT"])}
%{python:pkg("Sindhi", "sd", ["sd_IN"])}
%{python:pkg("Saami", "se", ["se_NO"])}
%{python:pkg("Samogitian", "sgs", ["sgs_LT"])}
%{python:pkg("Secwepemctsin", "shs", ["shs_CA"])}
%{python:pkg("Sinhala", "si", ["si_LK"])}
%{python:pkg("Slovak", "sk", ["sk_SK"])}
%{python:pkg("Slovenian", "sl", ["sl_SI"])}
%{python:pkg("Samoan", "sm", ["sm_WS"])}
%{python:pkg("Serbian", "sr", ["sr_ME", "sr_RS"])}
%{python:pkg("Somali", "so", ["so_DJ", "so_ET", "so_KE", "so_SO"])}
%{python:pkg("Albanian", "sq", ["sq_AL", "sq_MK"])}
%{python:pkg("Swati", "ss", ["ss_ZA"])}
%{python:pkg("Sotho", "st", ["st_ZA"])}
%{python:pkg("Swedish", "sv", ["sv_FI", "sv_SE"])}
# sw_XX?
%{python:pkg("Swahili", "sw", ["sw_KE", "sw_TZ"])}
%{python:pkg("Silesian", "szl", ["szl_PL"])}
%{python:pkg("Tamil", "ta", ["ta_IN", "ta_LK"])}
%{python:pkg("Telugu", "te", ["te_IN"])}
%{python:pkg("Tajik", "tg", ["tg_TJ"])}
%{python:pkg("Thai", "th", ["th_TH"])}
%{python:pkg("Tharu/Tharuhati", "the", ["the_NP"])}
%{python:pkg("Tok Pisin", "tpi", ["tpi_PG"])}
%{python:pkg("Turkmen", "tk", ["tk_TM"])}
%{python:pkg("Pilipino", "tl", ["r:ph", "fil_PH", "tl_PH"])}
%{python:pkg("Tswana", "tn", ["tn_ZA"])}
%{python:pkg("Tonga", "to", ["to_TO"])}
%{python:pkg("Turkish", "tr", ["tr_CY", "tr_TR"])}
%{python:pkg("Tsonga", "ts", ["ts_ZA"])}
%{python:pkg("Tatar", "tt", ["tt_RU"])}
%{python:pkg("Tulu", "tcy", ["tcy_IN"])}
%{python:pkg("Uyghur", "ug", ["ug_CN"])}
%{python:pkg("Unami", "unm", ["unm_US"])}
%{python:pkg("Ukrainian", "uk", ["uk_UA"])}
%{python:pkg("Urdu", "ur", ["ur_PK"])}
%{python:pkg("Uzbek", "uz", ["uz_UZ"])}
%{python:pkg("Venda", "ve", ["ve_ZA"])}
%{python:pkg("Vietnamese", "vi", ["vi_VN"])}
%{python:pkg("Walloon", "wa", ["wa_BE"])}
%{python:pkg("Walser", "wae", ["wae_CH"])}
%{python:pkg("Wolof", "wo", ["wo_SN"])}
%{python:pkg("Xhosa", "xh", ["xh_ZA"])}
%{python:pkg("Yiddish", "yi", ["yi_US"])}
%{python:pkg("Yoruba", "yo", ["yo_NG"])}
%{python:pkg("Yue Chinese (Cantonese)", "yue", ["yue_HK"])}
%{python:pkg("Chinese", "zh", ["zh_CN", "zh_HK", "zh_SG", "zh_TW", "cmn_TW", "hak_TW", "lzh_TW", "nan_TW"])}
%{python:pkg("Zulu", "zu", ["zu_ZA"])}

%endif

%files -f libc.lang
%if "%{name}" == "glibc"
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
%endif
%if %isarch x86_64
%exclude %{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFF32
%exclude %{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFFBIG
%exclude %{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFF32
%exclude %{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFFBIG
%exclude %{_prefix}/libexec/getconf/XBS5_ILP32_OFF32
%exclude %{_prefix}/libexec/getconf/XBS5_ILP32_OFFBIG
%endif
%{_slibdir}/ld-%{fullver}.so
%if %isarch %{ix86}
%{_slibdir}/ld-linux.so.2
%{_slibdir}/i686
%endif
%if %isarch x86_64
%{_slibdir}/ld-linux-x86-64.so.2
%endif
%if %isarch armv7l
%{_slibdir}/ld-linux.so.3
%endif
%if %isarch armv7hl armv6j
%{_slibdir}/ld-linux-armhf.so.3
%endif
%if %isarch aarch64
%{_slibdir}/ld-linux-aarch64.so.1
/lib/ld-linux-aarch64.so.1
%endif
%if %isarch %{mips}
%{_slibdir}/ld.so.1
%endif
%{_slibdir}/lib*-[.0-9]*.so
%{_slibdir}/lib*.so.[0-9]*
%{_slibdir}/libSegFault.so
%if "%{name}" == "glibc"
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
%if %isarch %{ix86}
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
%else
%if %isarch mips mipsel
%if %{build_biarch}
%{_slibdir32}/ld-%{fullver}.so
%{_slibdir32}/ld.so.1
%{_slibdir32}/lib*-[.0-9]*.so
%{_slibdir32}/lib*.so.[0-9]*
%{_slibdir32}/libSegFault.so
%dir %{_slibdirn32}
%{_slibdirn32}/ld*-[.0-9]*.so
%{_slibdirn32}/ld.so.1
%{_slibdirn32}/lib*-[.0-9]*.so
%{_slibdirn32}/lib*.so.[0-9]*
%{_slibdirn32}/libSegFault.so
%endif
%endif
%endif

########################################################################
%if %{build_biarch} && !%{build_cross}
#-----------------------------------------------------------------------
%package -n	%{multilibc}
Summary:	The GNU libc libraries
Group:		System/Libraries
Conflicts:	glibc < 6:2.14.90-13
Requires(post):	%{name}
Requires(post):	bash

%post -n %{multilibc}
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
%{_slibdir32}/ld-%{fullver}.so
%{_slibdir32}/ld-linux*.so.2
%{_slibdir32}/lib*-[.0-9]*.so
%{_slibdir32}/lib*.so.[0-9]*
%{_slibdir32}/libSegFault.so
%if "%{name}" == "glibc"
%dir %{_libdir32}/audit
%{_libdir32}/audit/sotruss-lib.so
%dir %{_libdir32}/gconv
%{_libdir32}/gconv/*.so
%{_libdir32}/gconv/gconv-modules
%ghost %{_libdir32}/gconv/gconv-modules.cache
%endif

%{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFF32
%{_prefix}/libexec/getconf/POSIX_V6_ILP32_OFFBIG
%{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFF32
%{_prefix}/libexec/getconf/POSIX_V7_ILP32_OFFBIG
%{_prefix}/libexec/getconf/XBS5_ILP32_OFF32
%{_prefix}/libexec/getconf/XBS5_ILP32_OFFBIG
#-----------------------------------------------------------------------
# build_biarch
%endif

#-----------------------------------------------------------------------
%package	devel
Summary:	Header and object files for development using standard C libraries
Group:		Development/C
Requires:	%{name} = %{EVRD}
%if %{build_biarch}
Requires:	%{multilibc} = %{EVRD}
%endif
%if %{build_cross}
Autoreq:	false
Autoprov:	false
%else
Autoreq:	true
Provides:	glibc-crypt_blowfish-devel = %{crypt_bf_ver}
Provides:	eglibc-crypt_blowfish-devel = %{crypt_bf_ver}
%endif
Requires:	%{?cross:cross-}kernel-headers
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

%package	doc
Summary:	Docs for %{name}
Group:		Development/C
BuildArch:	noarch

%description	doc
The glibc-docs package contains docs for %{name}.

%files		doc
%doc %{_docdir}/glibc/*
%exclude %{_docdir}/glibc/nss
%exclude %{_docdir}/glibc/gai.conf
%exclude %{_docdir}/glibc/COPYING
%exclude %{_docdir}/glibc/COPYING.LIB

%files		devel
%if "%{name}" == "glibc"
%{_mandir}/man3/*
%{_infodir}/libc.info*
%endif
%{_includedir}/*
%{_libdir}/*.o
%{_libdir}/*.so
%exclude %{_slibdir}/ld*-[.0-9]*.so
%exclude %{_slibdir}/lib*-[.0-9]*.so
%exclude %{_slibdir}/libSegFault.so
%{_libdir}/libc_nonshared.a
# Exists for some, but not all arches
%optional %{_libdir}/libmvec_nonshared.a
%{_libdir}/libg.a
%{_libdir}/libieee.a
%{_libdir}/libmcheck.a
%optional %{_libdir}/libmvec.a
%{_libdir}/libpthread_nonshared.a
%if %{build_biarch}
%{_libdir32}/*.o
%{_libdir32}/*.so
%{_libdir32}/libc_nonshared.a
%{_libdir32}/libg.a
%{_libdir32}/libieee.a
%{_libdir32}/libmcheck.a
%{_libdir32}/libpthread_nonshared.a
%if %isarch mips mipsel
%exclude %{_slibdir32}/ld*-[.0-9]*.so
%exclude %{_slibdir32}/lib*-[.0-9]*.so
%exclude %{_slibdir32}/libSegFault.so
%exclude %{_slibdirn32}/ld*-[.0-9]*.so
%exclude %{_slibdirn32}/lib*-[.0-9]*.so
%exclude %{_slibdirn32}/libSegFault.so
%{_libdirn32}/*.o
%{_libdirn32}/*.so
%{_libdirn32}/libc_nonshared.a
%{_libdirn32}/libg.a
%{_libdirn32}/libieee.a
%{_libdirn32}/libmcheck.a
%{_libdirn32}/libpthread_nonshared.a
%exclude %{_slibdir}/ld*-[.0-9]*.so
%exclude %{_slibdir}/lib*-[.0-9]*.so
%exclude %{_slibdir}/libSegFault.so
%endif
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
# Versioned libm.a seems to be generated only on x86_64
%optional %{_libdir}/libm-%{version}.a
%{_libdir}/libnsl.a
%{_libdir}/libpthread.a
%{_libdir}/libresolv.a
%{_libdir}/librt.a
%{_libdir}/libutil.a
%if %{build_biarch}
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
%if %isarch mips mipsel
%{_libdirn32}/libBrokenLocale.a
%{_libdirn32}/libanl.a
%{_libdirn32}/libc.a
%{_libdirn32}/libcrypt.a
%{_libdirn32}/libdl.a
%{_libdirn32}/libm.a
%{_libdirn32}/libnsl.a
%{_libdirn32}/libpthread.a
%{_libdirn32}/libresolv.a
%{_libdirn32}/librt.a
%{_libdirn32}/libutil.a
%endif
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
nscd -i passwd -i group || :
%systemd_post nscd.socket nscd.service

%files -n 	nscd
%config(noreplace) %{_sysconfdir}/nscd.conf
%dir %attr(0755,root,root) /run/nscd
%dir %attr(0755,root,root) %{_var}/db/nscd
%dir %attr(0755,root,root) %{_sysconfdir}/netgroup
%{_unitdir}/nscd.service
%{_unitdir}/nscd.socket
%{_sbindir}/nscd
%{_tmpfilesdir}/nscd.conf
%attr(0644,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /run/nscd/nscd.pid
%attr(0666,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /run/nscd/socket
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /run/nscd/passwd
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /run/nscd/group
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /run/nscd/hosts
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) /run/nscd/services
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) %{_var}/db/nscd/passwd
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) %{_var}/db/nscd/group
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) %{_var}/db/nscd/hosts
%attr(0600,root,root) %verify(not md5 size mtime) %ghost %config(missingok,noreplace) %{_var}/db/nscd/services
%ghost %config(missingok,noreplace) %{_sysconfdir}/sysconfig/nscd
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
%if %{build_biarch}
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

%prep
%setup -q -n %{source_dir} -a3 -a50
# copy freesec source
cp %{SOURCE52} %{SOURCE53} crypt/
mv crypt/crypt.h crypt/gnu-crypt.h
chmod 0644 crypt_blowfish-%{crypt_bf_ver}/*.[chS]
cp -a crypt_blowfish-%{crypt_bf_ver}/*.[chS] crypt/

%apply_patches

%if %{with selinux}
    # XXX kludge to build nscd with selinux support as it added -nostdinc
    # so /usr/include/selinux is not found
    ln -s %{_includedir}/selinux selinux
%endif

find . -type f -size 0 -o -name "*.orig" -exec rm {} \;

# Remove patch backups from files we ship in glibc packages
#rm localedata/locales/[a-z_]*.*

# Regenerate autoconf files, some of our patches touch them
# Remove the autoconf 2.68 hardcode...
sed -e "s,2.68,`autoconf --version |head -n1 |cut -d' ' -f4`," -i aclocal.m4
# fix nss headers location
sed -e 's@<hasht.h>@<nss/hasht.h>@g' -e 's@<nsslowhash.h>@<nss/nsslowhash.h>@g' -i configure*

aclocal
autoconf

#-----------------------------------------------------------------------
%build
# ...
%if !%{build_cross}
mkdir -p bin
ln -sf %{_bindir}/ld.bfd bin/ld
export PATH=$PWD/bin:$PATH
%endif

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
  # -Wall is just added to get conditionally %%optflags printed...
  # cut -flto flag
  BuildFlags="`rpm --macros %%{_usrlibrpm}/platform/${arch}-%{_target_os}/macros -D '__common_cflags_with_ssp -Wall' -E %%{optflags} | sed -e 's# -fPIC##g' -e 's#-g##' -e 's#-flto##'`"
  case $arch in
    i[3-6]86)
%ifarch x86_64
	BuildFlags="-march=pentium4 -mtune=generic"
	BuildAltArch="yes"
	BuildCompFlags="-m32"
%endif
      ;;
    x86_64)
      BuildFlags="-mtune=generic"
      ;;
    mips|mipsel)
      BuildCompFlags="$BuildFlags"
      ;;
    mips32|mips32el)
      BuildFlags="-march=mips3 -mabi=n32"
      BuildCompFlags="-march=mips3 -mabi=n32"
      ;;
    mips64|mips64el)
      BuildFlags="-march=mips3 -mabi=64"
      BuildCompFlags="-march=mips3 -mabi=64"
      ;;
    armv5t*)
      BuildFlags="-march=armv5t"
      BuildCompFlags="-march=armv5t"
      ;;
    # to check
    armv7*)
      BuildCompFlags="$BuildFlags"
      ;;
    armv6*)
      BuildCompFlags="$BuildFlags"
      ;;
  esac
  BuildCompFlags="$BuildCompFlags"

  # Choose biarch support
  MultiArchFlags=
  case $arch in
    i686 | x86_64)
      MultiArchFlags="--enable-multi-arch"
      ;;
  esac

  # Determine C & C++ compilers
  BuildCC="gcc -fuse-ld=bfd $BuildCompFlags"
  BuildCXX="g++ -fuse-ld=bfd $BuildCompFlags"

  # Are we supposed to cross-compile?
  if [[ "%{target_cpu}" != "%{_target_cpu}" ]]; then
    # Can't use BuildCC anymore with previous changes.
    BuildCC="%{cross_program_prefix}gcc $BuildCompFlags"
    BuildCXX="%{cross_program_prefix}g++ $BuildCompFlags"
    BuildCross="--build=%{_target_platform}"
    export libc_cv_forced_unwind=yes libc_cv_c_cleanup=yes
  fi

  BuildFlags="$BuildFlags -DNDEBUG=1 %{__common_cflags} -O3"
  %if "%{distepoch}" >= "2015.0"
  BuildFlags="$BuildFlags -fno-lto"
  %endif

  if [ "$arch" = "i686" ]; then
    # Work around https://sourceware.org/ml/libc-alpha/2015-10/msg00745.html
    BuildCC="$BuildCC -fomit-frame-pointer"
    BuildCXX="$BuildCXX -fomit-frame-pointer"
  fi

  # XXX: -frecord-gcc-switches makes gold abort with assertion error and gcc segfault :|
  BuildFlags="$(echo $BuildFlags |sed -e 's#-frecord-gcc-switches##g')"

  # Do not use direct references against %gs when accessing tls data
  # XXX make it the default in GCC? (for other non glibc specific usage)
%if %isarch %{xenarches}
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

  # Add-ons
  AddOns="libidn"

  # Kernel headers directory
  %if "%{name}" == "glibc"
    KernelHeaders=%{_includedir}
  %else
    KernelHeaders=/usr/%{target_arch}-%{_target_os}/include
  %endif

  LIB=$(rpm --macros %{_usrlibrpm}/macros:%{_usrlibrpm}/platform/${arch}-%{_target_os}/macros --target=${arch} -E %%{_lib})
%if %{build_cross}
    LIBDIR=%{_exec_prefix}/${LIB}
    SLIBDIR=%{_exec_prefix}/${LIB}
%else
  LIBDIR=$(rpm --macros %{_usrlibrpm}/macros:%{_usrlibrpm}/platform/${arch}-%{_target_os}/macros --target=${arch} -E %%{_libdir})
  SLIBDIR=/${LIB}
%endif

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
  # Force a separate object dir
  mkdir -p build-$arch-linux
  pushd  build-$arch-linux
  [[ "$BuildAltArch" = "yes" ]] && touch ".alt" || touch ".main"
  export libc_cv_slibdir=${SLIBDIR}
  CC="$BuildCC" CXX="$BuildCXX" CFLAGS="$BuildFlags -Wno-error" LDFLAGS="%{ldflags} -fuse-ld=bfd" ../configure \
    --target=$arch-%{platform} \
    --host=$arch-%{platform} \
    $BuildCross \
    --prefix=%{_prefix} \
    --libexecdir=%{_prefix}/libexec \
    --libdir=${LIBDIR} \
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
%if !%{with nscd}
    --disable-build-nscd \
%endif
    --enable-bind-now \
    --enable-lock-elision \
    $ExtraFlags \
    $MultiArchFlags \
    --enable-kernel=%{enablekernel} \
    --with-headers=$KernelHeaders ${1+"$@"} \
    --with-bugurl=%{bugurl}
  make -r all subdir_stubs
  popd

  check_flags="-k"

  # Generate test matrix
  [[ -d "build-$arch-linux" ]] || {
    echo "ERROR: PrepareGlibcTest: build-$arch-linux does not exist!"
    return 1
  }
  local BuildJobs="%{_smp_mflags}"
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
BuildGlibc %{target_cpu}

%if %{build_biarch}
    %if %isarch x86_64
	BuildGlibc i686
    %endif
    %if %isarch mips
	BuildGlibc mips64
	BuildGlibc mips32
    %endif
    %if %isarch mipsel
	BuildGlibc mips64el
	BuildGlibc mips32el
    %endif
    %if %isarch mips64
	BuildGlibc mips
	BuildGlibc mips32
    %endif
    %if %isarch mips64el
	BuildGlibc mipsel
	BuildGlibc mips32el
    %endif
%else
    # Build i686 libraries if not already building for i686
    case %{target_cpu} in
    i686)
	;;
    i[3-5]86)
	BuildGlibc i686
	;;
    esac
%endif

%if "%{name}" == "glibc"
make -C crypt_blowfish-%{crypt_bf_ver} man

# post install wrapper
gcc -static -Lbuild-%{target_cpu}-linux %{optflags} -Os %{SOURCE2} -o build-%{target_cpu}-linux/glibc_post_upgrade \
  '-DLIBTLS="/%{_lib}/tls/"' \
  '-DGCONV_MODULES_DIR="%{_libdir}/gconv"' \
  '-DLD_SO_CONF="/etc/ld.so.conf"' \
  '-DICONVCONFIG="%{_sbindir}/iconvconfig"'
%endif

#-----------------------------------------------------------------------

%if !%{build_cross}
%check
# ...
export PATH=$PWD/bin:$PATH

export TMPDIR=/tmp
export TIMEOUTFACTOR=16
while read arglist; do
    sh %{SOURCE5} $arglist || exit 1
done < %{checklist}
%endif

#-----------------------------------------------------------------------
%install
# ...
%if !%isarch %{mipsx}
export PATH=$PWD/bin:$PATH
%endif

make install_root=%{buildroot} install -C build-%{target_cpu}-linux

%if %{build_biarch} || %isarch %{mips} %{mipsel}
    %if %isarch x86_64
	ALT_ARCHES=i686-linux
    %endif
    %if %isarch %{mips}
	ALT_ARCHES="mips64-linux mips32-linux"
    %endif
    %if %isarch %{mipsel}
	ALT_ARCHES="mips64el-linux mips32el-linux"
    %endif
    %if %isarch mips64
	ALT_ARCHES="mips-linux mips32-linux"
    %endif
    %if %isarch mips64el
	ALT_ARCHES="mipsel-linux mips32el-linux"
    %endif
    for ALT_ARCH in $ALT_ARCHES; do
	mkdir -p %{buildroot}/$ALT_ARCH
	%make install_root=%{buildroot}/$ALT_ARCH -C build-$ALT_ARCH \
	%if %{build_cross}
		install-headers install-lib
	%else
		install
	%endif

	# Dispatch */lib only
	case "$ALT_ARCH" in
	    mips32*)
		LIB="%{_slibdirn32}"
		;;
	    mips64*)
		LIB="%{_slibdir}"
		;;
	    mips*)
		LIB="%{_slibdir32}"
		;;
	    *)
		LIB=/lib
		;;
	esac
	%if !%{build_cross}
	    mv     %{buildroot}/$ALT_ARCH/$LIB %{buildroot}/$LIB
	    mv     %{buildroot}/$ALT_ARCH%{_libexecdir}/getconf/* %{buildroot}%{_prefix}/libexec/getconf/
	    [ ! -d %{buildroot}%{_prefix}/$LIB/ ] && mkdir -p %{buildroot}%{_prefix}/$LIB/
	    mv     %{buildroot}/$ALT_ARCH%{_prefix}/$LIB/* %{buildroot}%{_prefix}/$LIB/
	%else
	    mv     %{buildroot}/$ALT_ARCH%{_prefix}/lib %{buildroot}/$LIB
	    sed -e "s!%{_slibdir}!$LIB!g" -i %{buildroot}/$LIB/libc.so
	%endif

	rm -rf %{buildroot}/$ALT_ARCH
	# XXX Dispatch 32-bit stubs
	(sed '/^@/d' include/stubs-prologue.h; LC_ALL=C sort $(find build-$ALT_ARCH -name stubs)) \
	> %{buildroot}%{_includedir}/gnu/stubs-32.h
	done
%endif

%if "%{name}" == "glibc"
    install -m700 build-%{target_cpu}-linux/glibc_post_upgrade -D %{buildroot}%{_sbindir}/glibc_post_upgrade
    sh manpages/Script.sh
%endif

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
%if %isarch %{ix86}
case %{target_cpu} in
i[3-5]86)
  InstallGlibc build-i686-linux i686
  ;;
esac
%endif

# NPTL <bits/stdio-lock.h> is not usable outside of glibc, so include
# the generic one (RH#162634)
install -m644 sysdeps/generic/stdio-lock.h -D %{buildroot}%{_includedir}/bits/stdio-lock.h
# And <bits/libc-lock.h> needs sanitizing as well.
install -m644 %{SOURCE10} -D %{buildroot}%{_includedir}/bits/libc-lock.h

# Compatibility hack: this locale has vanished from glibc, but some other
# programs are still using it. Normally we would handle it in the %pre
# section but with glibc that is simply not an option
mkdir -p %{buildroot}%{_localedir}/ru_RU/LC_MESSAGES

# kernel headers are located in a directory neutral to whatever target_cpu built for, so
# let's create symlinks into the target tree
%if "%{name}" != "glibc"
  for path in /usr/%{target_arch}-%{_target_os}/include/*; do
    dir=$(basename $path)
    mkdir -p %{buildroot}%{_includedir}/$dir
    ln -s $path/* %{buildroot}%{_includedir}/$dir
  done
%endif

%if "%{name}" == "glibc"
install -m 644 mandriva/nsswitch.conf %{buildroot}%{_sysconfdir}/nsswitch.conf
%endif

# This is for ncsd - in glibc 2.2
%if %{with nscd}
    install -m644 nscd/nscd.conf -D %{buildroot}%{_sysconfdir}/nscd.conf
    install -m755 -d %{buildroot}%{_sysconfdir}/sysconfig
    touch %{buildroot}%{_sysconfdir}/sysconfig/nscd
    install -m755 -d %{buildroot}%{_sysconfdir}/netgroup
    mkdir -p %{buildroot}%{_unitdir}
    install -m 644 nscd/nscd.service nscd/nscd.socket %{buildroot}%{_unitdir}
    install -m644 nscd/nscd.tmpfiles -D %{buildroot}%{_tmpfilesdir}/nscd.conf
    install -m755 -d %{buildroot}%{_var}/db/nscd
    touch %{buildroot}%{_var}/db/nscd/{passwd,group,hosts,services}
    install -m755 -d %{buildroot}/run/nscd
    touch %{buildroot}/run/nscd/{nscd.pid,socket,passwd,group,hosts,services}
%endif

# These man pages require special attention
mkdir -p %{buildroot}%{_mandir}/man3
install -p -m 0644 crypt_blowfish-%{crypt_bf_ver}/*.3 %{buildroot}%{_mandir}/man3/

# Include ld.so.conf
%if "%{name}" == "glibc"
%if %isarch mips mipsel
# needed to get a ldd which understands o32, n32, 64
install -m755 build-%{_target_cpu}-linux/elf/ldd %{buildroot}%{_bindir}/ldd
%endif
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
%if %{build_biarch}
    touch %{buildroot}%{_libdir32}/gconv/gconv-modules.cache
    chmod 644 %{buildroot}%{_libdir32}/gconv/gconv-modules.cache
%endif

touch %{buildroot}%{_sysconfdir}/ld.so.cache
%endif

# Are we cross-compiling?
Strip="strip"
if [[ "%{_target_cpu}" != "%{target_cpu}" ]]; then
  Strip="%{cross_program_prefix}$Strip"
fi

# Strip debugging info from all static libraries
pushd %{buildroot}%{_slibdir}
for i in *.a; do
  if [ -f "$i" ]; then
    case "$i" in
    *_p.a) ;;
    *) $Strip -g -R .comment -R .GCC.command.line         $i ;;
    esac
  fi
done
popd

%if %{with i18ndata}
    install -m644 localedata/SUPPORTED %{buildroot}%{_datadir}/i18n/
%endif

rm -r %{buildroot}%{_includedir}/netatalk/

# /etc/localtime - we're proud of our timezone #Well we(mdk) may put Paris
%if %{with timezone}
    rm %{buildroot}%{_sysconfdir}/localtime
    cp -f %{buildroot}%{_datadir}/zoneinfo/CET %{buildroot}%{_sysconfdir}/localtime
%endif

# Documentation
install -m 755 -d %{buildroot}%{_docdir}/glibc
    pushd build-%{target_cpu}-linux
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
    CONFORMANCE hesiod/README.hesiod					\
    ChangeLog* crypt/README.ufc-crypt nis/nss posix/gai.conf		\
    %{buildroot}%{_docdir}/glibc
xz -0 --text -T0 %{buildroot}%{_docdir}/glibc/ChangeLog*
install -m 644 timezone/README %{buildroot}%{_docdir}/glibc/README.timezone
install -m 755 -d %{buildroot}%{_docdir}/glibc/crypt_blowfish
install -m 644 crypt_blowfish-%{crypt_bf_ver}/{README,LINKS,PERFORMANCE} \
    %{buildroot}%{_docdir}/glibc/crypt_blowfish

# Localization
%if "%{name}" == "glibc"
%find_lang libc
%else
touch libc.lang
%endif

# Remove unpackaged files
rm -f %{buildroot}%{_bindir}/rpcgen %{buildroot}%{_mandir}/man1/rpcgen.1*

# XXX: verify
#find %{buildroot}%{_localedir} -type f -name LC_\* -o -name SYS_LC_\* |xargs rm -f

%if %{without utils}
    rm -f %{buildroot}%{_bindir}/memusage
    rm -f %{buildroot}%{_bindir}/memusagestat
    rm -f %{buildroot}%{_bindir}/mtrace
    rm -f %{buildroot}%{_bindir}/pcprofiledump
    rm -f %{buildroot}%{_bindir}/xtrace
    rm -f %{buildroot}%{_slibdir}/libmemusage.so
    rm -f %{buildroot}%{_slibdir}/libpcprofile.so
    %if %{build_biarch}
	rm -f %{buildroot}%{_slibdir32}/libmemusage.so
	rm -f %{buildroot}%{_slibdir32}/libpcprofile.so
    %endif
    %if %isarch %{mips} %{mipsel}
	rm -f %{buildroot}%{_slibdirn32}/libmemusage.so
	rm -f %{buildroot}%{_slibdirn32}/libpcprofile.so
    %endif
%endif

%if !%{with timezone}
    rm -f %{buildroot}%{_sbindir}/zdump
    rm -f %{buildroot}%{_sbindir}/zic
    rm -f %{buildroot}%{_mandir}/man1/zdump.1*
%endif

%if !%{with i18ndata}
    rm -rf %{buildroot}%{_datadir}/i18n
%endif

%if %{with locales}
# Build locales...
export PATH=%{buildroot}%{_bindir}:%{buildroot}%{_sbindir}:$PATH
%global	glibcver %(rpm -q --qf "%%{VERSION}" glibc)
%if "%{shrink:%{python:rpm.evrCompare(rpm.expandMacro("%{ver}"),rpm.expandMacro("%{glibcver}"))}}" == "0"
export LD_LIBRARY_PATH=%{buildroot}%{_slibdir}:%{buildroot}%{_libdir}:$LD_LIBRARY_PATH
%endif
export I18NPATH=%{buildroot}%{_datadir}/i18n

# make default charset pseudo-locales
# those will be symlinked (for LC_CTYPE, LC_COLLATE mainly) from
# a lot of other locales, thus saving space
for DEF_CHARSET in UTF-8 ISO-8859-1 ISO-8859-2 ISO-8859-3 ISO-8859-4 \
	 ISO-8859-5 ISO-8859-7 ISO-8859-9 \
	 ISO-8859-13 ISO-8859-14 ISO-8859-15 KOI8-R KOI8-U CP1251 
do
	# don't use en_DK because of LC_MONETARY
	localedef -c -f $DEF_CHARSET -i en_US %{buildroot}%{_datadir}/locale/$DEF_CHARSET || :
done

# Build regular locales
# Don't try to use SMP make here - that would result in concurrent writes to the locale
# archive.
SUPPORTED=$I18NPATH/SUPPORTED DESTDIR=%{buildroot} make -f %{SOURCE20}
# Locale related tools
install -c -m 755 %{SOURCE1001} %{SOURCE1002} %{buildroot}%{_bindir}/
# And configs
install -c -m 644 %{SOURCE1003} -D %{buildroot}%{_sysconfdir}/sysconfig/locales

# Hardlink identical locales
perl %{SOURCE1004} %{buildroot}%{_datadir}/locale
# Symlink identical files
pushd %{buildroot}%{_datadir}/locale
for i in ??_??* ???_??*; do
	LC_ALL=C perl %{SOURCE1005} $i
done
popd

# Needed for/used by locale-archive
mkdir -p %{buildroot}%{_prefix}/lib/locale
touch %{buildroot}%{_prefix}/lib/locale/locale-archive
%endif

%if %isarch aarch64
# Compat symlink -- some versions of ld hardcoded /lib/ld-linux-aarch64.so.1
# as dynamic loader
ln -s %{_slibdir}/ld-linux-aarch64.so.1 %{buildroot}/lib/ld-linux-aarch64.so.1
%endif

%if %isarch x86_64
# Needed for bootstrapping x32 compilers
[ -e %{buildroot}%{_includedir}/gnu/stubs-x32.h ] || cp %{buildroot}%{_includedir}/gnu/stubs-64.h %{buildroot}%{_includedir}/gnu/stubs-x32.h
%endif

%if "%{name}" != "glibc"
rm -rf %{buildroot}/boot
rm -rf %{buildroot}/sbin
rm -rf %{buildroot}/usr/share
rm -rf %{buildroot}%{_bindir}
rm -rf %{buildroot}%{_sbindir}
rm -rf %{buildroot}%{_datadir}
rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_prefix}/etc
rm -rf %{buildroot}%{_libdir}/gconv
rm -rf %{buildroot}%{_libdir32}/gconv
rm -rf %{buildroot}%{_libdirn32}/gconv
rm -rf %{buildroot}%{_libdir}/audit
rm -rf %{buildroot}%{_libdir32}/audit
rm -rf %{buildroot}%{_libdirn32}/audit
rm -rf %{buildroot}%{_libexecdir}/getconf
rm -rf %{buildroot}%{_localstatedir}/db/Makefile


# In case we are cross-compiling, don't bother to remake symlinks and
# fool spec-helper when stripping files
export DONT_SYMLINK_LIBS=1
%endif

# This will make the '-g' argument to be passed to eu-strip for these libraries, so that
# some info is kept that's required to make valgrind work without depending on glibc-debug
# package to be installed.
export EXCLUDE_FROM_FULL_STRIP="ld-%{fullver}.so libpthread libc-%{fullver}.so libm-%{fullver}.so"

unset LD_LIBRARY_PATH

%if %{with locales}
%files -n locales
%{_bindir}/locale_install.sh
%{_bindir}/locale_uninstall.sh
%config(noreplace) %{_sysconfdir}/sysconfig/locales
%dir %{_datadir}/locale
%dir %{_prefix}/lib/locale
%ghost %{_prefix}/lib/locale/locale-archive
%{_datadir}/locale/ISO*
%{_datadir}/locale/CP*
%{_datadir}/locale/UTF*
%{_datadir}/locale/KOI*

%post -n locales
%{_bindir}/locale_install.sh "ENCODINGS"

%preun -n locales
%{_bindir}/locale_uninstall.sh "ENCODINGS"
%endif
