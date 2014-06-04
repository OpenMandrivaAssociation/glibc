%define	checklist	%{_builddir}/%{name}-%{version}/Check.list

# crypt blowfish support
%define crypt_bf_ver	1.2

%define _libdir32	%{_prefix}/lib

%define	oname		glibc
%define	major		6
%define	source_dir	%{oname}-%{version}
%define	libc		%mklibname c %{major}
%define	devname		%mklibname -d c
%define	statname	%mklibname -d -s c
%define	multilibc	libc%{major}

%define	_disable_ld_no_undefined	1
%undefine _fortify_cflags


# Define "cross" to an architecture to which glibc is to be
# cross-compiled
%define build_cross		0
%{expand: %{?cross:		%%global build_cross 1}}

%if %{build_cross}
%define	_srcrpmfilename	%{oname}-%{version}-%{release}.src.rpm
%define	_build_pkgcheck_set /usr/bin/rpmlint -T -f %{_sourcedir}/%{oname}.rpmlintrc
%define	_build_pkgcheck_srpm /usr/bin/rpmlint -T -f %{_sourcedir}/%{oname}.rpmlintrc
%define target_cpu	%{cross}
%define cross_prefix	cross-%{target_cpu}-
%define _prefix		/usr/%{target_cpu}-%{_target_vendor}-%{_target_os}%{gnuext}
%define cross_program_prefix	%{target_cpu}-%{_target_vendor}-%{_target_os}%{gnuext}-
%define _exec_prefix	%{_prefix}
# brain damage alert: should not be needed imho
# overriding _prefix and _exec_prefix should be enough
%define _bindir		%{_exec_prefix}/bin
%define _sbindir	%{_exec_prefix}/sbin
%define _libexecdir	%{_exec_prefix}/libexec
%define _datadir	%{_prefix}/share
%define _sharedstatedir	%{_prefix}/com
%define _localstatedir	%{_prefix}/var
%define _lib		lib
%define _libdir		%{_exec_prefix}/%{_lib}
%define _slibdir	%{_exec_prefix}/%{_lib}
%define _slibdir32	%{_exec_prefix}/lib
%define _includedir	%{_prefix}/include
%else
%define gnuext		%{?_gnu}
%define target_cpu	%{_target_cpu}
%define cross_prefix	%{nil}
%define cross_program_prefix	%{nil}
%define _slibdir	/%{_lib}
%define _slibdir32	/lib
%endif

# Define target (base) architecture
%define arch		%(echo %{target_cpu}|sed -e "s/\\(i.86\\|athlon\\)/i386/" -e "s/amd64/x86_64/")
%define isarch()	%(case " %* " in (*" %{arch} "*) echo 1;; (*) echo 0;; esac)

%if %{build_cross}
%if %isarch %arm
%define gnuext          -gnueabi
%else
%define gnuext          %{?_gnu}
%endif
%endif

# Define Xen arches to build with -mno-tls-direct-seg-refs
%define xenarches	%{ix86}

# Define to build nscd with selinux support
%bcond_with selinux

# Allow make check to fail only when running kernels where we know
# tests must pass (no missing features or bugs in the kernel)
%define check_min_kver 2.6.21

# Define to build a biarch package
%define build_biarch	0
%if %isarch x86_64 mips64 mips64el
%define build_biarch	1
%endif

%bcond_without nscd
%bcond_without i18ndata
%bcond_with timezone
%bcond_without nsscrypt
%bcond_with locales


%if %isarch %{ix86} x86_64
%bcond_without systap
%else
%bcond_with systap
%endif

# build documentation by default
%bcond_without		doc
%bcond_with		pdf
# enable utils by default
%bcond_without		utils


# Disable a few defaults when cross-compiling a glibc
%if %{build_cross}
%unglobal	with_doc
%unglobal	with_pdf
%unglobal	with_nscd
%unglobal	with_timezone
%unglobal	with_i18ndata
%unglobal	with_locales
%unglobal	with_systap
%unglobal	with_utils
%unglobal	with_nsscrypt
%endif

#-----------------------------------------------------------------------
Summary:	The GNU libc libraries
Name:		%{cross_prefix}%{oname}
Epoch:		6
Version:	2.19
Release:	6
Source0:	http://ftp.gnu.org/gnu/glibc/%{oname}-%{version}.tar.xz
Source1:	http://ftp.gnu.org/gnu/glibc/%{oname}-%{version}.tar.xz.sig
License:	LGPLv2+ and LGPLv2+ with exceptions and GPLv2+
Group:		System/Libraries
Url:		http://www.eglibc.org/

# From Fedora
Source2:	glibc_post_upgrade.c
Source3:	glibc-manpages.tar.bz2
Source5:	glibc-check.sh
Source6:	nscd.service
Source7:	nscd.socket
Source10:	libc-lock.h

# Locales
Source20:	Makefile.locales

# Blowfish support
Source50:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz
Source51:	http://www.openwall.com/crypt/crypt_blowfish-%{crypt_bf_ver}.tar.gz.sign
Source52:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.c
Source53:	http://cvsweb.openwall.com/cgi/cvsweb.cgi/~checkout~/Owl/packages/glibc/crypt_freesec.h

Source100:	%{oname}.rpmlintrc

Source1000:	locale-pkg
Source1001:	locale_install.sh
Source1002:	locale_uninstall.sh
Source1003:	locales.sysconfig
Source1004:	locales-hardlink.pl
Source1005:	locales-softlink.pl

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
Patch89:	glibc-2.19-nscd-socket-and-pid-moved-from-varrun-to-run.patch
# Crypt-blowfish patches
Patch100:	crypt_blowfish-arm.patch

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
# we'll be the only package requiring this, avoiding any other package
# dependencies on '/bin/sh' or 'bash'
Requires:	bash
Requires:	filesystem
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
%define		enablekernel 2.6.32
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
Provides:	/sbin/ldconfig
Obsoletes:	nss_db
%endif

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.

%if "%{name}" == glibc
%post -p %{_sbindir}/glibc_post_upgrade
%endif

%if %{with locales}
%package -n locales
Summary:	Base files for localization
Group:		System/Internationalization

%description -n locales
These are the base files for language localization.
You also need to install the specific locales-?? for the
language(s) you want. Then the user need to set the
LANG variable to their preferred language in their
~/.profile configuration file.

# Locale specifc packages
%{expand:%(sh %{SOURCE1000} Afar aa aa_DJ aa_ER aa_ET)}
%{expand:%(sh %{SOURCE1000} Afrikaans af af_ZA)}
%{expand:%(sh %{SOURCE1000} Amharic am am_ET byn_ER gez_ER gez_ET om_ET om_KE sid_ET ti_ER ti_ET tig_ER wal_ET)}
%{expand:%(sh %{SOURCE1000} Akan ak ak_GH)}
%{expand:%(sh %{SOURCE1000} Angika anp anp_IN)}
%{expand:%(sh %{SOURCE1000} Arabic ar ar_AE ar_BH ar_DZ ar_EG ar_IN ar_IQ ar_JO ar_KW ar_LB ar_LY ar_MA ar_OM ar_QA ar_SA ar_SD ar_SS ar_SY ar_TN ar_YE)}
%{expand:%(sh %{SOURCE1000} Assamese as as_IN)}
%{expand:%(sh %{SOURCE1000} Asturian ast ast_ES)}
%{expand:%(sh %{SOURCE1000} Aymara ayc ayc_PE)}
%{expand:%(sh %{SOURCE1000} Azeri az az_AZ)}
%{expand:%(sh %{SOURCE1000} Belarusian be be_BY)}
%{expand:%(sh %{SOURCE1000} Bemba bem bem_ZM)}
%{expand:%(sh %{SOURCE1000} Berber ber ber_DZ ber_MA)}
%{expand:%(sh %{SOURCE1000} Bulgarian bg bg_BG)}
%{expand:%(sh %{SOURCE1000} Bengali bn bn_BD bn_IN)}
%{expand:%(sh %{SOURCE1000} Tibetan bo bo_CN bo_IN)}
%{expand:%(sh %{SOURCE1000} Breton br br_FR)}
%{expand:%(sh %{SOURCE1000} Bosnian bs bs_BA)}
%{expand:%(sh %{SOURCE1000} Catalan ca ca_AD ca_ES ca_FR ca_IT)}
%{expand:%(sh %{SOURCE1000} "Crimean Tatar" crh crh_UA)}
%{expand:%(sh %{SOURCE1000} Czech cs cs_CZ)}
%{expand:%(sh %{SOURCE1000} Chuvash cv cv_RU)}
%{expand:%(sh %{SOURCE1000} Welsh cy cy_GB)}
%{expand:%(sh %{SOURCE1000} Danish da da_DK)}
%{expand:%(sh %{SOURCE1000} German de de_AT de_BE de_CH de_DE de_LU)}
%{expand:%(sh %{SOURCE1000} Dogri doi doi_IN)}
%{expand:%(sh %{SOURCE1000} Dhivehi dv dv_MV)}
%{expand:%(sh %{SOURCE1000} Dzongkha dz dz_BT)}
%{expand:%(sh %{SOURCE1000} Greek el r:gr el_CY el_GR)}
%{expand:%(sh %{SOURCE1000} English en en_AG en_AU en_BW en_CA en_DK en_GB en_HK en_IE en_IN en_NG en_NZ en_PH en_SG en_US en_ZA en_ZM en_ZW)}
%{expand:%(sh %{SOURCE1000} Esperanto eo eo_XX)}
# Potentially unhandled: es@tradicional?, an = Aragonese
%{expand:%(sh %{SOURCE1000} Spanish es an_ES es_AR es_BO es_CL es_CO es_CR es_CU es_DO es_EC es_ES es_GT es_HN es_MX es_NI es_PA es_PE es_PR es_PY es_SV es_US es_UY es_VE)}
%{expand:%(sh %{SOURCE1000} Estonian et et_EE)}
%{expand:%(sh %{SOURCE1000} Basque eu eu_ES)}
%{expand:%(sh %{SOURCE1000} Farsi fa fa_IR)}
%{expand:%(sh %{SOURCE1000} Finnish fi fi_FI)}
%{expand:%(sh %{SOURCE1000} Fulah ff ff_SN)}
%{expand:%(sh %{SOURCE1000} Faroese fo fo_FO)}
%{expand:%(sh %{SOURCE1000} French fr fr_BE fr_CA fr_CH fr_FR fr_LU)}
%{expand:%(sh %{SOURCE1000} Friulan fur fur_IT)}
%{expand:%(sh %{SOURCE1000} Frisian fy fy_DE fy_NL)}
%{expand:%(sh %{SOURCE1000} Irish ga ga_IE)}
%{expand:%(sh %{SOURCE1000} "Scottish Gaelic" gd gd_GB)}
%{expand:%(sh %{SOURCE1000} Galician gl gl_ES)}
%{expand:%(sh %{SOURCE1000} Gujarati gu gu_IN)}
%{expand:%(sh %{SOURCE1000} "Manx Gaelic" gv gv_GB)}
%{expand:%(sh %{SOURCE1000} Hausa ha ha_NG)}
%{expand:%(sh %{SOURCE1000} Hebrew he he_IL iw_IL)}
%{expand:%(sh %{SOURCE1000} Hindi hi bho_IN brx_IN hi_IN ur_IN)}
%{expand:%(sh %{SOURCE1000} Chhattisgarhi hne hne_IN)}
%{expand:%(sh %{SOURCE1000} Croatian hr hr_HR)}
%{expand:%(sh %{SOURCE1000} "Upper Sorbian" hsb hsb_DE)}
%{expand:%(sh %{SOURCE1000} Breyol ht ht_HT)}
%{expand:%(sh %{SOURCE1000} Hungarian hu hu_HU)}
%{expand:%(sh %{SOURCE1000} Armenian hy hy_AM)}
%{expand:%(sh %{SOURCE1000} Interlingua ia ia_FR)}
%{expand:%(sh %{SOURCE1000} Indonesian id id_ID)}
%{expand:%(sh %{SOURCE1000} Igbo ig ig_NG)}
%{expand:%(sh %{SOURCE1000} Inupiaq ik ik_CA)}
%{expand:%(sh %{SOURCE1000} Icelandic is is_IS)}
%{expand:%(sh %{SOURCE1000} Italian it it_CH it_IT)}
%{expand:%(sh %{SOURCE1000} Inuktitut iu iu_CA)}
%{expand:%(sh %{SOURCE1000} Japanese ja ja ja_JP)}
%{expand:%(sh %{SOURCE1000} Georgian ka ka_GE)}
%{expand:%(sh %{SOURCE1000} Kazakh kk kk_KZ)}
%{expand:%(sh %{SOURCE1000} Greenlandic kl kl_GL)}
%{expand:%(sh %{SOURCE1000} Khmer km km_KH)}
%{expand:%(sh %{SOURCE1000} Kannada kn kn_IN)}
%{expand:%(sh %{SOURCE1000} Korean ko ko_KR)}
%{expand:%(sh %{SOURCE1000} Konkani kok kok_IN)}
%{expand:%(sh %{SOURCE1000} Kashmiri ks ks_IN ks_IN@devanagari)}
%{expand:%(sh %{SOURCE1000} Kurdish ku ku_TR)}
%{expand:%(sh %{SOURCE1000} Cornish kw kw_GB)}
%{expand:%(sh %{SOURCE1000} Kyrgyz ky ky_KG)}
%{expand:%(sh %{SOURCE1000} Luxembourgish lb lb_LU)}
%{expand:%(sh %{SOURCE1000} Luganda lg lg_UG)}
%{expand:%(sh %{SOURCE1000} Limburguish li li_BE li_NL)}
%{expand:%(sh %{SOURCE1000} Ligurian lij lij_IT)}
%{expand:%(sh %{SOURCE1000} Laotian lo lo_LA)}
%{expand:%(sh %{SOURCE1000} Lithuanian lt lt_LT)}
%{expand:%(sh %{SOURCE1000} Latvian lv lv_LV)}
%{expand:%(sh %{SOURCE1000} Magahi mag mag_IN)}
%{expand:%(sh %{SOURCE1000} Maithili mai mai_IN)}
%{expand:%(sh %{SOURCE1000} Malagasy mg mg_MG)}
%{expand:%(sh %{SOURCE1000} Mari mhr mhr_RU)}
%{expand:%(sh %{SOURCE1000} Maori mi mi_NZ)}
%{expand:%(sh %{SOURCE1000} Macedonian mk mk_MK)}
%{expand:%(sh %{SOURCE1000} Malayalam ml ml_IN)}
%{expand:%(sh %{SOURCE1000} Mongolian mn mn_MN)}
%{expand:%(sh %{SOURCE1000} Manipuri mni mni_IN)}
%{expand:%(sh %{SOURCE1000} Marathi mr mr_IN)}
%{expand:%(sh %{SOURCE1000} Malay ms ms_MY)}
%{expand:%(sh %{SOURCE1000} Maltese mt mt_MT)}
%{expand:%(sh %{SOURCE1000} Burmese my my_MM)}
%{expand:%(sh %{SOURCE1000} "Lower Saxon" nds nds_DE nds_NL)}
%{expand:%(sh %{SOURCE1000} Nepali ne ne_NP)}
%{expand:%(sh %{SOURCE1000} Nahuatl nhn nhn_MX)}
%{expand:%(sh %{SOURCE1000} Niuean niu niu_NU niu_NZ)}
%{expand:%(sh %{SOURCE1000} Dutch nl nl_AW nl_BE nl_NL)}
%{expand:%(sh %{SOURCE1000} Norwegian no r:nb r:nn nb_NO nn_NO)}
%{expand:%(sh %{SOURCE1000} Ndebele nr nr_ZA)}
%{expand:%(sh %{SOURCE1000} "Northern Sotho" nso nso_ZA)}
%{expand:%(sh %{SOURCE1000} Occitan oc oc_FR)}
%{expand:%(sh %{SOURCE1000} Oriya or or_IN)}
%{expand:%(sh %{SOURCE1000} Ossetian os os_RU)}
%{expand:%(sh %{SOURCE1000} Punjabi pa pa_IN pa_PK)}
%{expand:%(sh %{SOURCE1000} Papiamento pap r:pp pap_AN pap_AW pap_CW)}
%{expand:%(sh %{SOURCE1000} Polish pl csb_PL pl_PL)}
%{expand:%(sh %{SOURCE1000} Pashto ps ps_AF)}
%{expand:%(sh %{SOURCE1000} Portuguese pt pt_BR pt_PT)}
%{expand:%(sh %{SOURCE1000} Quechua quz quz_PE)}
%{expand:%(sh %{SOURCE1000} Romanian ro ro_RO)}
%{expand:%(sh %{SOURCE1000} Russian ru ru_RU ru_UA)}
%{expand:%(sh %{SOURCE1000} Kinyarwanda rw rw_RW)}
%{expand:%(sh %{SOURCE1000} Sanskrit sa sa_IN)}
%{expand:%(sh %{SOURCE1000} Santali sat sat_IN)}
%{expand:%(sh %{SOURCE1000} Sardinian sc sc_IT)}
%{expand:%(sh %{SOURCE1000} Sindhi sd sd_IN sd_IN@devanagari)}
%{expand:%(sh %{SOURCE1000} Saami se se_NO)}
%{expand:%(sh %{SOURCE1000} Secwepemctsin shs shs_CA)}
%{expand:%(sh %{SOURCE1000} Sinhala si si_LK)}
%{expand:%(sh %{SOURCE1000} Slovak sk sk_SK)}
%{expand:%(sh %{SOURCE1000} Slovenian sl sl_SI)}
%{expand:%(sh %{SOURCE1000} Serbian sr sr_ME sr_RS)}
%{expand:%(sh %{SOURCE1000} Somali so so_DJ so_ET so_KE so_SO)}
%{expand:%(sh %{SOURCE1000} Albanian sq sq_AL sq_MK)}
%{expand:%(sh %{SOURCE1000} Swati ss ss_ZA)}
%{expand:%(sh %{SOURCE1000} Sotho st st_ZA)}
%{expand:%(sh %{SOURCE1000} Swedish sv sv_FI sv_SE)}
# sw_XX?
%{expand:%(sh %{SOURCE1000} Swahili sw sw_KE sw_TZ)}
%{expand:%(sh %{SOURCE1000} Silesian szl szl_PL)}
%{expand:%(sh %{SOURCE1000} Tamil ta ta_IN ta_LK)}
%{expand:%(sh %{SOURCE1000} Telugu te te_IN)}
%{expand:%(sh %{SOURCE1000} Tajik tg tg_TJ)}
%{expand:%(sh %{SOURCE1000} Thai th th_TH)}
%{expand:%(sh %{SOURCE1000} Tharu/Tharuhati the the_NP)}
%{expand:%(sh %{SOURCE1000} Turkmen tk tk_TM)}
%{expand:%(sh %{SOURCE1000} Pilipino tl r:ph fil_PH tl_PH)}
%{expand:%(sh %{SOURCE1000} Tswana tn tn_ZA)}
%{expand:%(sh %{SOURCE1000} Turkish tr tr_CY tr_TR)}
%{expand:%(sh %{SOURCE1000} Tsonga ts ts_ZA)}
%{expand:%(sh %{SOURCE1000} Tatar tt tt_RU)}
%{expand:%(sh %{SOURCE1000} Uyghur ug ug_CN)}
%{expand:%(sh %{SOURCE1000} Unami unm unm_US)}
%{expand:%(sh %{SOURCE1000} Ukrainian uk uk_UA)}
%{expand:%(sh %{SOURCE1000} Urdu ur ur_PK)}
%{expand:%(sh %{SOURCE1000} Uzbek uz uz_UZ)}
%{expand:%(sh %{SOURCE1000} Venda ve ve_ZA)}
%{expand:%(sh %{SOURCE1000} Vietnamese vi vi_VN)}
%{expand:%(sh %{SOURCE1000} Walloon wa wa_BE)}
%{expand:%(sh %{SOURCE1000} Walser wae wae_CH)}
%{expand:%(sh %{SOURCE1000} Wolof wo wo_SN)}
%{expand:%(sh %{SOURCE1000} Xhosa xh xh_ZA)}
%{expand:%(sh %{SOURCE1000} Yiddish yi yi_US)}
%{expand:%(sh %{SOURCE1000} Yoruba yo yo_NG)}
%{expand:%(sh %{SOURCE1000} "Yue Chinese (Cantonese)" yue yue_HK)}
%{expand:%(sh %{SOURCE1000} Chinese zh zh_CN zh_HK zh_SG zh_TW cmn_TW hak_TW lzh_TW nan_TW nam_TW@latin)}
%{expand:%(sh %{SOURCE1000} Zulu zu zu_ZA)}
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
%{_slibdir}/ld-%{version}.so
%if %isarch %{ix86}
%{_slibdir}/ld-linux.so.2
%{_slibdir}/i686
%endif
%if %isarch x86_64
%{_slibdir}/ld-linux-x86-64.so.2
%endif
%if %isarch %{arm}
%{_slibdir}/ld-linux.so.3
%endif
%if %isarch armv7hl armv6j
%{_slibdir}/ld-linux-armhf.so.3
%endif
%if %isarch aarch64
%{_slibdir}/ld-linux-aarch64.so.1
%{_slibdir32}/ld-linux-aarch64.so.1
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
%endif

########################################################################
%if %{build_biarch}
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
%if "%{name}" == "glibc"
%dir %{_libdir32}/audit
%{_libdir32}/audit/sotruss-lib.so
%{_libdir32}/gconv/*.so
%{_libdir32}/gconv/gconv-modules
%ghost %{_libdir32}/gconv/gconv-modules.cache
%endif
%if %isarch %{mips} %{mipsel}
%{_slibdir}32/ld-%{glibcversion}.so
%{_slibdir}32/ld.so.1
%{_slibdir}32/lib*-[.0-9]*.so
%{_slibdir}32/lib*.so.[0-9]*
%{_slibdir}32/libSegFault.so
%dir %{_libdir}32/gconv
%{_libdir}32/gconv/*
%{_slibdir}64/ld-%{glibcversion}.so
%{_slibdir}64/ld.so.1
%{_slibdir}64/lib*-[.0-9]*.so
%{_slibdir}64/lib*.so.[0-9]*
%{_slibdir}64/libSegFault.so
%dir %{_libdir}64/gconv
%{_libdir}64/gconv/*
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
Requires:	kernel-headers
Provides:	glibc-crypt_blowfish-devel = %{crypt_bf_ver}
Provides:	eglibc-crypt_blowfish-devel = %{crypt_bf_ver}
%rename		glibc-doc
%endif
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
%if "%{name}" == "glibc"
%{_mandir}/man3/*
%{_infodir}/libc.info*
%doc %{_docdir}/glibc/*
%exclude %{_docdir}/glibc/nss
%exclude %{_docdir}/glibc/gai.conf
%exclude %{_docdir}/glibc/COPYING
%exclude %{_docdir}/glibc/COPYING.LIB
%endif
%{_includedir}/*
%{_libdir}/*.o
%{_libdir}/*.so
%exclude %{_slibdir}/ld*-[.0-9]*.so
%exclude %{_slibdir}/lib*-[.0-9]*.so
%exclude %{_slibdir}/libSegFault.so
%{_libdir}/libc_nonshared.a
%{_libdir}/libg.a
%{_libdir}/libieee.a
%{_libdir}/libmcheck.a
%{_libdir}/libpthread_nonshared.a
#%if "%{name}" == "glibc"
%{_libdir}/librpcsvc.a
#%endif
%if %{build_biarch}
%{_libdir32}/*.o
%{_libdir32}/*.so
%{_libdir32}/libc_nonshared.a
%{_libdir32}/libg.a
%{_libdir32}/libieee.a
%{_libdir32}/libmcheck.a
%{_libdir32}/libpthread_nonshared.a
#%if "%{name}" == "glibc"
%{_libdir32}/librpcsvc.a
#%endif
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

%files -n 	nscd
%config(noreplace) %{_sysconfdir}/nscd.conf
%dir %attr(0755,root,root) /run/nscd
%dir %attr(0755,root,root) %{_var}/db/nscd
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

########################################################################
%prep
%setup -q -n %{source_dir} -a3 -a50

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
%patch70 -p1 -b .biarch~
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

%patch89 -p1 -b .nscd_runpath~

%patch100 -p1 -b .blowfish_nonx86~

%if %{with selinux}
    # XXX kludge to build nscd with selinux support as it added -nostdinc
    # so /usr/include/selinux is not found
    ln -s %{_includedir}/selinux selinux
%endif

find . -type f -size 0 -o -name "*.orig" -exec rm {} \;

# Remove patch backups from files we ship in glibc packages
rm localedata/locales/[a-z_]*.*

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
  BuildFlags=""
  case $arch in
    i[3-6]86)
%ifarch x86_64
	BuildFlags="-march=pentium4 -mtune=generic"
	BuildAltArch="yes"
	BuildCompFlags="-m32"
%else
	BuildFlags="-march=$arch -mtune=atom"
%endif
      ;;
    x86_64)
      BuildFlags="-mtune=generic"
      ;;
    mips|mipsel)
      BuildFlags="-march=mips3"
      BuildCompFlags="-march=mips3"
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
      BuildFlags="-march=armv7-a"
      BuildCompFlags="-march=armv7-a"
      ;;
    armv6*)
      BuildFlags="-march=armv6"
      BuildCompFlags="-march=armv6"
      ;;
  esac

  # Choose biarch support
  MultiArchFlags=
  case $arch in
    i686 | x86_64)
      MultiArchFlags="--enable-multi-arch"
      ;;
  esac

  # Determine C & C++ compilers
  BuildCC="%{__cc} $BuildCompFlags"
  BuildCXX="%{__cxx} $BuildCompFlags"

  # Are we supposed to cross-compile?
  if [[ "%{target_cpu}" != "%{_target_cpu}" ]]; then
    # Can't use BuildCC anymore with previous changes.
    BuildCC="%{cross_program_prefix}gcc $BuildCompFlags"
    BuildCXX="%{cross_program_prefix}g++ $BuildCompFlags"
    BuildCross="--build=%{_target_platform}"
    export libc_cv_forced_unwind=yes libc_cv_c_cleanup=yes
  fi


  BuildFlags="$BuildFlags -DNDEBUG=1 %{__common_cflags} -O3 -fno-lto"

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

  # NPTL+TLS are now the default
  Pthreads="nptl"

  # Add-ons
  AddOns="$Pthreads,ports,libidn"

  # Kernel headers directory
  KernelHeaders=%{_includedir}

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
  rm -rf build-$arch-linux
  mkdir  build-$arch-linux
  pushd  build-$arch-linux
  [[ "$BuildAltArch" = "yes" ]] && touch ".alt" || touch ".main"
  CC="$BuildCC" CXX="$BuildCXX" CFLAGS="$BuildFlags" LDFLAGS="%{ldflags}" ../configure \
    $arch-%{_target_vendor}-%{_target_os}%{gnuext} $BuildCross \
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
%if !%{with nscd}
    --disable-build-nscd \
%endif
    --enable-bind-now \
    --enable-lock-elision \
    $ExtraFlags \
    $MultiArchFlags \
    --enable-kernel=%{enablekernel} \
    --with-headers=$KernelHeaders ${1+"$@"}
  %make -r
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
	%make install install_root=%{buildroot}/$ALT_ARCH -C build-$ALT_ARCH

	# Dispatch */lib only
	case "$ALT_ARCH" in
	    mips32*)
		LIB="%{_slibdir}32"
		;;
	    mips64*)
		LIB="%{_slibdir}64"
		;;
	    mips*)
		LIB="%{_slibdir}"
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
install -m644 bits/stdio-lock.h -D %{buildroot}%{_includedir}/bits/stdio-lock.h
# And <bits/libc-lock.h> needs sanitizing as well.
install -m644 %{SOURCE10} -D %{buildroot}%{_includedir}/bits/libc-lock.h

# Compatibility hack: this locale has vanished from glibc, but some other
# programs are still using it. Normally we would handle it in the %pre
# section but with glibc that is simply not an option
mkdir -p %{buildroot}%{_localedir}/ru_RU/LC_MESSAGES

# (tpg) workaround for aarch64 ?
%if %isarch aarch64
ls -sf %{_slibdir}/ld-linux-aarch64.so.1 %{buildroot}%{_slibdir32}/ld-linux-aarch64.so.1
%endif

%if "%{name}" == "glibc"
install -m 644 mandriva/nsswitch.conf %{buildroot}%{_sysconfdir}/nsswitch.conf
%endif

# This is for ncsd - in glibc 2.2
%if %{with nscd}
    install -m644 nscd/nscd.conf -D %{buildroot}%{_sysconfdir}/nscd.conf
    install -m755 -d %{buildroot}%{_sysconfdir}/sysconfig
    touch %{buildroot}%{_sysconfdir}/sysconfig/nscd
    install -m755 %{SOURCE6} -D %{buildroot}%{_unitdir}/nscd.service
    install -m755 %{SOURCE7} -D %{buildroot}%{_unitdir}/nscd.socket
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

# rquota.x and rquota.h are now provided by quota
rm %{buildroot}%{_includedir}/rpcsvc/rquota.[hx]

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
    pushd build-%{target_cpu}-linux html
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
	rm -f %{buildroot}%{_slibdir}32/libmemusage.so
	rm -f %{buildroot}%{_slibdir}32/libpcprofile.so
	rm -f %{buildroot}%{_slibdir}64/libmemusage.so
	rm -f %{buildroot}%{_slibdir}64/libpcprofile.so
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
export LD_LIBRARY_PATH=%{buildroot}/%{_lib}:%{buildroot}%{_libdir}:$LD_LIBRARY_PATH
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
SUPPORTED=$I18NPATH/SUPPORTED DESTDIR=%{buildroot} %make -f %{SOURCE20}
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
rm -rf %{buildroot}%{_libdir}/audit
rm -rf %{buildroot}%{_libexecdir}/getconf
rm -rf %{buildroot}%{_localstatedir}/db/Makefile


# In case we are cross-compiling, don't bother to remake symlinks and
# fool spec-helper when stripping files
export DONT_SYMLINK_LIBS=1
%endif

# This will make the '-g' argument to be passed to eu-strip for these libraries, so that
# some info is kept that's required to make valgrind work without depending on glibc-debug
# package to be installed.
export EXCLUDE_FROM_FULL_STRIP="ld-%{version}.so libpthread libc-%{version}.so libm-%{version}.so"

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
