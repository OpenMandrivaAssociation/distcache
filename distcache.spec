%define	major 1
%define libname %mklibname %{name} %{major}
%define develname %mklibname -d %{name}

Summary:	Programs to provide a distributed session caching architecture
Name:		distcache
Version:	1.5.1
Release:	%mkrel 14
License:	LGPL
Group:		System/Servers
URL:		http://www.distcache.org/
Source0:	http://prdownloads.sourceforge.net/distcache/%{name}-%{version}.tar.bz2
Source1:	dc_server.init
Source2:	dc_client.init
Patch0:		distcache-limits.diff
Patch1:		distcache-libdeps.diff
Patch2:		distcache-1.5.1-autopoo_fixes.diff
BuildRequires:	openssl-devel
BuildRequires:	chrpath
BuildRequires:	automake1.7
BuildRequires:	autoconf2.5
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This package provides tools from the distcache project to deploy a distributed
session caching environment. This is most notably useful for SSL/TLS session
caching with supported OpenSSL-based applications. The caching protocol and API
is independent of SSL/TLS specifics and could be useful in other (non-SSL/TLS)
circumstances.

%package	server
Summary:	Distributed session cache server
Group:		System/Servers
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	server
dc_server runs a cache server and starts listening on a configurable network
address for connections. Incoming connections are expected to communicate using
the distcache protocol, and would typically be instances of dc_client running
on other machines.

%package	client
Summary:	Distributed session cache client proxy
Group:		System/Servers
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description	client
dc_client runs a client proxy to provide access to a remote cache server
(typically over TCP/IPv4) by providing a local service (typically over unix
domain sockets). It starts listening on a configurable network address for
connections and establishes a persistent connection to an instance of dc_server
for proxying cache operations to. Incoming connections are expected to
communicate using the distcache protocol, and would typically be applications
using one of the distcache APIs in libdistcache to encapsulate these
communications.

The common use of dc_client is to run as a local agent on each host machine
that requires use of the distributed cache, as the listening address should
probably use unix domain sockets which are better suited to frequent (and
temporary) connections being used for individual cache operations. Likewise,
the connection dc_client makes to the cache server (dc_server) for proxying
cache operations is typically over a genuine network to remote machine, using
TCP/IPv4.

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n	%{libname}
This package provides tools from the distcache project to deploy a distributed
session caching environment. This is most notably useful for SSL/TLS session
caching with supported OpenSSL-based applications. The caching protocol and API
is independent of SSL/TLS specifics and could be useful in other (non-SSL/TLS)
circumstances.

%package -n	%{develname}
Summary:	Libraries and header files for building distcache-compatible software
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{libname}-devel = %{version}
Obsoletes:	%{libname}-devel
Provides:	%{name}-devel = %{version}
Obsoletes:	%{name}-devel

%description -n	%{develname}
This package includes the libraries and header files from the distcache project
that are required to compile
distcache-compatible software.

%package	utils
Summary:	Utilities for testing and benchmarking %{name} SSL/TLS servers
Group:		System/Servers
Requires:	%{libname} = %{version}

%description	utils
 o dc_snoop - Distributed session cache traffic analysis.
 o dc_test - Distributed session cache testing and benchmarking tool.
 o nal_test - benchmarking and self-testing libnal program.
 o piper - Test file-descriptor based addresses.
 o sslswamp - SSL/TLS load-tester based on OpenSSL.

%prep

%setup -q -n %{name}-%{version}
%patch0 -p0
%patch1 -p1
%patch2 -p1

cp %{SOURCE1} dc_server.init
cp %{SOURCE2} dc_client.init

%build
%serverbuild

export WANT_AUTOCONF_2_5=1

# bootstrap it (bootstrap.sh won't cut it...)
libtoolize --copy --force; aclocal-1.7; autoheader; autoconf; automake-1.7 --foreign --add-missing

pushd ssl
    libtoolize --copy --force; aclocal-1.7; autoheader; autoconf; automake-1.7 --foreign --add-missing
popd

export CFLAGS="$CFLAGS -fPIC"

%configure2_5x \
    --enable-shared \
    --enable-static \
    --enable-ssl \
    --enable-swamp \
    --with-ssl=%{_prefix}
%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall

install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}

install -m755 dc_server.init %{buildroot}%{_initrddir}/dc_server
install -m755 dc_client.init %{buildroot}%{_initrddir}/dc_client

mv %{buildroot}%{_bindir}/dc* %{buildroot}%{_sbindir}/
mv %{buildroot}%{_bindir}/nal* %{buildroot}%{_sbindir}/

# delete rpath
chrpath -d %{buildroot}%{_bindir}/sslswamp

%post server
%_post_service dc_server

%preun server
%_preun_service dc_server

%post client
%_post_service dc_client

%preun client
%_preun_service dc_client

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files server
%defattr(-,root,root,0755)
%doc ANNOUNCE BUGS CHANGES FAQ README
%attr(0755,root,root) %{_initrddir}/dc_server
%attr(0755,root,root) %{_sbindir}/dc_server
%{_mandir}/man1/dc_server.1*
%{_mandir}/man8/distcache.8*

%files client
%defattr(-,root,root,0755)
%doc ANNOUNCE BUGS CHANGES FAQ README
%attr(0755,root,root) %{_initrddir}/dc_client
%attr(0755,root,root) %{_sbindir}/dc_client
%{_mandir}/man1/dc_client.1*

%files utils
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/piper
%attr(0755,root,root) %{_bindir}/sslswamp
%attr(0755,root,root) %{_sbindir}/dc_snoop
%attr(0755,root,root) %{_sbindir}/*_test
%attr(0755,root,root) %{_sbindir}/nal_echo
%attr(0755,root,root) %{_sbindir}/nal_ping
%attr(0755,root,root) %{_sbindir}/nal_hose
%attr(0755,root,root) %{_sbindir}/nal_pong
%attr(0755,root,root) %{_sbindir}/nal_proxy
%{_datadir}/swamp
%{_mandir}/man1/sslswamp.1*
%{_mandir}/man1/dc_snoop.1*
%{_mandir}/man1/dc_test.1*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.*

%files -n %{develname}
%defattr(-,root,root)
%{_includedir}/libnal
%{_includedir}/distcache
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a
%{_mandir}/man2/*.2*
