# undefine the next line to either build for the newest or all current kernels
# that's rpmfusion-specific, so only build an akmod for fedora copr
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod

# name should have a -kmod suffix
Name:           intel-gna-kmod

Version:        5.1
Release:        1%{?dist}.5
Summary:        Kernel module for the Intel Gaussian & Neural Accelerator

# See: https://docs.kernel.org/kbuild/modules.html
# Those are the upstream docs on how to build and install out of tree modules

Group:          System Environment/Kernel

License:        GPL-2.0-only AND MIT AND (GPL-2.0-only WITH Linux-syscall-note)
URL:            https://github.com/xanderlent/intel-gna-kmod
Source0:        COPYING
Source1:        drm_internal.h
Source2:        gna_device.c
Source3:        gna_device.h
Source4:        gna_gem.h
Source5:        gna_hw.c
Source6:        gna_hw.h
Source7:        gna_ioctl.c
Source8:        gna_mem.c
Source9:        gna_mem.h
Source10:	gna_pci.c
Source11:	gna_pci.h
Source12:	gna_request.c
Source13:	gna_request.h
Source14:	gna.rst
Source15:	gna_score.c
Source16:	gna_score.h
Source17:	gna_drm.h
Source18:	Linux-syscall-note
Source19:	GPL-2.0
Source20:	MIT
Source21:	Makefile
Source22:	README.md
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  kmodtool
BuildRequires:	kernel-devel
BuildRequires:	kernel-modules-core

# Verify that the package build for all architectures.
# In most time you should remove the Exclusive/ExcludeArch directives
# and fix the code (if needed).
ExclusiveArch:  i686 x86_64
# ExcludeArch: i686 x86_64 ppc64 ppc64le armv7hl aarch64

# get the proper build-sysbuild package from the repo, which
# tracks in all the kernel-devel packages
# this is for rpmfusion users or other repos using the build-sybuild package magic
# more on that here https://lists.fedorahosted.org/archives/list/buildsys@lists.fedoraproject.org/thread/GPPUKUOV7G53RX3R3K3JZZC6OLNO3Z4F/
# we don't need it, it's only used when building for specific kernels, so comment it out
#BuildRequires:  #{_bindir}/kmodtool

# Uncommenting the following defines (and adjusting them for the current kernel) will allow you to manually build for a specific kernel
#define kernels 6.9.6-200.fc40.x86_64
# Actually, you can just leave this one commented because it is a no-op when kernels is defined.
#{!?kernels:BuildRequires: buildsys-build-#{repo}-kerneldevpkgs-#{?buildforkernels:#{buildforkernels}}#{!?buildforkernels:current}-#{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


%description
Out-of-tree kernel module for the Intel Gaussian & Neural Accelerator.

# We don't need a debug package for this particular package to work
# https://superuser.com/questions/1091529/rpm-build-error-empty-files-file-debugfiles-list
%global debug_package %{nil}

# RPMFusion docs say not to name this intel-gna-kmod-common, so uapi it is...
%package	-n intel-gna-headers
Summary:	Userspace API, docs, and licensing info for intel-gna-kmod
Requires:	intel-gna-kmod  >= %{version}
Provides:	intel-gna-kmod-common = %{version}

%description	-n intel-gna-headers
Provides the gna_drm.h userspace api file as well as documentation and license
information for intel-gna-kmod

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T
# manually recreate the correct structure
mkdir include/
mkdir include/uapi
mkdir include/uapi/drm
mkdir LICENSES/
mkdir LICENSES/exceptions/
mkdir LICENSES/preferred/
cp -a %{SOURCE0} %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} \
 %{SOURCE6} %{SOURCE7} %{SOURCE8} %{SOURCE9} %{SOURCE10} %{SOURCE11} \
 %{SOURCE12} %{SOURCE13} %{SOURCE14} %{SOURCE15} %{SOURCE16} %{SOURCE21} \
 %{SOURCE22} .
cp -aL %{SOURCE17} include/uapi/drm 
cp -aL %{SOURCE18} LICENSES/exceptions
cp -aL %{SOURCE19} LICENSES/preferred
cp -aL %{SOURCE20} LICENSES/preferred
# Moving up a directory is a horrible hack, but we'll do it
cd ..

for kernel_version in %{?kernel_versions} ; do
    cp -a intel-gna-kmod-%{version} _kmod_build_${kernel_version%%___*}
done


%build
# Moving up a directory is a horrible hack, but we'll do it
cd ..
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${kernel_version##*___}" M=${PWD}/_kmod_build_${kernel_version%%___*} modules
done


%install
rm -rf ${RPM_BUILD_ROOT}

mkdir -p %{buildroot}/%{_includedir}/drm
install -m 0644 include/uapi/drm/gna_drm.h %{buildroot}/%{_includedir}/drm/gna_drm.h

for kernel_version in %{?kernel_versions}; do
    mkdir -p ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
    make -C "${kernel_version##*___}" M=${PWD}/_kmod_build_${kernel_version%%___*} INSTALL_MOD_PATH=${RPM_BUILD_ROOT} INSTALL_MOD_DIR=%{kmodinstdir_postfix} modules_install
    install -m 0644 gna.ko ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/gna.ko
    # DEPMOD creates a bunch of files for us, we'd rather not bother with them
    rm ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/modules.*
done
%{?akmod_install}


%files -n intel-gna-headers 
%doc README.md gna.rst
%license COPYING LICENSES/
%{_includedir}/drm/gna_drm.h

%clean
rm -rf $RPM_BUILD_ROOT


%changelog
* Wed Jul 3 2024 Alexander F. Lent <lx@xanderlent.com> - 5.1-1.5
- Try installing the module manually if modules_install should fail for some reason (hopefully fixes the final step in the akmods build)
* Tue Jul 2 2024 Alexander F. Lent <lx@xanderlent.com> - 5.1-1.4
- Moving up a directory also has to happen during the build phase
- The make commands need to be adjusted for modern out-of-tree modules.
- DEPMOD during modules_install to the buildroot creates a bunch of files that we don't need.
* Sun Jun 30 2024 Alexander F. Lent <lx@xanderlent.com> - 5.1-1.3
- Move up a directory during the prep phase to fix actual module build
- Fix bad permissions on the installed header file
* Sun Jun 30 2024 Alexander F. Lent <lx@xanderlent.com> - 5.1-1.2
- Update headers package to install Documentation
- Expand README.md to cover potential questions
* Sat Jun 29 2024 Alexander F. Lent <lx@xanderlent.com> - 5.1-1.1
- Initial RPM package for this out of tree module
