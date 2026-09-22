%define libdir32 %{_exec_prefix}/lib
# (tpg) disable LTO as grub2 is not designed to benefit from it
%define _disable_lto 1

%if %{cross_compiling}
# host gdb-add-index aborts on riscv64 grub kernel.exec DWARF
%undefine _include_gdb_index
%endif

%ifarch %{ix86} %{x86_64}
%define platform pc
%elifarch armv7hnl
%define platform uboot
%elifarch %{efi}
%define platform efi
%endif

%define snapshot %{nil}
%define beta rc1
# GitLab snapshot tarball does not include imported gnulib; bootstrap.conf pin.
%define gnulib_rev 9f48fb992a3d7e96610c4ce8be969cff2d61a01b

Summary:	GNU GRUB is a Multiboot boot loader
Name:		grub2
## WARNING! before updating snapshots grep local for
## 'boot/grub' in the source , including Makefiles*
## and compare to grub2-2.02-unity-mkrescue-use-grub2-dir.patch
## do _NOT_ update without doing that .. we just go lucky until now.
Version:	2.16
Release:	%{?beta:0.%{beta}.}7
Group:		System/Kernel and hardware
License:	GPLv3+
Url:		https://www.gnu.org/software/grub/
%if 0%{?beta:1}
# Development moved to https://gitlab.freedesktop.org/gnu-grub/grub/
Source0:	https://gitlab.freedesktop.org/gnu-grub/grub/-/archive/grub-%{version}-%{beta}/grub-grub-%{version}-%{beta}.tar.bz2
%else
%if "%{snapshot}" == ""
Source0:	https://ftp.gnu.org/gnu/grub/grub-%{version}%{?beta:-%{beta}}.tar.xz
%else
# git clone https://gitlab.freedesktop.org/gnu-grub/grub.git
# git archive --format=tar --prefix grub-2.16-$(date +%Y%m%d)/ HEAD | xz -vf > grub-2.16-$(date +%Y%m%d).tar.xz
Source0:	grub-%{version}-%{snapshot}.tar.xz
%endif
%endif
Source1:	90_persistent
Source2:	grub.default
# www.4shared.com/archive/lFCl6wxL/grub_guidetar.html
Source4:	grub_guide.tar.gz
Source5:	DroidSansMonoLicense.txt
Source6:	DroidSansMono.ttf
Source9:	update-grub2
Source11:	grub2.rpmlintrc
# (tpg) source
# rm -rf grub-extras && git clone https://git.savannah.gnu.org/git/grub-extras.git && cd grub-extras
# git archive --prefix=grub-extras/ --format=tar HEAD | xz > ../grub-extras-$(date +%Y%m%d).tar.xz
Source12:	grub-extras-20231020.tar.xz
# documentation and simple test script for testing grub2 themes
Source13:	grub2-theme-test.sh
# Upstream 2.16 ships util/grub.d/30_uefi-firmware.in
Source14:	30-uefi_firmware
Source15:	https://github.com/coreutils/gnulib/archive/%{gnulib_rev}/gnulib-%{gnulib_rev}.tar.gz
# GitLab snapshot has no .po files; TP cannot be rsync'd at build time
# rsync -Lrtvz translationproject.org::tp/latest/grub/ grub-po
# tar cJf grub-po-$(date +%Y%m%d).tar.xz grub-po
Source16:	grub-po-20260820.tar.xz
Patch0:		grub2-locales.patch
Patch1:		grub2-00_header.patch
Patch2:		grub2-custom-color.patch
Patch3:		grub2-read-cfg.patch
Patch4:		grub2-symlink-is-garbage.patch
Patch5:		grub-2.04-workaround-llvm-bug-48528.patch
Patch6:		grub-2.06-enable-os-prober.patch
# (crazy) replaces:
# grub-2.00.Linux.remove.patch
# grub-2.00-add-recovery_option.patch
# grub2-2.02-add-support-for-kernel-install.patch
# fix-btrfs-GRUB_CMDLINE_LINUX_RECOVERY.patch ( https://issues.openmandriva.org/show_bug.cgi?id=2423 )
# Ok @bero .. ( also use this patch for OMV things touchting /grub.d/ and so on )
# In addition console boot support got added ( https://issues.openmandriva.org/show_bug.cgi?id=2402 )
Patch7:		omv-configuration.patch
Patch9:		grub2-2.00-class-via-os-prober.patch
Patch10:	grub-2.00-autoreconf-sucks.patch
Patch11:	0468-Don-t-write-messages-to-the-screen.patch
Patch12:	grub-2.02-beta2-custom-vendor-config.patch
#Patch13:	0001-Revert-Make-grub-install-check-for-errors-from-efibo.patch
Patch15:	grub-2.02-20180620-disable-docs.patch
# Without this, build fails on aarch64 w/ unresolved symbol abort
# while running grub-mkimage
Patch16:	grub-2.02-define-abort.patch
Patch17:	grub-2.04-grub-extras-lua-fix.patch

# (crazy) these are 2 BAD patches , FIXME after Lx4
# Patch7 prepares remove for that ( partially )
# Patches from Mageia
Patch100:	grub2-2.00-mga-dont_write_sparse_file_error_to_screen.patch
Patch101:	grub2-2.00-mga-dont_write_diskfilter_error_to_screen.patch

# Patches from SuSe

# Patches from Unity
Patch300:	grub2-2.02-unity-mkrescue-use-grub2-dir.patch

# Patches from upstream
# [Selected from running git format-patch grub-2.12-rc1 in master branch]
Patch1000:	0009-util-bash-completion-Load-scripts-on-demand.patch

# Additional OpenMandriva patches that need to be applied after upstream patches
Patch2000:	grub-2.06-add-mitigations-off-mode.patch
# BIOS: grub_pit_wait() can spin forever on a stuck 0x61 latch, hanging
# after the boot.S "GRUB " banner and before "Welcome to GRUB!" / menu
Patch2001:	grub-2.16-i386-pc-tsc-no-hang.patch
# BIOS: VBE page flipping draws the menu on a buffer the VBIOS never shows
Patch2002:	grub2-i386-pc-no-pageflipping.patch
# BIOS: do not switch to gfxterm (VBE mode-set hang before the menu)
Patch2003:	grub-2.16-00_header-bios-console.patch
# Quiet remaining BIOS banners (loading dots, Welcome to GRUB!)
Patch2004:	grub-2.16-quiet-bios-banner.patch
# EFI: when the legacy initrd allocation cannot fit a large initrd below
# initrd_addr_max (low RAM reported as boot-services memory), report an
# explicit actionable error instead of the opaque relocator "out of memory".
# The LoadFile2 path (default for modern kernels) is unaffected.
Patch2005:	grub-2.16-legacy-initrd-diag.patch

BuildRequires:	autoconf
BuildRequires:	autoconf-archive
BuildRequires:	automake
BuildRequires:	python
BuildRequires:	patch
BuildRequires:	git-core
BuildRequires:	slibtool
BuildRequires:	libatomic-devel
BuildRequires:	%{_lib}atomic-static-devel
BuildRequires:	make
BuildRequires:	efi-srpm-macros
BuildRequires:	autogen
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	fontpackages-devel
BuildRequires:	unifont
BuildRequires:	fonts-ttf-dejavu
BuildRequires:	unifont-fonts
BuildRequires:	help2man
BuildRequires:	rsync
BuildRequires:	texinfo
BuildRequires:	texlive-tex.bin
BuildRequires:	glibc-static-devel
BuildRequires:	locales-extra-charsets
BuildRequires:	gettext-devel
BuildRequires:	lzo-devel
BuildRequires:	pkgconfig(devmapper)
BuildRequires:	pkgconfig(fuse3)
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(libtasn1)
%if %{cross_compiling}
# target grub-mkimage is run via binfmt qemu while building grub.efi
BuildRequires:	qemu-%{_arch}-static
%endif
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	pkgconfig(ncursesw)
%ifarch %{arm} %{armx}
BuildRequires:	gcc
%endif
Provides:	bootloader
# (crazy) without gettext() function of grub2 is fakeed with printf ..
Requires:	gettext-base
Suggests:	os-prober
Suggests:	distro-theme-common
Suggests:	distro-theme-OpenMandriva-grub2
%ifarch %{ix86} %{x86_64}
Suggests:	microcode-intel
%endif
Conflicts:	grub2-tools < 2.02-1.beta2.6
%rename		grub2-tools
Suggests:	%{name}-doc >= %{EVRD}
Suggests:	%{name}-extra >= %{EVRD}
%ifarch %{efi}
# (tpg) this is needed for grub2-install
Requires:	efibootmgr
Requires:	efi-filesystem
%endif

%description
GNU GRUB is a Multiboot boot loader. It was derived from GRUB, the
GRand Unified Bootloader, which was originally designed and implemented
by Erich Stefan Boleyn.

Briefly, a boot loader is the first software program that runs when a
computer starts. It is responsible for loading and transferring control
to the operating system kernel software (such as the Hurd or Linux).
The kernel, in turn, initializes the rest of the operating system (e.g. GNU).

%ifarch %{efi}
%package efi
Summary:	GRUB for EFI systems
Group:		System/Kernel and hardware
# (tpg) this is needed to sign our EFI image
#BuildRequires:	pesign
Requires:	%{name} >= %{EVRD}
# (crazy) without gettext() function of grub2 is fakeed with printf ..
Requires:	gettext-base
Conflicts:	%{name} < 2.02-8

%description efi
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.

It support rich variety of kernel formats, file systems, computer
architectures and hardware devices.  This subpackage provides support
for EFI systems.
%endif

%package extra
Summary:	Extra tools for GRUB
Group:		System/Kernel and hardware
Requires:	%{name} >= %{EVRD}
Conflicts:	%{name} < 2.02-8
Requires:	console-setup
Suggests:	xorriso
Suggests:	mtools

%description extra
Extra tools and files for GRUB.

%package starfield-theme
Summary:	An example theme for GRUB
Group:		System/Kernel and hardware
Requires:	%{name} >= %{EVRD}

%description starfield-theme
Example 'starfield' theme for GRUB.

%package doc
Summary:	Documentation for GRUB
Group:		System/Kernel and hardware
Requires:	%{name} >= %{EVRD}
Conflicts:	%{name} < 2.02-8

%description doc
Documentation for GRUB.

#-----------------------------------------------------------------------

%ifarch %{arm} %{armx}
%global optflags %{optflags} -fuse-ld=bfd
%global build_ldflags %{build_ldflags} -fuse-ld=bfd
%endif

%prep
%autosetup -p1 -n grub-grub-%{version}-%{beta} -a12
# Keep gnulib outside the source tree so autogen.sh does not add it to POTFILES
tar -xf %{SOURCE15} -C ..

# GitLab archive is a git snapshot: import gnulib and generate configure
./bootstrap --no-git --skip-po --gnulib-srcdir=../gnulib-%{gnulib_rev}

# VPATH builds run pot generation from $builddir/po
sed -i -e 's|sed -f grub.d.sed|sed -f $(srcdir)/grub.d.sed|' po/Makefile.in.in

sed -i -e "s|^FONT_SOURCE=.*|FONT_SOURCE=%{SOURCE6}|g" configure configure.ac
sed -ri -e 's/-g"/"/g' -e "s/-Werror//g" configure.ac
sed -i -e 's/-Werror//g' grub-core/Makefile.am
touch grub-core/extra_deps.lst

# (tpg) remove not needed extra modules
rm -rf grub-extras/915resolution
rm -rf grub-extras/disabled
rm -rf grub-extras/ntldr-img
rm -rf grub-extras/lua

export GRUB_CONTRIB=./grub-extras
sed -i -e 's,-I m4,-I m4 --dont-fix,g' autogen.sh

# GitLab snapshot has no catalogs; ship TP snapshot (ABF has no network)
tar -xf %{SOURCE16} --strip-components=1 -C po
{
	ls po/*.po | xargs -L 100 basename -s .po -a
	echo en@quot en@hebrew de@hebrew en@cyrillic en@greek en@arabic en@piglatin de_CH
} | tr ' ' '\n' | sort -u | xargs > po/LINGUAS

#-----------------------------------------------------------------------
%build
%define _disable_ld_no_undefined 1
export GRUB_CONTRIB="$PWD/grub-extras"
export CONFIGURE_TOP="$PWD"
%if %{cross_compiling}
# so the target grub-mkimage can run (binfmt qemu-user)
export QEMU_LD_PREFIX=/usr/%{_target_platform}
# target ld.so has no cache and only searches /lib by default
export LD_LIBRARY_PATH=/usr/%{_lib}:/%{_lib}
# Host freetype for BUILD_CC. Using the target .pc would mix native
# headers with the cross library (or the reverse).
_grub_host_freetype_cflags="$(PKG_CONFIG_SYSROOT_DIR= PKG_CONFIG_LIBDIR=%{_libdir}/pkgconfig:%{_datadir}/pkgconfig PKG_CONFIG_PATH= pkg-config --cflags freetype2)"
_grub_host_freetype_libs="$(PKG_CONFIG_SYSROOT_DIR= PKG_CONFIG_LIBDIR=%{_libdir}/pkgconfig:%{_datadir}/pkgconfig PKG_CONFIG_PATH= pkg-config --libs freetype2)"
%endif

#(proyvind): debugedit will fail on some binaries if linked using gold
# https://savannah.gnu.org/bugs/?34539
# https://sourceware.org/bugzilla/show_bug.cgi?id=14187
./autogen.sh

%if "%{platform}" != ""
mkdir -p %{platform}
cd %{platform}
# Clang causes openmandriva theme to disappear. Only black theme on non UEFI/EFI platform. Switch back to gcc (angry)
%if %{cross_compiling}
%configure CC=%{_target_platform}-gcc BUILD_CC=gcc TARGET_CC=%{_target_platform}-gcc \
	BUILD_FREETYPE_CFLAGS="$_grub_host_freetype_cflags" \
	BUILD_FREETYPE_LIBS="$_grub_host_freetype_libs" \
%else
%configure CC=gcc BUILD_CC=gcc TARGET_CC=gcc \
%endif
	CFLAGS="-Os -fuse-ld=bfd" \
	LDFLAGS="" \
	TARGET_LDFLAGS="-static" \
	--with-platform=%{platform} \
	--with-dejavufont=%{_datadir}/fonts/TTF/dejavu/DejaVuSans.ttf \
	--enable-nls \
%ifarch %{x86_64}
	--enable-efiemu \
%endif
	--program-transform-name=s,grub,%{name}, \
	--libdir=%{libdir32} \
	--libexecdir=%{libdir32} \
	--with-grubdir=grub2 \
	--disable-werror \
	--enable-device-mapper \
	--enable-grub-mkfont \
	--enable-device-mapper \
	--enable-grub-emu-sdl \
	--without-included-regex

# make -O can swallow extra_deps.lst redirection
mkdir -p grub-core
touch grub-core/extra_deps.lst
%make_build ascii.h widthspec.h
%make_build all
cd -
%endif

%ifarch %{efi}
mkdir -p efi
cd efi
%ifarch %{arm} %{armx}
%configure CC=gcc BUILD_CC=gcc TARGET_CC=gcc \
%else
%if %{cross_compiling}
%configure CC=%{_target_platform}-gcc BUILD_CC=gcc TARGET_CC=%{_target_platform}-gcc \
	BUILD_FREETYPE_CFLAGS="$_grub_host_freetype_cflags" \
	BUILD_FREETYPE_LIBS="$_grub_host_freetype_libs" \
%else
%configure BUILD_CC=%{__cc} TARGET_CC=%{__cc} \
%endif
%endif
	CFLAGS="-Os -fuse-ld=bfd" \
	LDFLAGS="" \
	TARGET_LDFLAGS="-static" \
	--with-platform=efi \
	--with-dejavufont=%{_datadir}/fonts/TTF/dejavu/DejaVuSans.ttf \
	--enable-nls \
	--program-transform-name=s,grub,%{name}-efi, \
	--libdir=%{libdir32} \
	--libexecdir=%{libdir32} \
	--with-grubdir=grub2 \
	--disable-werror \
	--enable-grub-mkfont \
	--enable-device-mapper \
	--enable-grub-emu-sdl \
	--without-included-regex

# make -O can swallow extra_deps.lst redirection
mkdir -p grub-core
touch grub-core/extra_deps.lst
%make_build ascii.h widthspec.h
%make_build -C grub-core

# gfxterm_menu is a test module, not a boot module
%define grub_modules_default all_video boot btrfs cat gettext chain configfile cryptodisk echo efi_gop efifwsetup efinet ext2 f2fs fat font gcry_rijndael gcry_rsa gcry_serpent gcry_sha256 gcry_twofish gcry_whirlpool gfxmenu gfxterm gfxterm_background gzio halt hfsplus iso9660 jpeg loadenv loopback linux lsefi luks lvm mdraid09 mdraid1x minicmd normal part_apple part_gpt part_msdos password_pbkdf2 probe png reboot regexp search search_fs_file search_fs_uuid search_label serial sleep squash4 syslinuxcfg test tftp video xfs zstd

%ifarch %{aarch64}
%define grubefiarch arm64-efi
%define grub_modules %{grub_modules_default}
%elifarch %{ix86} %{x86_64}
%define grubefiarch %{_arch}-efi
%define grub_modules multiboot multiboot2 %{grub_modules_default}
%else
%define grubefiarch %{_arch}-efi
%define grub_modules %{grub_modules_default}
%endif

#This line loads all the modules but makes the efi image unstable.
#./grub-mkimage -O %{grubefiarch} -p /EFI/openmandriva/%{name}-efi -o grub.efi -d grub-core $(ls grub-core/*.mod | sed 's/.*\///g' | sed 's/\.mod//g' | xargs
#) In practice the grub.efi image is only required for the iso. when grub is installed it selects the modules it needs to boot the current install from the installed
#  OS.

#These lines produce a grub.efi suitable for an iso. Note the path in the -p option it points to the grub.cfg file on the iso.
../%{platform}/grub-mkimage -v -O %{grubefiarch} -C xz -p /EFI/BOOT -o grub.efi -d grub-core %{grub_modules}

# sign our EFI image
#%%pesign -s -i%%{buildroot}/%{efi_esp_dir}/grub.efi -o %{buildroot}/%{efi_esp_dir}/OMgrub.efi
cd -
%endif


#-----------------------------------------------------------------------
%install
######legacy
%if "%{platform}" != ""
%make_install -C %{platform}

# (crazy) fixme? why so?
# Script that makes part of grub.cfg persist across updates
install -m755 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/grub.d/90_persistent
# 2.16 ships 30_uefi-firmware; do not install the older 30_uefi_firmware copy

# Ghost config file
install -d %{buildroot}/boot/%{name}
touch %{buildroot}/boot/%{name}/grub.cfg
%endif

######EFI
%ifarch %{efi}
%make_install -C efi/grub-core

install -m755 efi/grub.efi -D %{buildroot}/%{efi_esp_dir}/grub.efi
#%%pesign -s -i %%{buildroot}/%{efi_esp_dir}/grub.efi -o %%{buildroot}/%{efi_esp_dir}/grub.efi
%endif

%if "%{platform}" == "efi"
cd %{buildroot}%{_bindir}
for i in grub2-efi-*; do
    GENERICNAME="$(printf "%s\n" $i |sed -e 's,-efi,,')"
    mv $i $GENERICNAME
done
cd -
%endif

# (crazy) all this is strange , figure bc we do the same from other package(s)
# Defaults
install -m755 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/default/grub
# (tpg) use default distro name
sed -e 's#TMP_DISTRO#%{distribution}#' -i %{buildroot}%{_sysconfdir}/default/grub

#Add more useful update-grub2 script
install -m755 %{SOURCE9} -D %{buildroot}%{_bindir}

install -d %{buildroot}/boot/%{name}/themes/

#bugfix: error message before loading of grub2 menu on boot
mkdir -p %{buildroot}%{_localedir}/en/LC_MESSAGES
cp -f %{buildroot}%{_localedir}/en@quot/LC_MESSAGES/grub.mo %{buildroot}%{_localedir}/en/LC_MESSAGES/grub.mo

# (tpg) remove *.modules and leave *.mod
# Allow stuff to fail because some modules may not have been built
# (e.g. no EFI)
find %{buildroot}%{libdir32}/grub/*-%{platform} -name "*.module" -delete || :
find %{buildroot}%{libdir32}/grub/%{_arch}-efi/ -name "*.module" -delete || :

rm -f %{buildroot}%{_bindir}/%{name}-sparc64-setup
rm -f %{buildroot}%{_bindir}/%{name}-ofpathname

%find_lang grub

%triggerin -- %{name} < %{EVRD}
# (tpg) run only on update
# (tpg) remove wrong line in boot options
if [ -e %{_sysconfdir}/default/grub ]; then
    if grep -q "init=/lib/systemd/systemd" %{_sysconfdir}/default/grub; then
	sed -i -e 's#init=/lib/systemd/systemd##g' %{_sysconfdir}/default/grub
    fi
# (tpg) handle backlight parameter for varsious kernel versions
    if grep -q "acpi_backlight=vendor" %{_sysconfdir}/default/grub && [[ $(uname -r | awk -F[-] '{print $1}') < "4.3.0" ]] ; then
	sed -e 's#acpi_backlight=vendor# video.use_native_backlight=1 #g' %{_sysconfdir}/default/grub
    fi
    if grep -q "video.use_native_backlight=1" %{_sysconfdir}/default/grub && [[ $(uname -r | awk -F[-] '{print $1}') > "4.3.0" ]] ; then
	sed -e 's#video.use_native_backlight=1# acpi_backlight=vendor #g' %{_sysconfdir}/default/grub
    fi
# (tpg) disable audit messages
    if ! grep -q "^GRUB_CMDLINE_LINUX_DEFAULT.*audit=0.*" %{_sysconfdir}/default/grub; then
	sed -i -e 's#^GRUB_CMDLINE_LINUX_DEFAULT\=\"#GRUB_CMDLINE_LINUX_DEFAULT\=\" audit=0 #' %{_sysconfdir}/default/grub
    fi
# (crazy) FIXME: this need patch , btrfs and f2fs
# (tpg) set GRUB_SAVEDEFAULT=false to fix bug https://issues.openmandriva.org/show_bug.cgi?id=1814
# (tpg) revert because of https://issues.openmandriva.org/show_bug.cgi?id=1915
    if grep -q "GRUB_SAVEDEFAULT=" %{_sysconfdir}/default/grub; then
	sed -i -e 's#GRUB_SAVEDEFAULT=false#GRUB_SAVEDEFAULT=true#g' %{_sysconfdir}/default/grub
    fi
# (tpg) set acpi_osi=Linux
    if ! grep -q "acpi_osi=Linux" %{_sysconfdir}/default/grub; then
	sed -i -e 's#^GRUB_CMDLINE_LINUX_DEFAULT\=\"#GRUB_CMDLINE_LINUX_DEFAULT\=\" acpi_osi=Linux #' %{_sysconfdir}/default/grub
    fi
# (tpg) set acpi_osi='!Windows 2012' for modern UEFI
    if ! grep -q "acpi_osi='\!Windows 2012'" %{_sysconfdir}/default/grub; then
	sed -i -e "s#^GRUB_CMDLINE_LINUX_DEFAULT\=\"#GRUB_CMDLINE_LINUX_DEFAULT\=\" acpi_osi='\!Windows 2012' #" %{_sysconfdir}/default/grub
    fi
# (tpg) enable Multi-Queue Block IO Queueing Mechanism
    if ! grep -q "scsi_mod.use_blk_mq=1" %{_sysconfdir}/default/grub; then
	sed -i -e "s#^GRUB_CMDLINE_LINUX_DEFAULT\=\"#GRUB_CMDLINE_LINUX_DEFAULT\=\" scsi_mod.use_blk_mq=1 #" %{_sysconfdir}/default/grub
    fi
# Stock default used to start with auto; VBE EDID/native first hangs
# some legacy BIOSes before the menu. Only rewrite that known prefix.
    if grep -q '^GRUB_GFXMODE=auto,' %{_sysconfdir}/default/grub; then
	sed -i -e 's/^GRUB_GFXMODE=auto,\(.*\)$/GRUB_GFXMODE=\1,auto/' %{_sysconfdir}/default/grub
    fi
# (tpg) regenerate grub2 at the end
    %{_bindir}/update-grub2
%ifarch %{ix86} %{x86_64}
    # core.img lives in the MBR gap / BIOS boot partition; mkconfig
    # alone does not refresh it. Re-embed after i386-pc kernel fixes.
    if [ ! -d /sys/firmware/efi ] \
	&& [ "$(stat -c %d:%i /)" = "$(stat -c %d:%i /proc/1/root/.)" ]; then
	boot_disk=$(%{_sbindir}/%{name}-probe -t disk /boot 2>/dev/null \
	    || %{_sbindir}/%{name}-probe -t disk / 2>/dev/null)
	if [ -n "$boot_disk" ] && [ -b "$boot_disk" ]; then
	    %{_sbindir}/%{name}-install --target=i386-pc "$boot_disk" \
		>>/var/log/grub2-bios-install.log 2>&1 || :
	fi
    fi
%endif
fi


%transfiletriggerin -p <lua> -- /boot /boot/grub2/themes /etc/os-release /etc/grub.d /usr/sbin/os-prober
os.execute("%{_bindir}/%{name}-mkconfig -o /boot/%{name}/grub.cfg")

%transfiletriggerpostun -p <lua> -- /lib/modules /boot/grub2/themes
os.execute("%{_bindir}/%{name}-mkconfig -o /boot/%{name}/grub.cfg")

%post
# Only run update-grub2 if we aren't installing to a chroot environment...
# better not to mess with the bootloader in chroot!
if [ "$(stat -c %d:%i /)" = "$(stat -c %d:%i /proc/1/root/.)" ]; then
	%{_sbindir}/update-grub2
%ifarch %{ix86} %{x86_64}
	if [ ! -d /sys/firmware/efi ]; then
		boot_disk=$(%{_sbindir}/%{name}-probe -t disk /boot 2>/dev/null \
			|| %{_sbindir}/%{name}-probe -t disk / 2>/dev/null)
		if [ -n "$boot_disk" ] && [ -b "$boot_disk" ]; then
			%{_sbindir}/%{name}-install --target=i386-pc "$boot_disk" \
				>>/var/log/grub2-bios-install.log 2>&1 || :
		fi
	fi
%endif
fi

# ------------------------------------------------------------------------

%files  -f grub.lang
%{libdir32}/grub/*-%{platform}
%ifarch %{efi}
%if "%{platform}" != "efi"
# grub2-install still needs the EFI modules when the primary platform is BIOS
%{libdir32}/grub/%{_arch}-efi/
%endif
%endif
%{_bindir}/%{name}-editenv
%{_bindir}/%{name}-menulst2cfg
%{_bindir}/%{name}-mkimage
%{_bindir}/%{name}-mkpasswd-pbkdf2
%{_bindir}/%{name}-mkpasswd-argon2
%{_bindir}/%{name}-mkrelpath
%{_bindir}/%{name}-mount
%{_bindir}/%{name}-script-check
%{_bindir}/%{name}-file
%{_sbindir}/update-grub2
%{_sbindir}/%{name}-bios-setup
%{_sbindir}/%{name}-install
%{_sbindir}/%{name}-mkconfig
%{_sbindir}/%{name}-probe
%{_sbindir}/%{name}-reboot
%{_sbindir}/%{name}-set-default
%{_datadir}/grub
%{_datadir}/bash-completion/completions/*
%exclude %{_datadir}/grub/themes/*
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%{_sysconfdir}/grub.d/README
%config %{_sysconfdir}/grub.d/??_*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/default/grub
%dir /boot/%{name}
%dir /boot/%{name}/themes
# Actually, this is replaced by update-grub from scriptlets,
# but it takes care of modified persistent part
%config(noreplace) /boot/%{name}/grub.cfg

%files extra
%{_bindir}/%{name}-fstest
%{_bindir}/%{name}-kbdcomp
%{_bindir}/%{name}-glue-efi
%{_bindir}/%{name}-mkfont
%{_bindir}/%{name}-mklayout
%{_bindir}/%{name}-mknetdir
%{_bindir}/%{name}-mkrescue
%{_bindir}/%{name}-mkstandalone
%{_bindir}/%{name}-protect
%{_bindir}/%{name}-syslinux2cfg
%if %{cross_compiling}
# help2man is skipped when cross-compiling
%optional %{_mandir}/man1/%{name}-*.1*
%optional %{_mandir}/man8/%{name}-*.8*
%else
%{_mandir}/man1/%{name}-*.1*
%{_mandir}/man8/%{name}-*.8*
%endif

%ifarch %{efi}
%files efi
# Files in this package are only required for the creation of iso's
# The install process creates all the files required to boot with grub via EFI
%attr(0755,root,root) %{efi_esp_dir}/grub.efi
%{_bindir}/%{name}-render-label
%{_sbindir}/%{name}-macbless
%endif

%files starfield-theme
%{_datadir}/grub/themes/starfield

%files doc
%doc NEWS README THANKS TODO
#{_docdir}/%%{name}
#{_infodir}/%%{name}.info*
#{_infodir}/grub-dev.info*
