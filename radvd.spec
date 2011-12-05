%define RADVD_UID 75
Summary:    A Router Advertisement daemon
Name:       radvd
Version:    1.6
Release:    1%{?dist}
# The code includes the advertising clause, so it's GPL-incompatible
License:    BSD with advertising
Group:      System Environment/Daemons
URL:        http://www.litech.org/radvd/
Source:     http://www.litech.org/radvd/dist/%{name}-%{version}.tar.gz
Requires(postun):   chkconfig, /usr/sbin/userdel, initscripts
Requires(preun):    chkconfig, initscripts
Requires(post):     chkconfig
Requires(pre):      /usr/sbin/useradd
BuildRequires:      flex, byacc
BuildRoot:          %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Patch1: radvd-1.5-lsb.patch

%description
radvd is the router advertisement daemon for IPv6.  It listens to router
solicitations and sends router advertisements as described in "Neighbor
Discovery for IP Version 6 (IPv6)" (RFC 2461).  With these advertisements
hosts can automatically configure their addresses and some other
parameters.  They also can choose a default router based on these
advertisements.

Install radvd if you are setting up IPv6 network and/or Mobile IPv6
services.

%prep
%setup -q

%patch1 -p1 -b .lsb

%build
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIE -fno-strict-aliasing"
export LDFLAGS='-pie -Wl,-z,relro,-z,now,-z,noexecstack,-z,nodlopen'
%configure --with-pidfile=/var/run/radvd/radvd.pid
make
# make %{?_smp_mflags} 
# Parallel builds still fail because seds that transform y.tab.x into
# scanner/gram.x are not executed before compile of scanner/gram.x
#

%install
[ $RPM_BUILD_ROOT != "/" ] && rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
mkdir -p $RPM_BUILD_ROOT/var/run/radvd

install -m 644 redhat/radvd.conf.empty $RPM_BUILD_ROOT%{_sysconfdir}/radvd.conf
install -m 755 redhat/radvd.init $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/radvd
install -m 644 redhat/radvd.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/radvd

%clean
[ $RPM_BUILD_ROOT != "/" ] && rm -rf $RPM_BUILD_ROOT

%postun
if [ "$1" -ge "1" ]; then
    /sbin/service radvd condrestart >/dev/null 2>&1
fi

%post
/sbin/chkconfig --add radvd

%preun
if [ $1 = 0 ]; then
   /sbin/service radvd stop >/dev/null 2>&1
   /sbin/chkconfig --del radvd
fi

%pre
getent group radvd >/dev/null || groupadd -g %RADVD_UID -r radvd
getent passwd radvd >/dev/null || \
  useradd -r -u %RADVD_UID -g radvd -d / -s /sbin/nologin -c "radvd user" radvd
exit 0

%files
%defattr(-,root,root,-)
%doc COPYRIGHT README CHANGES INTRO.html TODO
%config(noreplace) %{_sysconfdir}/radvd.conf
%config(noreplace) /etc/sysconfig/radvd
%{_sysconfdir}/rc.d/init.d/radvd
%dir %attr(-,radvd,radvd) /var/run/radvd/
%doc radvd.conf.example
%{_mandir}/*/*
%{_sbindir}/radvd
%{_sbindir}/radvdump

%changelog
* Wed Jun 09 2010 Jiri Skala <jskala@redhat.com> - 1.6-1
- Resolves: #602110 - Re-base to latest upstream version radvd-1.6

* Fri May 21 2010 Jiri Skala <jskala@redhat.com> - 1.5-5
- Resolves: #594399 - wrong users and groups creation in spec file
- Resolves: #594329 - RPMdiff run failed

* Thu Apr 22 2010 Jiri Skala <jskala@redhat.com> - 1.5-4
- Resolves: #584411 - radvd initscript improvement

* Fri Feb 19 2010 Jiri Skala <jskala@redhat.com> - 1.5-3
- Resolves: #543948 - replaced initdir define by sysconfdir 

* Fri Jan 29 2010 Jiri Skala <jskala@redhat.com> - 1.5-2
- Resolves: #555835 - spec and initscript modifications makes rpmlint more silent

* Thu Jan 14 2010 Jiri Skala <jskala@redhat.com> - 1.5-1
- Resolves: #555348 - radvd eats 100% CPU after interface comes back
- Resolves: #555352 - radvd[11524]: sendmsg: Bad file descriptor
- updated to latest upstream version - fixes bug #555348

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.3-2.1
- Rebuilt for RHEL 6

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 10 2009 Jiri Skala <jskala@redhat.com> - 1.3-1
- updated to latest upstream version

* Wed Jun 03 2009 Jiri Skala <jskala@redhat.com> - 1.2-3
- changed echos to be able to accept localization

* Tue Apr 28 2009 Jiri Skala <jskala@redhat.com> - 1.2-2
- fixed ambiguous condition in init script (exit 4)

* Mon Apr 27 2009 Jiri Skala <jskala@redhat.com> - 1.2-1
- updated to latest upstream version

* Fri Feb 27 2009 Jiri Skala <jskala@redhat.com> - 1.1-8
- regenerated posix patch

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 02 2009 Jiri Skala <jskala@redhat.com> - 1.1-6
- init script modified to be POSIX compliant

* Wed Sep  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.1-5
- fix license tag

* Mon Jun 23 2008 Jiri Skala <jskala@redhat.com> - 1.1-4
- radvd.init LSB compliant

* Fri Apr 11 2008 Martin Nagy <mnagy@redhat.com> - 1.1-3
- remove stale pid file on start

* Mon Feb 25 2008 Martin Nagy <mnagy@redhat.com> - 1.1-2
- fix up string comparison in init script (#427047)

* Mon Feb 25 2008 Martin Nagy <mnagy@redhat.com> - 1.1-1
- update to new upstream version
- remove patch fixed in upstream: initscript

* Mon Feb 11 2008 Martin Nagy <mnagy@redhat.com> - 1.0-6
- rebuild for gcc-4.3

* Tue Nov 13 2007 Martin Bacovsky <mbacovsk@redhat.com> - 1.0-5
- resolves #376081: The radvd init script exits without doing anything if /usr/sbin/radvd exists

* Thu Aug 23 2007 Martin Bacovsky <mbacovsk@redhat.com> - 1.0-4.1
- Rebuild

* Fri Aug  3 2007 Martin Bacovsky <mbacovsk@redhat.com> - 1.0-4
- resolves: #247041: Initscript Review

* Wed Feb 14 2007 Martin Bacovsky <mbacovsk@redhat.com> - 1.0-3
- specfile cleanup for review

* Thu Feb  1 2007 Martin Bacovsky <mbacovsk@redhat.com> - 1.0-2
- linking with -pie flag turned on again

* Wed Jan 31 2007 Martin Bacovsky <mbacovsk@redhat.com> - 1.0-1
- rebase to upstream 1.0
- Resolves: #225542: radvd 1.0 released

* Fri Aug 18 2006 Jesse Keating <jkeating@redhat.com> - 0.9.1-4
- rebuilt with latest binutils to pick up 64K -z commonpagesize on ppc*
  (#203001)

* Mon Jul 17 2006 Jason Vas Dias <jvdias@redhat.com> - 0.9.1-3
- rebuild for new FC-6 build environment

* Mon Jun 05 2006 Jason Vas Dias <jvdias@redhat.com> - 0.9.1-2
- fix BuildRequires for Mock

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.9.1-1.1.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jason Vas Dias <jvdias@redhat.com> - 0.9.1-1.1
- rebuild for new gcc, glibc, glibc-kernheaders

* Mon Jan 16 2006 Jason Vas Dias<jvdias@redhat.com> - 0.9.1-1
- Upgrade to upstream version 0.9.1

* Sun Dec 18 2005 Jason Vas Dias<jvdias@redhat.com>
- Upgrade to upstream version 0.9

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Jul 18 2005 Jason Vas Dias <jvdias@redhat.com> 0.8.2.FC5
- fix bug 163593: must use '%%configure' to get correct conf file location

* Mon Jul 18 2005 Jason Vas Dias <jvdias@redhat.com> 0.8-1.FC5
- Upgrade to upstream version 0.8

* Fri Jul  8 2005 Pekka Savola <pekkas@netcore.fi> 0.8-1
- 0.8.
- Ship the example config file as %%doc (Red Hat's #159005)

* Fri Feb 25 2005 Jason Vas Dias <jvdias@redhat.com> 0.7.3-1_FC4
- make version compare > that of FC3

* Mon Feb 21 2005 Jason Vas Dias <jvdias@redhat.com> 0.7.3-1
- Upgrade to radvd-0.7.3
- add execshield -fPIE / -pie compile / link options

* Mon Feb 21 2005 Pekka Savola <pekkas@netcore.fi> 0.7.3-1
- 0.7.3.

* Mon Oct 28 2002 Pekka Savola <pekkas@netcore.fi>
- 0.7.2.

* Tue May  7 2002 Pekka Savola <pekkas@netcore.fi>
- remove '-g %%{RADVD_GID}' when creating the user, which may be problematic
  if the user didn't exist before.

* Fri Apr 12 2002 Bernhard Rosenkraenzer <bero@redhat.com> 0.7.1-1
- 0.7.1 (bugfix release, #61023), fixes:
  - Check that forwarding is enabled when starting radvd
    (helps avoid odd problems) 
  - Check configuration file permissions (note: in setuid operation, must not
    be writable by the user.group) 
  - Cleanups and enhancements for radvdump
  - Ensure NULL-termination with strncpy even with overlong strings
    (non-criticals, but better safe than sorry) 
  - Update config.{guess,sub} to cope with some newer architectures 
  - Minor fixes and cleanups 

* Wed Jan 14 2002 Pekka Savola <pekkas@netcore.fi>
- 0.7.1.

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue Jan  8 2002 Pekka Savola <pekkas@netcore.fi>
- Change 'reload' to signal HUP to radvd instead or restarting.

* Fri Dec 28 2001 Pekka Savola <pekkas@netcore.fi>
- License unfortunately is BSD *with* advertising clause, so to be pedantic,
  change License: to 'BSD-style'.

* Thu Nov 22 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- 0.7.0

* Wed Nov 14 2001 Pekka Savola <pekkas@netcore.fi>
- spec file cleanups
- update to 0.7.0.

* Mon Jul  9 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- initial Red Hat Linux build

* Sun Jun 24 2001 Pekka Savola <pekkas@netcore.fi>
- add a patch from USAGI for overflow, Copyright -> License.

* Wed Jun 20 2001 Pekka Savola <pekkas@netcore.fi>
- use /sbin/service.
- update to 0.6.2pl4.

* Sat Apr 28 2001 Pekka Savola <pekkas@netcore.fi>
- update to 0.6.2pl3.

* Wed Apr 11 2001 Pekka Savola <pekkas@netcore.fi>
- update to 0.6.2pl2.

* Wed Apr  4 2001 Pekka Savola <pekkas@netcore.fi>
- update to 0.62pl1.  Bye bye patches!
- Require: initscripts (should really be with a version providing IPv6)
- clean up the init script, make condrestart work properly
- Use a static /etc/rc.d/init.d; init.d/radvd required it anyway.

* Sun Apr  1 2001 Pekka Savola <pekkas@netcore.fi>
- add patch to chroot (doesn't work well yet, as /proc is used directly)
- clean up droproot patch, drop the rights earlier; require user-writable
pidfile directory
- set up the pidfile directory at compile time.

* Sat Mar 31 2001 Pekka Savola <pekkas@netcore.fi>
- add select/kill signals patch from Nathan Lutchansky <lutchann@litech.org>.
- add address syntax checked fix from Marko Myllynen <myllynen@lut.fi>.
- add patch to check the pid file before fork.
- add support for OPTIONS sourced from /etc/sysconfig/radvd, provide a nice
default one.
- add/delete radvd user, change the pidfile to /var/run/radvd/radvd.pid.
- fix initscript NETWORKING_IPV6 check.

* Sun Mar 18 2001 Pekka Savola <pekkas@netcore.fi>
- add droproot patch, change to nobody by default (should use radvd:radvd or
the like, really).

* Mon Mar  5 2001 Tim Powers <timp@redhat.com>
- applied patch supplied by Pekka Savola in #30508
- made changes to initscript as per Pekka's suggestions

* Thu Feb 15 2001 Tim Powers <timp@redhat.com>
- needed -D_GNU_SOURCE to build properly

* Tue Feb  6 2001 Tim Powers <timp@redhat.com>
- use %%configure and %%makeinstall, just glob the manpages, cleans
  things up
- fixed initscript so that it can be internationalized in the future

* Fri Feb 2 2001 Pekka Savola <pekkas@netcore.fi>
- Create a single package(source) for glibc21 and glibc22 (automatic
Requires can handle this just fine).
- use %%{_mandir} and friends
- add more flesh to %%doc
- streamline %%config file %%attrs
- streamline init.d file a bit:
   * add a default chkconfig: (default to disable for security etc. reasons; 
     also, the default config isn't generic enough..)
   * add reload/condrestart
   * minor tweaks
   * missing: localization support (initscripts-5.60)
- use %%initdir macro

* Thu Feb 1 2001 Lars Fenneberg <lf@elemental.net>
- updated to new release 0.6.2

* Thu Feb 1 2001 Marko Myllynen <myllynen@lut.fi>
- initial version, radvd version 0.6.1
