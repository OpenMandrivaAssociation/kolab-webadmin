%define kolab_version		2.2.4
%define _requires_exceptions 	pear(/usr/share/php/smarty/Smarty.class.php)\\|pear(/etc/kolab/session_vars.php)
%define kolab_webroot 		/var/www/html/kolab
%define kolab_statedir		/var/www/html/kolab


Summary:	Kolab Groupware Server Web Administration Interface
Name:		kolab-webadmin
License:	GPL
Version:	%{kolab_version}
Release:	%mkrel 6
Group:		System/Servers
URL:		http://kolab.org/cgi-bin/viewcvs-kolab.cgi/server/kolab-webadmin/
Source0:	%{name}-%{version}.tar.gz
Source1:	mandriva
Source2:	bootstrap
Patch0:		mandriva.diff
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Requires(pre):	rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.4
Requires(pre):	apache-mpm >= 2.2.4
Requires(pre):	apache-mod_php
Requires(pre):	kolab >= %{kolab_version}
Requires:	apache-conf >= 2.2.4
Requires:	apache-mod_dav >= 2.2.4
Requires:	apache-mod_ldap >= 2.2.4
Requires:	apache-mod_php
Requires:	apache-mod_ssl >= 2.2.4
Requires:	apache-mpm >= 2.2.4
Requires:	kolab >= %{kolab_version}
Requires:	locales-de
Requires:	locales-es
Requires:	locales-fr
Requires:	locales-it
Requires:	locales-nl
Requires:	php-dba >= 5.2.2
Requires:	php-gettext >= 5.2.2
Requires:	php-imap >= 5.2.2
Requires:	php-ldap >= 5.2.2
Requires:	php-pear-Net_Sieve
Requires:	php-xml >= 5.2.2
Requires:	php-smarty2
BuildArch:	noarch




%description
Web based administration interface for The Kolab Groupware Server.

%prep

%setup -q -n %{name}-%{version}
%patch0 -p0


# the main config file
find -type f | xargs perl -pi -e "s|\@kolab_php_module_prefix\@admin/include/config\.php|%{_sysconfdir}/kolab/webadmin/config\.php|g"
find -type f | xargs perl -pi -e "s|require_once\(\'config\.php\'\)\;|require_once\(\'%{_sysconfdir}/kolab/webadmin/config\.php\'\)\;|g"

# the Smarty config file and other related stuff...
find -type f | xargs perl -pi -e "s|require_once\(\'\@kolab_php_smarty_prefix\@/Smarty\.class\.php\'\)\;|require_once\(\'%{_datadir}/php/smarty/Smarty\.class\.php\'\)\;|g" 
find -type f | xargs perl -pi -e "s|require_once\(\'mysmarty\.php\'\)\;|require_once\(\'%{_sysconfdir}/kolab/webadmin/mysmarty\.php\'\)\;|g"
find -type f | xargs perl -pi -e "s|require_once\(\'\@kolab_php_module_prefix\@admin/include/mysmarty\.php\'\)\;|require_once\(\'%{_sysconfdir}/kolab/webadmin/mysmarty\.php\'\)\;|g"

find -type f | xargs perl -pi -e "s|\\\$php_dir/\@kolab_php_module_prefix\@admin/|%{kolab_webroot}/admin/|g"
perl -pi -e "s|\\\$basedir\.\'templates_c/\'\;|\'%{_localstatedir}/lib/kolab/webadmin/templates_c/\'\;|g" php/admin/include/mysmarty.php.in
perl -pi -e "s|\\\$basedir\.\'configs/\'\;|\'%{_sysconfdir}/kolab/webadmin/smarty/\'\;|g" php/admin/include/mysmarty.php.in

# hard code some paths
find -type f | xargs perl -pi -e "s|\@kolab_php_module_prefix\@admin/include/|%{kolab_webroot}/admin/include/|g"
find -type f | xargs perl -pi -e "s|%{kolab_webroot}/admin/include/mysmarty\.php|%{_sysconfdir}/kolab/webadmin/mysmarty\.php|g"
find -type f | xargs perl -pi -e "s|require_once\(\'locale\.php\'\)\;|require_once\(\'%{kolab_webroot}/admin/include/locale\.php\'\)\;|g"
find -type f | xargs perl -pi -e "s|require_once\(\'mysmarty\.php\'\)|require_once\(\'%{_sysconfdir}/kolab/webadmin/mysmarty\.php\'\)|g"



%build

touch README
autoreconf -fi

%configure  \
	--with-dist=mandriva \
	--with-openpkg=no

%{__make}



%install
%__sed -i "s/@kolab_version@/%{version} \[%{_pversion}\]/" www/admin/kolab/versions.php

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/kolab/webadmin/smarty



mv %{buildroot}%{kolab_statedir}/admin/include/config.php %{buildroot}%{_sysconfdir}/kolab/webadmin/config.php
mv %{buildroot}%{kolab_statedir}/admin/include/mysmarty.php %{buildroot}%{_sysconfdir}/kolab/webadmin/mysmarty.php

install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/
cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf <<EOF
php_value include_path '.:%{_datadir}/pear:%{kolab_webroot}:%{_datadir}/smarty:%{_datadir}/kolab/php:%{_datadir}/kolab/php/horde'
EOF

# cleanup
rm -rf %{buildroot}%{_datadir}/doc/kolab

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog INSTALL NEWS
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%attr(0640,apache,apache) %config(noreplace) %{_sysconfdir}/kolab/webadmin/config.php
%attr(0640,apache,apache) %config(noreplace) %{_sysconfdir}/kolab/webadmin/mysmarty.php
%dir %attr(0755,root,root) %{_sysconfdir}/kolab/webadmin/smarty
%dir %attr(0755,apache,apache) %{_localstatedir}/lib/kolab/webadmin/templates_c
%dir %attr(0755,root,root) %{kolab_statedir}/admin
%dir %attr(0755,root,root) %{kolab_statedir}/admin/include
%dir %attr(0755,root,root) %{kolab_statedir}/admin/templates
%dir %attr(0755,root,root) %{kolab_webroot}/admin/addressbook
%dir %attr(0755,root,root) %{kolab_webroot}/admin/administrator
%dir %attr(0755,root,root) %{kolab_webroot}/admin/distributionlist
%dir %attr(0755,root,root) %{kolab_webroot}/admin/maintainer
%dir %attr(0755,root,root) %{kolab_webroot}/admin/pics
%dir %attr(0755,root,root) %{kolab_webroot}/admin/settings
%dir %attr(0755,root,root) %{kolab_webroot}/admin/sharedfolder
%dir %attr(0755,root,root) %{kolab_webroot}/admin/user
%dir %attr(0755,root,root) %{kolab_webroot}/
%{kolab_statedir}/admin/locale
%attr(0644,root,root) %{kolab_webroot}/admin/addressbook/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/administrator/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/*.css
%attr(0644,root,root) %{kolab_webroot}/admin/distributionlist/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/kolab/*.php
%attr(0644,root,root) %{kolab_statedir}/admin/include/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/maintainer/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/pics/*.png
%attr(0644,root,root) %{kolab_webroot}/*.png
%attr(0644,root,root) %{kolab_webroot}/admin/settings/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/sharedfolder/*.php
%attr(0644,root,root) %{kolab_statedir}/admin/templates/*.tpl
%attr(0644,root,root) %{kolab_webroot}/admin/user/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/domainmaintainer/*.php



%changelog
* Sun May 15 2011 Thomas Spuhler <tspuhler@mandriva.org> 2.2.4-4mdv2011.0
+ Revision: 674724
- changed Requires:php-smarty >=2.6.20 to Requires: php-smarty2 because the package doesn't work with smarty >=3

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 2.2.4-2
+ Revision: 666036
- mass rebuild

* Wed Jul 14 2010 Thomas Spuhler <tspuhler@mandriva.org> 2.2.4-1mdv2011.0
+ Revision: 553010
- Updated to upstream version 2.2.4

* Thu Jul 01 2010 Thomas Spuhler <tspuhler@mandriva.org> 2.2.3-2.1mdv2011.0
+ Revision: 549721
- added patch user.php.diff
  fixed bug # 59632
  bumped to subrelease 1

* Tue Apr 20 2010 Thomas Spuhler <tspuhler@mandriva.org> 2.2.3-2mdv2010.1
+ Revision: 536905
- changed location of sieve directory from /var/lib/sieve to /var/lib/imap/sieve
  Increase release verison to 2

* Mon Apr 12 2010 Thomas Spuhler <tspuhler@mandriva.org> 2.2.3-1mdv2010.1
+ Revision: 533617
- added missing files to source, mandriva and bootstrap
- Updated to version 2.2.3
- Updated to version 2.2.3

* Sun Sep 13 2009 Thomas Spuhler <tspuhler@mandriva.org> 2.1.0-9mdv2010.0
+ Revision: 438601
- removed the fuss=0 define
- changed path of smarty to actual 2010, by the mysmarty.php patch added the mandriva patch for a lot of other path correction and correct the path in the spec file
- changed path of smarty to actual 2010

  + Christophe Fergeau <cfergeau@mandriva.com>
    - rebuild

* Fri Sep 19 2008 Oden Eriksson <oeriksson@mandriva.com> 2.1.0-8mdv2009.0
+ Revision: 285836
- fix #42455 (kolab-webadmin-2.1.0-7mdv2009.0.noarch cannot be installed because of dependency)

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 2.1.0-7mdv2009.0
+ Revision: 222594
- fix #%%define is forbidden
- rebuild

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Sun Jan 13 2008 Thierry Vignaud <tv@mandriva.org> 2.1.0-6mdv2008.1
+ Revision: 150432
- rebuild
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Sun Sep 23 2007 Oden Eriksson <oeriksson@mandriva.com> 2.1.0-5mdv2008.0
+ Revision: 92347
- misc build fixes

* Mon Sep 10 2007 Oden Eriksson <oeriksson@mandriva.com> 2.1.0-4mdv2008.0
+ Revision: 84132
- fix #33305,#33392 (path to mysmarty.php)

* Mon Jun 25 2007 Oden Eriksson <oeriksson@mandriva.com> 2.1.0-3mdv2008.0
+ Revision: 43903
- really fix build
- fix build
- fix deps

* Fri Jun 01 2007 Oden Eriksson <oeriksson@mandriva.com> 2.1.0-2mdv2008.0
+ Revision: 33632
- new mandriva file

* Sat May 26 2007 Oden Eriksson <oeriksson@mandriva.com> 2.1.0-1mdv2008.0
+ Revision: 31492
- 2.1.0
- fixed a lot of stuff...


* Wed Oct 11 2006 Oden Eriksson <oeriksson@mandriva.com>
+ 2006-10-10 09:52:38 (63286)
- hmmm..., forgot the mkrel macro

* Wed Oct 11 2006 Oden Eriksson <oeriksson@mandriva.com>
+ 2006-10-10 09:50:04 (63284)
- rebuild

* Tue May 30 2006 Andreas Hasenack <andreas@mandriva.com>
+ 2006-05-29 08:36:37 (31646)
- renamed mdv to packages because mdv is too generic and it's hosting only packages anyway

* Sun Sep 11 2005 oeriksson
+ 2005-09-10 07:40:04 (878)
- new snap (small fixes)

* Sun Sep 11 2005 oeriksson
+ 2005-09-10 07:38:53 (877)
- new snap (small fixes)

* Sat Aug 20 2005 Andreas Hasenack <andreas@mandriva.com>
+ 2005-08-19 14:51:51 (709)
- remove references to kolab user/groups since they are
  not used in this package. Also delegate user creation to
  the main kolab package.

* Fri Aug 19 2005 Andreas Hasenack <andreas@mandriva.com>
+ 2005-08-18 13:29:35 (698)
- added phpself patch: $PHP_SELF -> $_SERVER['PHP_SELF']

* Wed Aug 17 2005 oeriksson
+ 2005-08-16 00:05:13 (651)
- added deps on locales to make language switching work

* Tue Aug 16 2005 oeriksson
+ 2005-08-15 07:03:59 (645)
- fix kolab-server/kolab renaming

* Sun Aug 14 2005 oeriksson
+ 2005-08-13 04:41:00 (628)
- fix smarter perl search and replace (works faster)
- add the kolab user and group from here because i never managed to
  make urpmi install kolab-server first...

* Sat Aug 13 2005 oeriksson
+ 2005-08-12 01:50:42 (610)
- new snap (20050812)
- fix deps
- rediff the antibork patch
- remove hardcoded path to /var/www/html/kolab
- added P1 to also install the italian locales

* Sat Aug 06 2005 Andreas Hasenack <andreas@mandriva.com>
+ 2005-08-05 07:04:29 (539)
- fixed prereq loop

* Thu Aug 04 2005 Andreas Hasenack <andreas@mandriva.com>
+ 2005-08-03 11:53:31 (524)
- added more include path fixes to the original antibork patch

* Tue Aug 02 2005 oeriksson
+ 2005-08-01 08:30:57 (487)
- use a recent cvs snap (20050801)
- fix deps
- added the Mandriva file that is used by the configure and Makefile to set certain values
- misc spec file fixes

* Sat Jul 23 2005 Andreas Hasenack <andreas@mandriva.com>
+ 2005-07-22 11:08:32 (427)
- applied Oden's latest changes

* Fri Jul 22 2005 Andreas Hasenack <andreas@mandriva.com>
+ 2005-07-21 08:14:25 (391)
- merged in Oden's changes:
  - added antibork patch
  - added requires for php-pear-Net_Sieve

* Wed Jul 13 2005 Andreas Hasenack <andreas@mandriva.com>
+ 2005-07-12 10:27:04 (364)
- added kolab-webadmin files
- packaged for Mandriva

