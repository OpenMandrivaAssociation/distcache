%define	major 1
%define libname %mklibname %{name} %{major}
%define develname %mklibname -d %{name}

Summary:	Programs to provide a distributed session caching architecture
Name:		distcache
Version:	1.5.1
Release:	22
License:	LGPL
Group:		System/Servers
URL:		http://www.distcache.org/
Source0:	http://prdownloads.sourceforge.net/distcache/%{name}-%{version}.tar.bz2
Source1:	dc_server.init
Source2:	dc_client.init
Patch0:		distcache-limits.diff
Patch1:		distcache-libdeps.diff
Patch2:		distcache-1.5.1-autopoo_fixes.diff
Patch3:		distcache-1.5.1-cvs_fixes.diff
Patch4:		distcache-1.5.1-automake-1.13.patch
BuildRequires:	pkgconfig(openssl)
BuildRequires:	chrpath
BuildRequires:	autoconf automake libtool

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
Requires:	%{libname} >= %{version}
Provides:	%{libname}-devel = %{version}
Provides:	%{name}-devel = %{version}

%description -n	%{develname}
This package includes the libraries and header files from the distcache project
that are required to compile
distcache-compatible software.

%package	utils
Summary:	Utilities for testing and benchmarking %{name} SSL/TLS servers
Group:		System/Servers
Requires:	%{libname} = %{version}-%{release}

%description	utils
 o dc_snoop - Distributed session cache traffic analysis.
 o dc_test - Distributed session cache testing and benchmarking tool.
 o nal_test - benchmarking and self-testing libnal program.
 o piper - Test file-descriptor based addresses.
 o sslswamp - SSL/TLS load-tester based on OpenSSL.

%prep
%setup -q
%patch0 -p0
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1 -b .am113~

cp %{SOURCE1} dc_server.init
cp %{SOURCE2} dc_client.init

%build
%serverbuild

export WANT_AUTOCONF_2_5=1

# bootstrap it (bootstrap.sh won't cut it...)
libtoolize --copy --force; aclocal; autoheader; autoconf; automake --foreign --add-missing

pushd ssl
    libtoolize --copy --force; aclocal; autoheader; autoconf; automake --foreign --add-missing
popd

export CFLAGS="$CFLAGS -fPIC"

%configure2_5x \
    --enable-shared \
    --disable-static \
    --enable-ssl \
    --enable-swamp \
    --with-ssl=%{_prefix}
%make

%install
rm -rf %{buildroot}

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

%files server
%doc ANNOUNCE BUGS CHANGES FAQ README
%attr(0755,root,root) %{_initrddir}/dc_server
%attr(0755,root,root) %{_sbindir}/dc_server
%{_mandir}/man1/dc_server.1*
%{_mandir}/man8/distcache.8*

%files client
%doc ANNOUNCE BUGS CHANGES FAQ README
%attr(0755,root,root) %{_initrddir}/dc_client
%attr(0755,root,root) %{_sbindir}/dc_client
%{_mandir}/man1/dc_client.1*

%files utils
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
%{_libdir}/*.so.*

%files -n %{develname}
%{_includedir}/libnal
%{_includedir}/distcache
%{_libdir}/*.so
%{_mandir}/man2/*.2*

%changelog
* Thu Dec 08 2011 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-22
+ Revision: 738984
- drop the static libs and the libtool *.la files
- various fixes

* Mon Jun 20 2011 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-21
+ Revision: 686308
- avoid pulling 32 bit libraries on 64 bit arch

* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-20
+ Revision: 663781
- mass rebuild

* Sun Jan 02 2011 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-19mdv2011.0
+ Revision: 627569
- don't force the usage of automake1.7

* Tue Nov 23 2010 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-18mdv2011.0
+ Revision: 599853
- added cvs fixes

* Thu Apr 08 2010 Eugeni Dodonov <eugeni@mandriva.com> 1.5.1-17mdv2010.1
+ Revision: 533130
- Rebuild for new openssl

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-16mdv2010.1
+ Revision: 511560
- rebuilt against openssl-0.9.8m

* Sun Aug 09 2009 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-15mdv2010.0
+ Revision: 413358
- rebuild

* Wed Dec 17 2008 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-14mdv2009.1
+ Revision: 315219
- fix autopoo borkiness (-Werror=format-security)

* Tue Sep 02 2008 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-13mdv2009.0
+ Revision: 279063
- added lsm headers into the init scripts

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 1.5.1-12mdv2009.0
+ Revision: 264407
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Wed May 21 2008 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-11mdv2009.0
+ Revision: 209796
- reconstruct the autopoo stuff
- more overlinking fixes...
- added 2 rediffed patches from fedora

* Tue Mar 04 2008 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-11mdv2008.1
+ Revision: 178762
- rebuild

  + Thierry Vignaud <tv@mandriva.org>
    - fix spacing at top of description
    - rebuild
    - kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Sat Aug 18 2007 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-9mdv2008.0
+ Revision: 65567
- use the new devel package naming

* Sat Jun 23 2007 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-8mdv2008.0
+ Revision: 43406
- use the new %%serverbuild macro

* Thu Jun 07 2007 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-7mdv2008.0
+ Revision: 36659
- use distro conditional -fstack-protector


* Wed Oct 11 2006 Oden Eriksson <oeriksson@mandriva.com>
+ 2006-10-10 08:59:21 (63269)
- bunzip the sources

* Sat Oct 07 2006 Oden Eriksson <oeriksson@mandriva.com>
+ 2006-10-06 07:12:01 (62912)
- Import distcache

* Thu Aug 10 2006 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-5mdv2007.0
- rebuild
- mist spec file fixes

* Mon May 15 2006 Stefan van der Eijk <stefan@eijk.nu> 1.5.1-4mdk
- rebuild for sparc

* Wed Nov 16 2005 Oden Eriksson <oeriksson@mandriva.com> 1.5.1-3mdk
- rebuilt against openssl-0.9.8a

* Tue Dec 28 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 1.5.1-2mdk
- lib64 fixes

* Mon Dec 06 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 1.5.1-1mdk
- 1.5.1

* Fri May 07 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 1.5.0-1mdk
- 1.5.0

* Sun Dec 14 2003 Oden Eriksson <oden.eriksson@kvikkjokk.net> 1.4.3-0.20031214.1mdk
- use a recent snapshot
- merge the static-devel subpackage into one devel subpackage
- merge fedora stuff
- split out the server and client parts into subpackages
- made a new more generic utils subpackage
- misc spec file fixes

