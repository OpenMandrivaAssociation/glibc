%bcond_without crosscompilers
%ifarch %{ix86} %{arm}
# FIXME add riscv32-linux when glibc starts supporting it
# FIXME Determine why (and fix) 32-bit platform to x86_64-linux crosscompilers
# are broken (build failure with static assertion on offset of __private_ss)
%global targets aarch64-linux armv7hnl-linux i686-linux x32-linux riscv64-linux
%else
# FIXME add riscv32-linux when glibc starts supporting it
%global targets aarch64-linux armv7hnl-linux i686-linux x86_64-linux x32-linux riscv64-linux
%endif
%global long_targets %(
        for i in %{targets}; do
                CPU=$(echo $i |cut -d- -f1)
                OS=$(echo $i |cut -d- -f2)
                echo -n "$(rpm --target=${CPU}-${OS} -E %%{_target_platform}) "
        done
)

%define _libdir32 %{_prefix}/lib
%define _libdirn32 %{_prefix}/lib32

%define ver 2.29
%define linaro %{nil}

%define oname glibc
%define major 6
%if "%{linaro}" != ""
%define fullver %{ver}-%{linaro}
%define source_dir glibc-linaro-%{fullver}
%else
%define fullver %{ver}
%define source_dir %{oname}-%{ver}
%endif
%define checklist %{_builddir}/%{source_dir}/Check.list
%define libc %mklibname c %{major}
%define devname %mklibname -d c
%define statname %mklibname -d -s c
%define multilibc libc%{major}

%define _disable_rebuild_configure 1
%define _disable_lto 1
%define _disable_ld_no_undefined 1

# (tpg) optimize it a bit
%global optflags %{optflags} -O3

%global platform %{_target_vendor}-%{_target_os}%{?_gnu}
%global target_cpu %{_target_cpu}

%global target_platform %{_target_platform}
%global target_arch %{_arch}
%define cross_prefix %{nil}
%define cross_program_prefix %{nil}
%define _slibdir /%{_lib}
%define _slibdir32 /lib

# Define target (base) architecture
%define arch %(echo %{target_cpu}|sed -e "s/\\(i.86\\|athlon\\)/i386/" -e "s/amd64/x86_64/")
%define isarch() %(case " %* " in (*" %{arch} "*) echo 1;; (*) echo 0;; esac)

# Define Xen arches to build with -mno-tls-direct-seg-refs
%define xenarches %{ix86}

# Determine minimum kernel versions (rhbz#619538)
%ifarch %{arm}
# currently using 3.0.35 kernel with wandboard
%define enablekernel 3.0.35
%else
%ifarch %{aarch64}
# Before increasing, please make sure all
# boxes we support can be updated:
# As of 2018/06/08:
# Opteron server boxes have 4.4.x
# Rockchip 3399 has 4.4.x
# Gemini PDA has 3.18.x
%define enablekernel 3.18.0
%else
%define enablekernel 4.14.0
%endif
%endif

# Define to build nscd with selinux support
%bcond_with selinux

# Define to build a biarch package
%define build_biarch 0
%if %isarch %{x86_64} mips64 mips64el mips mipsel
%define build_biarch 1
%endif

%bcond_without nscd
%bcond_without i18ndata
%bcond_with timezone
%bcond_without locales

%if %isarch %{ix86} %{x86_64}
%bcond_without systap
%else
%bcond_with systap
%endif

# build documentation by default
%bcond_without doc
%bcond_with pdf
# enable utils by default
%bcond_without utils

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
#if %(test $(echo %{version}.0 |cut -d. -f3) -lt 90 && echo 1 || echo 0)
#Source1:	http://ftp.gnu.org/gnu/glibc/%{oname}-%{ver}.tar.xz.sig
#endif
%endif
Release:	1
License:	LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
Group:		System/Libraries
Url:		http://www.gnu.org/software/libc/

# From Fedora
Source2:	glibc_post_upgrade.c
Source3:	glibc-manpages.tar.bz2
Source5:	glibc-check.sh
Source10:	libc-lock.h
# (tpg) our NSS config
Source11:	nsswitch.conf

Source100:	%{oname}.rpmlintrc
Source1000:	localepkg.sh
Source1001:	locale_install.sh
Source1002:	locale_uninstall.sh
Source1003:	locales.sysconfig

#-----------------------------------------------------------------------
# fedora patches
Patch21:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-i386-tls-direct-seg-refs.patch
Patch23:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-include-bits-ldbl.patch
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
Patch38:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-arm-hardfloat-3.patch
Patch40:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-c-utf8-locale.patch
Patch41:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-cs-path.patch
# We disagree with http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-disable-rwlock-elision.patch
# Patch 131 is a much nicer solution that disables rwlock elision only on CPUs that can't handle it.
Patch44:	http://pkgs.fedoraproject.org/cgit/rpms/glibc.git/plain/glibc-fedora-__libc_multiple_libcs.patch
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

#-----------------------------------------------------------------------
# Clear Linux patches
Patch83:	https://github.com/clearlinux-pkgs/glibc/blob/master/alternate_trim.patch
Patch84:	https://github.com/clearlinux-pkgs/glibc/blob/master/madvise-bss.patch
Patch85:	https://github.com/clearlinux-pkgs/glibc/blob/master/spinaphore.patch
Patch86:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/large-page-huge-page.patch
Patch87:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/use_madv_free.patch
Patch88:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/malloc_tune.patch
Patch89:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/ldconfig-format-new.patch
# (tpg) CLR disabled this patch
#Patch90:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/ldconfig-Os.patch
# https://sourceware.org/ml/libc-alpha/2018-03/msg00504.html
Patch98:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/pause.patch
Patch99:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/gcc-8-fix.patch
Patch100:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/spin-smarter.patch
Patch101:	https://raw.githubusercontent.com/clearlinux-pkgs/glibc/master/nostackshrink.patch

#
# Patches from upstream
#

#-----------------------------------------------------------------------
# OpenMandriva patches
Patch1000:	eglibc-mandriva-localedef-archive-follow-symlinks.patch
Patch1001:	eglibc-mandriva-fix-dns-with-broken-routers.patch
Patch1002:	eglibc-mandriva-nss-upgrade.patch
Patch1003:	eglibc-mandriva-share-locale.patch
Patch1004:	eglibc-mandriva-nsswitch.conf.patch
Patch1005:	eglibc-mandriva-xterm-xvt.patch
Patch1006:	eglibc-mandriva-nscd-enable.patch
Patch1007:	eglibc-mandriva-nscd-no-host-cache.patch
Patch1009:	eglibc-mandriva-nscd-init-should-start.patch
Patch1010:	eglibc-mandriva-timezone.patch
Patch1011:	eglibc-mandriva-biarch-cpp-defines.patch
Patch1012:	eglibc-mandriva-ENOTTY-fr-translation.patch
Patch1013:	eglibc-mandriva-biarch-utils.patch
Patch1015:	glibc-2.26-no-attribute-leaf-for-clang.patch
Patch1018:	eglibc-mandriva-testsuite-ldbl-bits.patch
Patch1019:	eglibc-mandriva-testsuite-rt-notparallel.patch
Patch1020:	glibc-2.19-no-__builtin_va_arg_pack-with-clang.patch
#Patch1021:	eglibc-mandriva-no-leaf-attribute.patch
# http://sourceware.org/bugzilla/show_bug.cgi?id=14995
# http://sourceware.org/bugzilla/attachment.cgi?id=6795
Patch1029:	glibc-2.19-nscd-socket-and-pid-moved-from-varrun-to-run.patch
Patch1033:	glibc-2.25-force-use-ld-bfd.patch
Patch1034:	glibc-2.27-clang-_Float.patch
Patch1035:	glibc-2.28-riscv-compile.patch

BuildRequires:	autoconf2.5
BuildRequires:	%{cross_prefix}binutils >= 2.30-7
BuildRequires:	%{cross_prefix}gcc
BuildRequires:	gettext
BuildRequires:	%{?cross:cross-}kernel-release-headers >= %{enablekernel}
BuildRequires:	patch
BuildRequires:	hardlink
BuildRequires:	cap-devel
BuildRequires:	bison
BuildRequires:	pkgconfig(libidn2)
BuildRequires:	systemd
%if %{with selinux}
BuildRequires:	libselinux-devel >= 1.17.10
%endif
BuildRequires:	texinfo
%if %{with pdf}
BuildRequires:	texlive
%endif
%if %{with utils}
BuildRequires:	gd-devel pkgconfig(zlib) pkgconfig(libpng)
%endif
%if %{with systap}
BuildRequires:	systemtap-devel
%endif
Requires:	filesystem
Requires(post):	filesystem
%if %isarch %{xenarches}
%rename		%{name}-xen
%endif
# The dynamic linker supports DT_GNU_HASH
Provides:	rtld(GNU_HASH)
Provides:	should-restart = system
Obsoletes:	glibc-profile
# Old prelink versions breaks the system with glibc 2.11
Conflicts:	prelink < 1:0.4.2-1.20091104.1mdv2010.1

Conflicts:	kernel < %{enablekernel}

# Don't try to explicitly provide GLIBC_PRIVATE versioned libraries
%global __filter_GLIBC_PRIVATE 1

%rename		ld.so
%ifarch %{mips} %{mipsel}
Provides:	ld.so.1
%endif
%rename		ldconfig
%define		libnssfiles %mklibname nss_files 2
%rename		%{libnssfiles}
Provides:	/sbin/ldconfig
Obsoletes:	nss_db

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
%post -p <lua>
os.execute("/usr/sbin/glibc_post_upgrade")

%transfiletriggerin -p <lua> -- /lib/ /lib64/ /usr/lib/ /usr/lib64/ /etc/ld.so.conf.d/
os.execute("/sbin/ldconfig -X")

%transfiletriggerpostun -p <lua> -- /lib/ /lib64/ /usr/lib/ /usr/lib64/ /etc/ld.so.conf.d/
os.execute("/sbin/ldconfig -X")
%endif

%if %{with locales}
%package -n locales
Summary:	Base files for localization
Group:		System/Internationalization
Obsoletes:	locales <= 2.18.90-2
Obsoletes:	locales < 2.19-13
Requires(post,preun):	/bin/sh
Requires(post,preun):	grep
Requires(post,preun):	sed
Requires(post,preun):	coreutils
Requires(post,preun):	util-linux
Requires(post,preun):	glibc
Requires(post,preun):	rpm

%description -n locales
These are the base files for language localization.
You also need to install the specific locales-?? for the
language(s) you want. Then the user need to set the
LANG variable to their preferred language in their
~/.profile configuration file.

# Locale specifc packages
# To look up a language name from a newly appearing code,
# Try http://scriptsource.org/cms/scripts/page.php?item_id=language_detail&key=XXX (where XXX is the new code without country suffix)
%{expand:%(sh %{S:1000} "Afar" "aa" "aa_DJ" "aa_ER" "aa_ET")}
%{expand:%(sh %{S:1000} "Afrikaans" "af" "af_ZA")}
%{expand:%(sh %{S:1000} "Aguaruna" "agr" "agr_PE")}
%{expand:%(sh %{S:1000} "Amharic" "am" "am_ET" "byn_ER" "gez_ER" "gez_ET" "om_ET" "om_KE" "sid_ET" "ti_ER" "ti_ET" "tig_ER" "wal_ET")}
%{expand:%(sh %{S:1000} "Akan" "ak" "ak_GH")}
%{expand:%(sh %{S:1000} "Angika" "anp" "anp_IN")}
%{expand:%(sh %{S:1000} "Arabic" "ar" "ar_AE" "ar_BH" "ar_DZ" "ar_EG" "ar_IN" "ar_IQ" "ar_JO" "ar_KW" "ar_LB" "ar_LY" "ar_MA" "ar_OM" "ar_QA" "ar_SA" "ar_SD" "ar_SS" "ar_SY" "ar_TN" "ar_YE")}
%{expand:%(sh %{S:1000} "Assamese" "as" "as_IN")}
%{expand:%(sh %{S:1000} "Asturian" "ast" "ast_ES")}
%{expand:%(sh %{S:1000} "Aymara" "ayc" "ayc_PE")}
%{expand:%(sh %{S:1000} "Azeri" "az" "az_AZ" "az_IR")}
%{expand:%(sh %{S:1000} "Belarusian" "be" "be_BY")}
%{expand:%(sh %{S:1000} "Bemba" "bem" "bem_ZM")}
%{expand:%(sh %{S:1000} "Berber" "ber" "ber_DZ" "ber_MA")}
%{expand:%(sh %{S:1000} "Bulgarian" "bg" "bg_BG")}
%{expand:%(sh %{S:1000} "Bhili" "bhb" "bhb_IN")}
%{expand:%(sh %{S:1000} "Bhojpuri" "bho" "bho_NP")}
%{expand:%(sh %{S:1000} "Bislama" "bi" "bi_VU")}
%{expand:%(sh %{S:1000} "Bengali" "bn" "bn_BD" "bn_IN")}
%{expand:%(sh %{S:1000} "Tibetan" "bo" "bo_CN" "bo_IN")}
%{expand:%(sh %{S:1000} "Breton" "br" "br_FR")}
%{expand:%(sh %{S:1000} "Bosnian" "bs" "bs_BA")}
%{expand:%(sh %{S:1000} "Catalan" "ca" "ca_AD" "ca_ES" "ca_FR" "ca_IT")}
%{expand:%(sh %{S:1000} "Chechen" "ce" "ce_RU")}
%{expand:%(sh %{S:1000} "Cherokee" "chr" "chr_US")}
%{expand:%(sh %{S:1000} "Crimean Tatar" "crh" "crh_UA")}
%{expand:%(sh %{S:1000} "Czech" "cs" "cs_CZ")}
%{expand:%(sh %{S:1000} "Chuvash" "cv" "cv_RU")}
%{expand:%(sh %{S:1000} "Welsh" "cy" "cy_GB")}
%{expand:%(sh %{S:1000} "Danish" "da" "da_DK")}
%{expand:%(sh %{S:1000} "German" "de" "de_AT" "de_BE" "de_CH" "de_DE" "de_LU" "de_IT" "de_LI")}
%{expand:%(sh %{S:1000} "Dogri" "doi" "doi_IN")}
%{expand:%(sh %{S:1000} "Dhivehi" "dv" "dv_MV")}
%{expand:%(sh %{S:1000} "Dzongkha" "dz" "dz_BT")}
%{expand:%(sh %{S:1000} "Greek" "el" "r:gr" "el_CY" "el_GR")}
%{expand:%(sh %{S:1000} "English" "en" "C" "en_AG" "en_AU" "en_BW" "en_CA" "en_DK" "en_GB" "en_HK" "en_IE" "en_IL" "en_IN" "en_NG" "en_NZ" "en_PH" "en_SC" "en_SG" "en_US" "en_ZA" "en_ZM" "en_ZW")}
%{expand:%(sh %{S:1000} "Esperanto" "eo" "eo" "eo_XX")}
# Potentially unhandled: es@tradicional? an = Aragonese
%{expand:%(sh %{S:1000} "Spanish" "es" "an_ES" "es_AR" "es_BO" "es_CL" "es_CO" "es_CR" "es_CU" "es_DO" "es_EC" "es_ES" "es_GT" "es_HN" "es_MX" "es_NI" "es_PA" "es_PE" "es_PR" "es_PY" "es_SV" "es_US" "es_UY" "es_VE")}
%{expand:%(sh %{S:1000} "Estonian" "et" "et_EE")}
%{expand:%(sh %{S:1000} "Basque" "eu" "eu_ES")}
%{expand:%(sh %{S:1000} "Farsi" "fa" "fa_IR")}
%{expand:%(sh %{S:1000} "Finnish" "fi" "fi_FI")}
%{expand:%(sh %{S:1000} "Fulah" "ff" "ff_SN")}
%{expand:%(sh %{S:1000} "Faroese" "fo" "fo_FO")}
%{expand:%(sh %{S:1000} "French" "fr" "fr_BE" "fr_CA" "fr_CH" "fr_FR" "fr_LU")}
%{expand:%(sh %{S:1000} "Friulan" "fur" "fur_IT")}
%{expand:%(sh %{S:1000} "Frisian" "fy" "fy_DE" "fy_NL")}
%{expand:%(sh %{S:1000} "Irish" "ga" "ga_IE")}
%{expand:%(sh %{S:1000} "Scottish Gaelic" "gd" "gd_GB")}
%{expand:%(sh %{S:1000} "Galician" "gl" "gl_ES")}
%{expand:%(sh %{S:1000} "Gujarati" "gu" "gu_IN")}
%{expand:%(sh %{S:1000} "Manx Gaelic" "gv" "gv_GB")}
%{expand:%(sh %{S:1000} "Hausa" "ha" "ha_NG")}
%{expand:%(sh %{S:1000} "Hebrew" "he" "he_IL" "iw_IL")}
%{expand:%(sh %{S:1000} "Hindi" "hi" "bho_IN" "brx_IN" "hi_IN" "ur_IN")}
%{expand:%(sh %{S:1000} "Fiji Hindi" "hif" "hif_FJ")}
%{expand:%(sh %{S:1000} "Chhattisgarhi" "hne" "hne_IN")}
%{expand:%(sh %{S:1000} "Croatian" "hr" "hr_HR")}
%{expand:%(sh %{S:1000} "Upper Sorbian" "hsb" "hsb_DE")}
%{expand:%(sh %{S:1000} "Lower Sorbian" "dsb" "dsb_DE")}
%{expand:%(sh %{S:1000} "Breyol" "ht" "ht_HT")}
%{expand:%(sh %{S:1000} "Hungarian" "hu" "hu_HU")}
%{expand:%(sh %{S:1000} "Armenian" "hy" "hy_AM")}
%{expand:%(sh %{S:1000} "Interlingua" "ia" "ia_FR")}
%{expand:%(sh %{S:1000} "Indonesian" "id" "id_ID")}
%{expand:%(sh %{S:1000} "Igbo" "ig" "ig_NG")}
%{expand:%(sh %{S:1000} "Inupiaq" "ik" "ik_CA")}
%{expand:%(sh %{S:1000} "Icelandic" "is" "is_IS")}
%{expand:%(sh %{S:1000} "Italian" "it" "it_CH" "it_IT")}
%{expand:%(sh %{S:1000} "Inuktitut" "iu" "iu_CA")}
%{expand:%(sh %{S:1000} "Japanese" "ja" "ja" "ja_JP")}
%{expand:%(sh %{S:1000} "Georgian" "ka" "ka_GE")}
%{expand:%(sh %{S:1000} "Kabyle" "kab" "kab_DZ")}
%{expand:%(sh %{S:1000} "Kazakh" "kk" "kk_KZ")}
%{expand:%(sh %{S:1000} "Sakha" "sah" "sah_RU")}
%{expand:%(sh %{S:1000} "Greenlandic" "kl" "kl_GL")}
%{expand:%(sh %{S:1000} "Khmer" "km" "km_KH")}
%{expand:%(sh %{S:1000} "Kannada" "kn" "kn_IN")}
%{expand:%(sh %{S:1000} "Korean" "ko" "ko_KR")}
%{expand:%(sh %{S:1000} "Konkani" "kok" "kok_IN")}
%{expand:%(sh %{S:1000} "Kashmiri" "ks" "ks_IN")}
%{expand:%(sh %{S:1000} "Kurdish" "ku" "ku_TR")}
%{expand:%(sh %{S:1000} "Cornish" "kw" "kw_GB")}
%{expand:%(sh %{S:1000} "Kyrgyz" "ky" "ky_KG")}
%{expand:%(sh %{S:1000} "Luxembourgish" "lb" "lb_LU")}
%{expand:%(sh %{S:1000} "Luganda" "lg" "lg_UG")}
%{expand:%(sh %{S:1000} "Limburguish" "li" "li_BE" "li_NL")}
%{expand:%(sh %{S:1000} "Ligurian" "lij" "lij_IT")}
%{expand:%(sh %{S:1000} "Lingala" "ln" "ln_CD")}
%{expand:%(sh %{S:1000} "Laotian" "lo" "lo_LA")}
%{expand:%(sh %{S:1000} "Lithuanian" "lt" "lt_LT")}
%{expand:%(sh %{S:1000} "Latvian" "lv" "lv_LV")}
%{expand:%(sh %{S:1000} "Magahi" "mag" "mag_IN")}
%{expand:%(sh %{S:1000} "Maithili" "mai" "mai_IN" "mai_NP")}
%{expand:%(sh %{S:1000} "Mauritian Creole" "mfe" "mfe_MU")}
%{expand:%(sh %{S:1000} "Malagasy" "mg" "mg_MG")}
%{expand:%(sh %{S:1000} "Mari" "mhr" "mhr_RU")}
%{expand:%(sh %{S:1000} "Maori" "mi" "mi_NZ")}
%{expand:%(sh %{S:1000} "Miskito" "miq" "miq_NI")}
%{expand:%(sh %{S:1000} "Karbi" "mjw" "mjw_IN")}
%{expand:%(sh %{S:1000} "Macedonian" "mk" "mk_MK")}
%{expand:%(sh %{S:1000} "Malayalam" "ml" "ml_IN")}
%{expand:%(sh %{S:1000} "Mongolian" "mn" "mn_MN")}
%{expand:%(sh %{S:1000} "Manipuri" "mni" "mni_IN")}
%{expand:%(sh %{S:1000} "Marathi" "mr" "mr_IN")}
%{expand:%(sh %{S:1000} "Malay" "ms" "ms_MY")}
%{expand:%(sh %{S:1000} "Maltese" "mt" "mt_MT")}
%{expand:%(sh %{S:1000} "Burmese" "my" "my_MM")}
%{expand:%(sh %{S:1000} "Lower Saxon" "nds" "nds_DE" "nds_NL")}
%{expand:%(sh %{S:1000} "Nepali" "ne" "ne_NP")}
%{expand:%(sh %{S:1000} "Nahuatl" "nhn" "nhn_MX")}
%{expand:%(sh %{S:1000} "Niuean" "niu" "niu_NU" "niu_NZ")}
%{expand:%(sh %{S:1000} "Dutch" "nl" "nl_AW" "nl_BE" "nl_NL")}
%{expand:%(sh %{S:1000} "Norwegian" "no" "r:nb" "r:nn" "nb_NO" "nn_NO")}
%{expand:%(sh %{S:1000} "Ndebele" "nr" "nr_ZA")}
%{expand:%(sh %{S:1000} "Northern Sotho" "nso" "nso_ZA")}
%{expand:%(sh %{S:1000} "Occitan" "oc" "oc_FR")}
%{expand:%(sh %{S:1000} "Oriya" "or" "or_IN")}
%{expand:%(sh %{S:1000} "Ossetian" "os" "os_RU")}
%{expand:%(sh %{S:1000} "Punjabi" "pa" "pa_IN" "pa_PK")}
%{expand:%(sh %{S:1000} "Papiamento" "pap" "r:pp" "pap_AN" "pap_AW" "pap_CW")}
%{expand:%(sh %{S:1000} "Polish" "pl" "csb_PL" "pl_PL")}
%{expand:%(sh %{S:1000} "Pashto" "ps" "ps_AF")}
%{expand:%(sh %{S:1000} "Portuguese" "pt" "pt_BR" "pt_PT")}
%{expand:%(sh %{S:1000} "Quechua" "quz" "quz_PE")}
%{expand:%(sh %{S:1000} "Rajasthani" "raj" "raj_IN")}
%{expand:%(sh %{S:1000} "Romanian" "ro" "ro_RO")}
%{expand:%(sh %{S:1000} "Russian" "ru" "ru_RU" "ru_UA")}
%{expand:%(sh %{S:1000} "Kinyarwanda" "rw" "rw_RW")}
%{expand:%(sh %{S:1000} "Sanskrit" "sa" "sa_IN")}
%{expand:%(sh %{S:1000} "Santali" "sat" "sat_IN")}
%{expand:%(sh %{S:1000} "Sardinian" "sc" "sc_IT")}
%{expand:%(sh %{S:1000} "Sindhi" "sd" "sd_IN")}
%{expand:%(sh %{S:1000} "Saami" "se" "se_NO")}
%{expand:%(sh %{S:1000} "Samogitian" "sgs" "sgs_LT")}
%{expand:%(sh %{S:1000} "Shan" "shn" "shn_MM")}
%{expand:%(sh %{S:1000} "Secwepemctsin" "shs" "shs_CA")}
%{expand:%(sh %{S:1000} "Sinhala" "si" "si_LK")}
%{expand:%(sh %{S:1000} "Slovak" "sk" "sk_SK")}
%{expand:%(sh %{S:1000} "Slovenian" "sl" "sl_SI")}
%{expand:%(sh %{S:1000} "Samoan" "sm" "sm_WS")}
%{expand:%(sh %{S:1000} "Serbian" "sr" "sr_ME" "sr_RS")}
%{expand:%(sh %{S:1000} "Somali" "so" "so_DJ" "so_ET" "so_KE" "so_SO")}
%{expand:%(sh %{S:1000} "Albanian" "sq" "sq_AL" "sq_MK")}
%{expand:%(sh %{S:1000} "Swati" "ss" "ss_ZA")}
%{expand:%(sh %{S:1000} "Sotho" "st" "st_ZA")}
%{expand:%(sh %{S:1000} "Swedish" "sv" "sv_FI" "sv_SE")}
# sw_XX?
%{expand:%(sh %{S:1000} "Swahili" "sw" "sw_KE" "sw_TZ")}
%{expand:%(sh %{S:1000} "Silesian" "szl" "szl_PL")}
%{expand:%(sh %{S:1000} "Tamil" "ta" "ta_IN" "ta_LK")}
%{expand:%(sh %{S:1000} "Telugu" "te" "te_IN")}
%{expand:%(sh %{S:1000} "Tajik" "tg" "tg_TJ")}
%{expand:%(sh %{S:1000} "Thai" "th" "th_TH")}
%{expand:%(sh %{S:1000} "Tharu/Tharuhati" "the" "the_NP")}
%{expand:%(sh %{S:1000} "Tok Pisin" "tpi" "tpi_PG")}
%{expand:%(sh %{S:1000} "Turkmen" "tk" "tk_TM")}
%{expand:%(sh %{S:1000} "Pilipino" "tl" "r:ph" "fil_PH" "tl_PH")}
%{expand:%(sh %{S:1000} "Tswana" "tn" "tn_ZA")}
%{expand:%(sh %{S:1000} "Tonga" "to" "to_TO")}
%{expand:%(sh %{S:1000} "Turkish" "tr" "tr_CY" "tr_TR")}
%{expand:%(sh %{S:1000} "Tsonga" "ts" "ts_ZA")}
%{expand:%(sh %{S:1000} "Tatar" "tt" "tt_RU")}
%{expand:%(sh %{S:1000} "Tulu" "tcy" "tcy_IN")}
%{expand:%(sh %{S:1000} "Uyghur" "ug" "ug_CN")}
%{expand:%(sh %{S:1000} "Unami" "unm" "unm_US")}
%{expand:%(sh %{S:1000} "Ukrainian" "uk" "uk_UA")}
%{expand:%(sh %{S:1000} "Urdu" "ur" "ur_PK")}
%{expand:%(sh %{S:1000} "Uzbek" "uz" "uz_UZ")}
%{expand:%(sh %{S:1000} "Venda" "ve" "ve_ZA")}
%{expand:%(sh %{S:1000} "Vietnamese" "vi" "vi_VN")}
%{expand:%(sh %{S:1000} "Walloon" "wa" "wa_BE")}
%{expand:%(sh %{S:1000} "Walser" "wae" "wae_CH")}
%{expand:%(sh %{S:1000} "Wolof" "wo" "wo_SN")}
%{expand:%(sh %{S:1000} "Xhosa" "xh" "xh_ZA")}
%{expand:%(sh %{S:1000} "Yiddish" "yi" "yi_US")}
%{expand:%(sh %{S:1000} "Yoruba" "yo" "yo_NG")}
%{expand:%(sh %{S:1000} "Yue Chinese (Cantonese)" "yue" "yue_HK")}
%{expand:%(sh %{S:1000} "Yau" "yuw" "yuw_PG")}
%{expand:%(sh %{S:1000} "Chinese" "zh" "zh_CN" "zh_HK" "zh_SG" "zh_TW" "cmn_TW" "hak_TW" "lzh_TW" "nan_TW")}
%{expand:%(sh %{S:1000} "Zulu" "zu" "zu_ZA")}

%endif

%files -f libc.lang
%if "%{name}" == "glibc"
%if %{with timezone}
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/localtime
%endif
# (tpg) please do not set (noreplace) here as after update system may end up in broken state
%config %{_sysconfdir}/nsswitch.conf
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
%if %isarch %{x86_64}
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
%endif
%if %isarch %{x86_64}
%{_slibdir}/ld-linux-x86-64.so.2
%endif
%if %isarch armv7l armv8l
%{_slibdir}/ld-linux.so.3
%endif
%if %isarch armv7hl armv7hnl armv8hl armv8hnl armv8hcnl armv6j
%{_slibdir}/ld-linux-armhf.so.3
%endif
%if %isarch aarch64
%{_slibdir}/ld-linux-aarch64.so.1
/lib/ld-linux-aarch64.so.1
%endif
%if %isarch %{mips}
%{_slibdir}/ld.so.1
%endif
%if %isarch riscv64
%{_slibdir}/ld-linux-riscv64-lp64d.so.1
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
%if %{build_biarch}
#-----------------------------------------------------------------------
%package -n %{multilibc}
Summary:	The GNU libc libraries
Group:		System/Libraries
Conflicts:	glibc < 2.14.90-13
Requires:	%{name} = %{EVRD}

%transfiletriggerin -p <lua> -- /usr/lib/gconv/
os.execute("/usr/sbin/iconvconfig /usr/lib/gconv -o /usr/lib/gconv/gconv-modules.cache")

%description -n %{multilibc}
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

%files -n %{multilibc}
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
%package devel
Summary:	Header and object files for development using standard C libraries
Group:		Development/C
Requires:	%{name} = %{EVRD}
Requires:	pkgconfig(libxcrypt)
%if %{build_biarch}
Requires:	%{multilibc} = %{EVRD}
%endif
Autoreq:	true
Requires:	%{?cross:cross-}kernel-release-headers >= %{enablekernel}
%if %{with pdf}
%rename		glibc-doc-pdf
%endif

%description devel
The glibc-devel package contains the header and object files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard header and object files available in order to create the
executables.

%package doc
Summary:	Docs for %{name}
Group:		Development/C
BuildArch:	noarch

%description doc
The glibc-docs package contains docs for %{name}.

%files doc
%doc %{_docdir}/glibc/*
%exclude %{_docdir}/glibc/nss
%exclude %{_docdir}/glibc/gai.conf
%exclude %{_docdir}/glibc/COPYING
%exclude %{_docdir}/glibc/COPYING.LIB

%files devel
%if "%{name}" == "glibc"
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
%{_libdir}/libmcheck.a
%optional %{_libdir}/libmvec.a
%if %{build_biarch}
%{_libdir32}/*.o
%{_libdir32}/*.so
%{_libdir32}/libc_nonshared.a
%{_libdir32}/libg.a
%{_libdir32}/libmcheck.a
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
%{_libdirn32}/libmcheck.a
%exclude %{_slibdir}/ld*-[.0-9]*.so
%exclude %{_slibdir}/lib*-[.0-9]*.so
%exclude %{_slibdir}/libSegFault.so
%endif
%endif

#-----------------------------------------------------------------------
%package static-devel
Summary:	Static libraries for GNU C library
Group:		Development/C
Requires:	%{name}-devel = %{EVRD}
Requires:	%{_lib}crypt-static-devel >= 4.4.3

%description static-devel
The glibc-static-devel package contains the static libraries necessary
for developing programs which use the standard C libraries. Install
glibc-static-devel if you need to statically link your program or
library.

%files static-devel
%{_libdir}/libBrokenLocale.a
%{_libdir}/libanl.a
%{_libdir}/libc.a
%{_libdir}/libdl.a
%{_libdir}/libm.a
# Versioned libm.a seems to be generated only on x86_64
%optional %{_libdir}/libm-%{version}.a
%{_libdir}/libpthread.a
%{_libdir}/libresolv.a
%{_libdir}/librt.a
%{_libdir}/libutil.a
%if %{build_biarch}
%{_libdir32}/libBrokenLocale.a
%{_libdir32}/libanl.a
%{_libdir32}/libc.a
%{_libdir32}/libdl.a
%{_libdir32}/libm.a
%{_libdir32}/libpthread.a
%{_libdir32}/libresolv.a
%{_libdir32}/librt.a
%{_libdir32}/libutil.a
%if %isarch mips mipsel
%{_libdirn32}/libBrokenLocale.a
%{_libdirn32}/libanl.a
%{_libdirn32}/libc.a
%{_libdirn32}/libdl.a
%{_libdirn32}/libm.a
%{_libdirn32}/libpthread.a
%{_libdirn32}/libresolv.a
%{_libdirn32}/librt.a
%{_libdirn32}/libutil.a
%endif
%endif

########################################################################
%if %{with nscd}
#-----------------------------------------------------------------------
%package -n nscd
Summary:	A Name Service Caching Daemon (nscd)
Group:		System/Servers
Conflicts:	kernel < 2.2.0
BuildRequires:	systemd-macros
BuildRequires:	rpm-helper
Requires(post):	systemd
Requires(pre):	shadow

%description -n nscd
Nscd caches name service lookups and can dramatically improve
performance with NIS+, and may help with DNS as well.

%pre -n nscd -p <lua>
user = os.execute("/usr/bin/getent passwd nscd >/dev/null 2>&1")
if user ~= 0 then
    os.execute("/usr/sbin/useradd -r -M -U -s /sbin/nologin -d / -c 'system user for nscd' nscd >/dev/null 2>&1")
end

%post -n nscd -p <lua>
os.execute("/usr/sbin/nscd -i passwd -i group >/dev/null 2>&1")
os.execute("/bin/systemctl preset --now nscd.socket >/dev/null 2>&1")
os.execute("/bin/systemctl preset --now nscd.service >/dev/null 2>&1")

%files -n nscd
%config(noreplace) %{_sysconfdir}/nscd.conf
%dir %attr(0755,root,root) /run/nscd
%dir %attr(0755,root,root) %{_var}/db/nscd
%dir %attr(0755,root,root) %{_sysconfdir}/netgroup
%{_presetdir}/86-nscd.preset
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
%package utils
Summary:	Development utilities from GNU C library
Group:		Development/Other
Requires:	%{name} = %{EVRD}

%description utils
The glibc-utils package contains memusage, a memory usage profiler,
mtrace, a memory leak tracer and xtrace, a function call tracer which
can be helpful during program debugging.

If unsure if you need this, don't install this package.

%files utils
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
%package i18ndata
Summary:	Database sources for 'locale'
Group:		System/Libraries
%rename		glibc-localedata

%description i18ndata
This package contains the data needed to build the locale data files
to use the internationalization features of the GNU libc.

%files i18ndata
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
%package -n timezone
Summary:	Time zone descriptions
Group:		System/Base
Obsoletes:	zoneinfo

%description -n timezone
These are configuration files that describe possible time zones.

%files -n timezone
%{_sbindir}/zdump
%{_sbindir}/zic
%{_mandir}/man1/zdump.1*
%{_datadir}/zoneinfo
#-----------------------------------------------------------------------
# with timezone
%endif

%if %{with crosscompilers}
%global kernelver %(rpm -q --qf '%%{version}-%%{release}%%{disttag}' kernel-release-source-latest)
%(
for i in %{long_targets}; do
	[ "$i" = "%{_target_platform}" ] && continue
	package=cross-${i}-libc
	cat <<EOF
%package -n ${package}
Summary: Libc for crosscompiling to ${i}
Group: Development/Other
BuildRequires: cross-${i}-binutils cross-${i}-gcc-bootstrap cross-${i}-kernel-release-headers
BuildRequires: kernel-release-source-latest
Recommends: cross-${i}-binutils cross-${i}-gcc
%description -n ${package}
Libc for crosscompiling to ${i}

%files -n ${package}
%{_prefix}/${i}/include/*
%{_prefix}/${i}/lib*/*
EOF
done
)
%endif

%prep
%setup -q -n %{source_dir} -a3
%autopatch -p1

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
mkdir -p bin
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
  # -Wall is just added to get conditionally %%optflags printed...
  # cut -flto flag
  BuildFlags="$(rpm --target ${arch}-%{_target_os} -D '%__common_cflags_with_ssp -Wall' -E %%{optflags} | sed -e 's# -fPIC##g' -e 's#-m64##' -e 's#-gdwarf-4##;s#-g##' -e 's#-flto##' -e 's#-O[s2]#-O3#')"

  case $arch in
    i[3-6]86)
%ifarch %{x86_64}
%ifarch znver1
	BuildFlags="$BuildFlags -march=znver1 -mtune=znver1"
%else
	BuildFlags="$BuildFlags -march=x86-64 -mtune=generic"
%endif
	BuildAltArch="yes"
	BuildCompFlags="-m32"
%endif
%ifarch %{ix86}
	BuildFlags="$BuildFlags -march=i686 -msse -mfpmath=sse -fasynchronous-unwind-tables -mtune=generic"
%endif
      ;;
    znver1)
      BuildFlags="$BuildFlags -march=znver1 -mtune=znver1"
      ;;
    x86_64)
      BuildFlags="$BuildFlags -march=x86-64 -mtune=generic"
      ;;
    mips|mipsel)
      BuildCompFlags="$BuildFlags"
      ;;
    mips32|mips32el)
      BuildFlags="$BuildFlags -march=mips3 -mabi=n32"
      BuildCompFlags="$BuildFlags -march=mips3 -mabi=n32"
      ;;
    mips64|mips64el)
      BuildFlags="$BuildFlags -march=mips3 -mabi=64"
      BuildCompFlags="$BuildFlags -march=mips3 -mabi=64"
      ;;
    armv5t*)
      BuildFlags="$BuildFlags -march=armv5t"
      BuildCompFlags="$BuildFlags -march=armv5t"
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
    i686|x86_64|znver1)
      MultiArchFlags="--enable-multi-arch"
      ;;
  esac

  # Determine C & C++ compilers
  BuildCC="gcc -fuse-ld=bfd $BuildCompFlags"
  BuildCXX="g++ -fuse-ld=bfd $BuildCompFlags"

  # Are we supposed to cross-compile?
  if [ "%{target_cpu}" != "%{_target_cpu}" ]; then
    # Can't use BuildCC anymore with previous changes.
    BuildCC="%{cross_program_prefix}gcc $BuildCompFlags"
    BuildCXX="%{cross_program_prefix}g++ $BuildCompFlags"
    BuildCross="--build=%{_target_platform}"
    export libc_cv_forced_unwind=yes libc_cv_c_cleanup=yes
  fi

# set some extra flags here
# (tpg) build with -O3

  BuildFlags="$BuildFlags -Wp,-D_GLIBCXX_ASSERTIONS -DNDEBUG=1 -fasynchronous-unwind-tables -fstack-clash-protection -funwind-tables %(echo %{__common_cflags_with_ssp} |sed -e 's#-O[s2]#-O3#g')"
  %if "%{distepoch}" >= "2015.0"
  BuildFlags="$BuildFlags -fno-lto"
  %endif

  if [ "$arch" = 'i586' ] || [ "$arch" = 'i686' ]; then
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
%if %{with systap}
   if [ "$BuildAltArch" = 'no' ]; then
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
  LIBDIR=$(rpm --macros %{_usrlibrpm}/macros:%{_usrlibrpm}/platform/${arch}-%{_target_os}/macros --target=${arch} -E %%{_libdir})
  SLIBDIR=/${LIB}

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
  cd  build-$arch-linux
  [ "$BuildAltArch" = 'yes' ] && touch ".alt" || touch ".main"
  export libc_cv_slibdir=${SLIBDIR}
  case $arch in
  znver1)
    configarch=x86_64
    ;;
  *)
    configarch=$arch
    ;;
  esac
  CC="$BuildCC" CXX="$BuildCXX" CFLAGS="$BuildFlags -Wno-error" ARFLAGS="$ARFLAGS --generate-missing-build-notes=yes" LDFLAGS="%{ldflags} -fuse-ld=bfd" ../configure \
    --target=$configarch-%{platform} \
    --host=$configarch-%{platform} \
    $BuildCross \
    --prefix=%{_prefix} \
    --libexecdir=%{_prefix}/libexec \
    --libdir=${LIBDIR} \
    --infodir=%{_infodir} \
    --localedir=%{_localedir} \
    --enable-add-ons=$AddOns \
    --disable-profile \
    --enable-static \
    --disable-nss-crypt \
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
    --enable-tunables \
    --enable-stack-protector=strong \
    $ExtraFlags \
    $MultiArchFlags \
    --enable-kernel=%{enablekernel} \
    --with-headers=$KernelHeaders ${1+"$@"} \
    --with-bugurl=%{bugurl}

  # FIXME use %%make if the Makefiles ever get fixed for parallel build
  %make_build -j1 -r all subdir_stubs
  cd -

  check_flags="-k"

  # Generate test matrix
  [ -d "build-$arch-linux" ] || {
    echo "ERROR: PrepareGlibcTest: build-$arch-linux does not exist!"
    return 1
  }
  local BuildJobs="%{_smp_mflags}"
  echo "$BuildJobs -d build-$arch-linux $check_flags" >> %{checklist}

  case $arch in
  i[56]86)	base_arch=i686;;
  *)		base_arch=none;;
  esac

  [ -d "build-$base_arch-linux" ] && {
    check_flags="$check_flags -l build-$base_arch-linux/elf/ld.so"
    echo "$BuildJobs -d build-$arch-linux $check_flags" >> %{checklist}
  }
  return 0
}

%if %{with crosscompilers}
for i in %{targets}; do
        CPU=$(echo $i |cut -d- -f1)
        OS=$(echo $i |cut -d- -f2)
        TRIPLET="$(rpm --target=${CPU}-${OS} -E %%{_target_platform})"
	if [ "${TRIPLET}" = "%{_target_platform}" ]; then
		echo "===== Skipping $i cross libc (native arch) ====="
		continue
	fi
	echo "===== Building %{_target_platform} -> $i ($TRIPLET) cross libc ====="
	KARCH=$(echo $TRIPLET |cut -d- -f1)
	case $KARCH in
	aarch64)
		KARCH=arm64
		;;
	arm*)
		KARCH=arm
		;;
	i.86)
		KARCH=x86
		;;
	esac
	mkdir -p obj-${TRIPLET}
	cd obj-${TRIPLET}
	CFLAGS="$(rpm --target ${i} --eval '%%{optflags} -fuse-ld=bfd -fno-strict-aliasing -Wno-error' |sed -e 's,-flto,,g;s,-Werror[^ ]*,,g')" \
	CXXFLAGS="$(rpm --target ${i} --eval '%%{optflags} -fuse-ld=bfd -fno-strict-aliasing -Wno-error' |sed -e 's,-flto,,g;s,-Werror[^ ]*,,g')" \
	ASFLAGS="$(rpm --target ${i} --eval '%%{optflags} -fuse-ld=bfd -fno-strict-aliasing -Wno-error' |sed -e 's,-flto,,g;s,-Werror[^ ]*,,g')" \
	LDFLAGS="$(rpm --target ${i} --eval '%%{ldflags} -fuse-ld=bfd -fno-strict-aliasing -Wno-error' |sed -e 's,-flto,,g')" \
	CC="${TRIPLET}-gcc ${CFLAGS}" \
	../configure \
		--prefix=%{_prefix}/${TRIPLET} \
		--host=${TRIPLET} \
		--target=${TRIPLET} \
    		--with-gnu-ld=${TRIPLET}-ld.bfd \
		--with-headers=%{_prefix}/${TRIPLET}/include
	%make_build
	cd ..
done
%endif

# Build main glibc
BuildGlibc %{target_cpu}

%if %{build_biarch}
    %if %isarch %{x86_64}
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

# post install wrapper
gcc -static -Lbuild-%{target_cpu}-linux %{optflags} -Os %{SOURCE2} -o build-%{target_cpu}-linux/glibc_post_upgrade \
  '-DLIBTLS="/%{_lib}/tls/"' \
  '-DGCONV_MODULES_DIR="%{_libdir}/gconv"' \
  '-DLD_SO_CONF="/etc/ld.so.conf"' \
  '-DICONVCONFIG="%{_sbindir}/iconvconfig"'
%endif

#-----------------------------------------------------------------------

%if "%{target_cpu}" != "i686"
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

%if %{with crosscompilers}
for i in %{long_targets}; do
	if [ "${i}" = "%{_target_platform}" ]; then
		echo "===== Skipping $i cross libc (native arch)"
		continue
	fi
	echo "===== Installing %{_target_platform} -> $i cross libc ====="
	cd obj-${i}
	%make_install
	cd ..
	# We don't need all the bits and pieces with a crosscompiler
	rm -rf %{buildroot}%{_prefix}/$i/bin %{buildroot}%{_prefix}/$i/sbin %{buildroot}%{_prefix}/$i/var %{buildroot}%{_prefix}/$i/share %{buildroot}%{_prefix}/$i/etc
done
%endif

make install_root=%{buildroot} install -C build-%{target_cpu}-linux

%if %{build_biarch} || %isarch %{mips} %{mipsel}
    %if %isarch %{x86_64}
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
		install

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
	mv     %{buildroot}/$ALT_ARCH/$LIB %{buildroot}/$LIB
	mv     %{buildroot}/$ALT_ARCH%{_libexecdir}/getconf/* %{buildroot}%{_prefix}/libexec/getconf/
	[ ! -d %{buildroot}%{_prefix}/$LIB/ ] && mkdir -p %{buildroot}%{_prefix}/$LIB/
	mv     %{buildroot}/$ALT_ARCH%{_prefix}/$LIB/* %{buildroot}%{_prefix}/$LIB/

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

  [ -z "$LibDir" ] && LibDir="%{_slibdir}"

  cd $BuildDir
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
  cd -

}

# Install arch-specific optimized libraries
%if %isarch %{i586}
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

install -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/nsswitch.conf

# This is for nscd - in glibc 2.2
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
    install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-nscd.preset << EOF
enable nscd.socket
enable nscd.service
EOF
%endif

# Include ld.so.conf
%if "%{name}" == "glibc"
%if %isarch mips mipsel
# needed to get a ldd which understands o32, n32, 64
install -m755 build-%{_target_cpu}-linux/elf/ldd %{buildroot}%{_bindir}/ldd
%endif

# ldconfig cache
mkdir -p %{buildroot}%{_var}/cache/ldconfig
truncate -s 0 %{buildroot}%{_var}/cache/ldconfig/aux-cache
# Note: This has to happen before creating /etc/ld.so.conf.
# ldconfig is statically linked, so we can use the new version.
%{buildroot}/sbin/ldconfig -N -r %{buildroot}

echo "include /etc/ld.so.conf.d/*.conf" > %{buildroot}%{_sysconfdir}/ld.so.conf
chmod 644 %{buildroot}%{_sysconfdir}/ld.so.conf
mkdir -p  %{buildroot}%{_sysconfdir}/ld.so.conf.d

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
if [ "%{_target_cpu}" != "%{target_cpu}" ]; then
  Strip="%{cross_program_prefix}$Strip"
fi

# Strip debugging info from all static libraries
cd %{buildroot}%{_slibdir}
for i in *.a; do
  if [ -f "$i" ]; then
    case "$i" in
    *_p.a) ;;
    *) $Strip -g -R .comment -R .GCC.command.line         $i ;;
    esac
  fi
done
cd -

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
    cd build-%{target_cpu}-linux
%if %{with doc}
	make html
	cp -fpar manual/libc %{buildroot}%{_docdir}/glibc/html
%endif
%if %{with pdf}
	make pdf
	install -m644 -D manual/libc.pdf %{buildroot}%{_docdir}/glibc/libc.pdf
%endif
    cd -
install -m 644 COPYING COPYING.LIB README NEWS INSTALL 			\
    hesiod/README.hesiod						\
    ChangeLog nis/nss posix/gai.conf		\
    %{buildroot}%{_docdir}/glibc
xz -0 --text -T0 %{buildroot}%{_docdir}/glibc/ChangeLog
install -m 644 timezone/README %{buildroot}%{_docdir}/glibc/README.timezone

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
%global glibcver %(rpm -q --qf "%%{VERSION}" glibc)
export I18NPATH=%{buildroot}%{_datadir}/i18n

# make default charset pseudo-locales
# those will be symlinked (for LC_CTYPE, LC_COLLATE mainly) from
# a lot of other locales, thus saving space
for DEF_CHARSET in UTF-8 ISO-8859-1 ISO-8859-2 ISO-8859-3 ISO-8859-4 \
	ISO-8859-5 ISO-8859-7 ISO-8859-9 \
	ISO-8859-13 ISO-8859-14 ISO-8859-15 KOI8-R KOI8-U CP1251
do
	# don't use en_DK because of LC_MONETARY
	%{buildroot}%{_bindir}/localedef -c -f $DEF_CHARSET -i en_US %{buildroot}%{_datadir}/locale/$DEF_CHARSET
done

# Build regular locales
LANGS="$(sed '1,/^SUPPORTED-LOCALES=/d;s,\\$,,;s,\n,,' %{buildroot}%{_datadir}/i18n/SUPPORTED)"
for l in $LANGS; do
	LNG=$(echo $l |cut -d/ -f1)
	CS=$(echo $l |cut -d/ -f2)
	%{buildroot}%{_bindir}/localedef -i "$(echo $LNG |sed 's/\([^.]*\)[^@]*\(.*\)/\1\2/')" -c -f $CS %{buildroot}%{_datadir}/locale/$LNG
done

# Locale related tools
install -c -m 755 %{SOURCE1001} %{SOURCE1002} %{buildroot}%{_bindir}/
# And configs
install -c -m 644 %{SOURCE1003} -D %{buildroot}%{_sysconfdir}/sysconfig/locales

# Hardlink identical locales
%{_sbindir}/hardlink -vvc %{buildroot}%{_datadir}/locale

# Symlink identical files
# TODO

# Needed for/used by locale-archive
mkdir -p %{buildroot}%{_prefix}/lib/locale
touch %{buildroot}%{_prefix}/lib/locale/locale-archive
%endif

# Remove stuff we get from libxcrypt
rm -f %{buildroot}%{_prefix}/*/libcrypt.a %{buildroot}%{_includedir}/crypt.h %{buildroot}/*/libcrypt* %{buildroot}%{_prefix}/*/libcrypt.a
# remove broken symlink
rm -f %{buildroot}%{_prefix}/lib/libcrypt.so

%ifarch %{aarch64}
# Compat symlink -- some versions of ld hardcoded /lib/ld-linux-aarch64.so.1
# as dynamic loader
ln -s %{_slibdir}/ld-linux-aarch64.so.1 %{buildroot}/lib/ld-linux-aarch64.so.1
%endif

%ifarch riscv64
# RISC-V ABI wants to install everything in /lib64/lp64d or /usr/lib64/lp64d.
# Make these be symlinks to /lib64 or /usr/lib64 respectively.  See:
# https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/thread/DRHT5YTPK4WWVGL3GIN5BF2IKX2ODHZ3/
for d in %{buildroot}%{_libdir} %{buildroot}/%{_lib}; do
        mkdir -p $d
        (cd $d && ln -sf . lp64d)
done
%endif

%ifarch %{x86_64}
# Needed for bootstrapping x32 compilers
[ -e %{buildroot}%{_includedir}/gnu/stubs-x32.h ] || cp %{buildroot}%{_includedir}/gnu/stubs-64.h %{buildroot}%{_includedir}/gnu/stubs-x32.h
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
