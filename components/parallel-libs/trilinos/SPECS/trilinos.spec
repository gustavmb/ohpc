#----------------------------------------------------------------------------bh-
# This RPM .spec file is part of the OpenHPC project.
#
# It may have been modified from the default version supplied by the underlying
# release package (if available) in order to apply patches, perform customized
# build/install configurations, and supply additional files to support
# desired integration conventions.
#
#----------------------------------------------------------------------------eh-

# Build that is is dependent on compiler toolchain and MPI
%define ohpc_compiler_dependent 1
%define ohpc_mpi_dependent 1
%include %{_sourcedir}/OHPC_macros

# Base package name
%define pname trilinos
%define PNAME %(echo %{pname} | tr [a-z] [A-Z])
%define ver_exp 12-10-1

Name:           %{pname}-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
Version:        12.10.1
Release:        1%{?dist}
Summary:        A collection of libraries of numerical algorithms
License:        LGPL-2.0
Group:          %{PROJ_NAME}/parallel-libs
Url:            http://trilinos.sandia.gov/index.html
Source0:        https://github.com/trilinos/Trilinos/archive/trilinos-release-%{ver_exp}.tar.gz
Source1:        OHPC_macros
Patch0:         trilinos-11.14.3-no-return-in-non-void.patch
Patch1:         Trilinos-trilinos-aarch64.patch
BuildRequires:  cmake >= 2.8
BuildRequires:  doxygen
BuildRequires:  expat
BuildRequires:  graphviz
BuildRequires:  libxml2-devel
BuildRequires:  perl
%if 0%{?rhel_version} || 0%{?centos_version} || 0%{?rhel}
BuildRequires:  qt-devel
%else
BuildRequires:  libqt4-devel
%endif
BuildRequires:  swig > 2.0.0
BuildRequires:  xz
BuildRequires:  zlib-devel
BuildRequires:  boost-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
BuildRequires:  phdf5-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
BuildRequires:  netcdf-%{compiler_family}-%{mpi_family}%{PROJ_DELIM}
%if "%{compiler_family}" != intel
BuildRequires:  openblas-%{compiler_family}%{PROJ_DELIM}
%endif
%if 0%{?suse_version} <= 1110
%{!?python_sitearch: %global python_sitearch %(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

#!BuildIgnore: post-build-checks

# Default library install path
%define install_path %{OHPC_LIBS}/%{compiler_family}/%{mpi_family}/%{pname}/%version

%description
Trilinos is a collection of compatible software packages that support parallel
linear algebra computations, solution of linear, non-linear and eigen systems
of equations and related capabilities. The majority of packages are written in
C++ using object-oriented techniques. All packages are self-contained, with the
Trilinos top layer providing a common look-and-feel and infrastructure.

%prep
%setup -q -n  Trilinos-trilinos-release-%{ver_exp}
%patch0 -p1
%patch1 -p1

%build
# OpenHPC compiler/mpi designation
%ohpc_setup_compiler

module load phdf5
module load netcdf
module load boost
%if "%{compiler_family}" != "intel"
module load openblas
%endif

mkdir tmp
cd tmp
cmake   -DCMAKE_INSTALL_PREFIX=%{install_path}                          \
        -DCMAKE_EXE_LINKER_FLAGS:STRING="-fPIC"                         \
        -DCMAKE_VERBOSE_MAKEFILE:BOOL=TRUE                              \
        -DCMAKE_BUILD_TYPE:STRING=RELEASE                               \
        -DBUILD_SHARED_LIBS:BOOL=ON                                     \
        -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON                              \
        -DCMAKE_SKIP_RPATH:BOOL=ON                                      \
        -DTrilinos_VERBOSE_CONFIGURE:BOOL=ON                            \
        -DTrilinos_ENABLE_ALL_PACKAGES:BOOL=OFF                         \
%if "%{compiler_family}" == "intel"
        -DTrilinos_ENABLE_MueLu:BOOL=OFF                                \
        -DTPL_ENABLE_MKL:BOOL=ON                                        \
        -DMKL_INCLUDE_DIRS:FILEPATH="${MKLROOT}/include"                \
        -DMKL_LIBRARY_DIRS:FILEPATH="${MKLROOT}/lib/intel64"            \
        -DMKL_LIBRARY_NAMES:STRING="mkl_rt"                             \
        -DTPL_ENABLE_BLAS:BOOL=ON                                       \
        -DBLAS_LIBRARY_DIRS:PATH="${MKLROOT}/lib/intel64"               \
        -DBLAS_LIBRARY_NAMES:STRING="mkl_rt"                            \
        -DTPL_ENABLE_LAPACK:BOOL=ON                                     \
        -DLAPACK_LIBRARY_DIRS:PATH="${MKLROOT}/lib/intel64"             \
        -DLAPACK_LIBRARY_NAMES:STRING="mkl_rt"                          \
%else
        -DTPL_ENABLE_BLAS:BOOL=ON                                       \
        -DBLAS_LIBRARY_DIRS:PATH="${OPENBLAS_LIB}"                      \
        -DBLAS_LIBRARY_NAMES:STRING="openblas"                          \
        -DTPL_ENABLE_LAPACK:BOOL=ON                                     \
        -DLAPACK_LIBRARY_DIRS:PATH="${OPENBLAS_LIB}"                    \
        -DLAPACK_LIBRARY_NAMES:STRING="openblas"                        \
        -DTrilinos_EXTRA_LINK_FLAGS:STRING="-lgfortran"                 \
%endif
        -DTrilinos_ENABLE_Phalanx:BOOL=ON                               \
        -DTrilinos_ENABLE_Stokhos:BOOL=ON                               \
        -DTrilinos_ENABLE_Didasko:BOOL=ON                               \
        -DTrilinos_ENABLE_TrilinosCouplings:BOOL=ON                     \
        -DTrilinos_ENABLE_PyTrilinos:BOOL=OFF                           \
        -DTrilinos_ENABLE_CTrilinos:BOOL=ON                             \
%if 0%{?suse_version} >= 1210
        -DTrilinos_ENABLE_ForTrilinos:BOOL=ON                           \
%endif
        -DTrilinos_ENABLE_STK:BOOL=OFF                                  \
        -DTrilinos_ENABLE_TESTS:BOOL=OFF                                \
        -DTrilinos_ENABLE_OpenMP:BOOL=ON                                \
        -DTEUCHOS_ENABLE_expat:BOOL=ON                                  \
        -DTEUCHOS_ENABLE_expat:BOOL=ON                                  \
        -DTEUCHOS_ENABLE_libxml2:BOOL=ON                                \
        -DTEUCHOS_ENABLE_gmp:BOOL=ON                                    \
        -DTPL_ENABLE_MPI:BOOL=ON                                        \
        -DMPI_C_COMPILER:FILEPATH=mpicc                                 \
        -DMPI_CXX_COMPILER:FILEPATH=mpicxx                              \
        -DMPI_FORTRAN_COMPILER:FILEPATH=mpif90                          \
        -DTPL_ENABLE_Netcdf:BOOL=ON                                     \
        -DNetcdf_INCLUDE_DIRS:PATH="${NETCDF_INC}"                      \
        -DNetcdf_LIBRARY_DIRS:PATH="${NETCDF_LIB}"                      \
        -DTPL_ENABLE_HDF5:BOOL=ON                                       \
        -DHDF5_INCLUDE_DIRS:PATH="${HDF5_INC}"                          \
        -DHDF5_LIBRARY_DIRS:PATH="${HDF5_LIB}"                          \
        -DHDF5_LIBRARY_NAMES:STRING="hdf5"                              \
        -DTPL_ENABLE_Boost:BOOL=ON                                      \
        -DBOOST_INCLUDE_DIRS:PATH="${BOOST_INC}"                        \
        -DBOOST_LIBRARY_DIRS:PATH="${BOOST_LIB}"                        \
        -DBOOST_LIBRARY_NAMES:STRING="boost"                            \
        -DTPL_ENABLE_Pthread:BOOL=ON                                    \
        -DTPL_ENABLE_CppUnit:BOOL=OFF                                   \
        -DTPL_ENABLE_Zlib:BOOL=ON                                       \
        -DTPL_ENABLE_QT:BOOL=OFF                                        \
        -DTPL_ENABLE_Matio=OFF                                          \
        -DTPL_ENABLE_GLM=OFF                                            \
        ..
#       -DTPL_ENABLE_SCALAPACK:BOOL=ON                                  \
#       -DSCALAPACK_LIBRARY_DIRS:PATH="${MKLROOT}/lib/intel64"          \
#       -DSCALAPACK_LIBRARY_NAMES:STRING="mkl_rt"                       \
#       -DTPL_ENABLE_BLACS:BOOL=ON                                      \
#       -DBLACS_LIBRARY_DIRS:PATH="$MKLROOT/lib/intel64"                \
#       -DBLACS_INCLUDE_DIRS:PATH="$MKLROOT/include"                    \
#       -DBLACS_LIBRARY_NAMES:STRING="mkl_rt"                           \

make %{?_smp_mflags} VERBOSE=1
cd ..

%install
%ohpc_setup_compiler
cd tmp
make %{?_smp_mflags} DESTDIR=%{buildroot} install INSTALL='install -p'
cd ..

# OpenHPC module file
%{__mkdir_p} %{buildroot}%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}
%{__cat} << EOF > %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}/%{version}
#%Module1.0#####################################################################

proc ModulesHelp { } {

puts stderr " "
puts stderr "This module loads the %{pname} library built with the %{compiler_family} compiler"
puts stderr "toolchain and the %{mpi_family} MPI stack."
puts stderr "\nVersion %{version}\n"

}
module-whatis "Name: %{pname} built with %{compiler_family} compiler and %{mpi_family} MPI"
module-whatis "Version: %{version}"
module-whatis "Category: runtime library"
module-whatis "Description: %{summary}"
module-whatis "URL %{url}"

set     version                     %{version}

prepend-path    PATH                %{install_path}/bin
prepend-path    INCLUDE             %{install_path}/include
prepend-path    LD_LIBRARY_PATH     %{install_path}/lib

setenv          %{PNAME}_DIR        %{install_path}
setenv          %{PNAME}_BIN        %{install_path}/bin
setenv          %{PNAME}_INC        %{install_path}/include
setenv          %{PNAME}_LIB        %{install_path}/lib

# Autoload openblas for gnu builds
if [ expr [ module-info mode load ] || [module-info mode display ] ] {
    if { ![is-loaded intel] } {
        if { ![is-loaded openblas]  } {
          module load openblas
        }
    }
}

EOF

%{__cat} << EOF > %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}-%{mpi_family}/%{pname}/.version.%{version}
#%Module1.0#####################################################################
##
## version file for %{pname}-%{version}
##
set     ModulesVersion      "%{version}"
EOF

%{__mkdir_p} %{buildroot}/%_docdir

%files
%defattr(-,root,root,-)
%{OHPC_HOME}
%{OHPC_PUB}
%doc Copyright.txt INSTALL LICENSE README RELEASE_NOTES

%changelog
* Tue May 23 2017 Adrian Reber <areber@redhat.com> - 12.10.1-1
- Remove separate mpi setup; it is part of the %%ohpc_compiler macro

* Fri May 12 2017 Karl W Schulz <karl.w.schulz@intel.com> - 12.10.1-0
- switch to use of ohpc_compiler_dependent and ohpc_mpi_dependent flags

* Wed Feb 22 2017 Adrian Reber <areber@redhat.com> - 12.10.1-0
- Switching to %%ohpc_compiler macro
