%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

%define kolab_webroot /var/www/html/kolab

#%define _requires_exceptions pear(

Summary:	Kolab Groupware Server Web Administration Interface
Name:		kolab-webadmin
License:	GPL
Version:	2.1.0
Release:	%mkrel 5
Group:		System/Servers
URL:		http://www.kolab.org
Source0:	kolab-webadmin-%{version}.tar.bz2
Source1:	mandriva
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Requires(pre):	rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.4
Requires(pre):	apache-mpm >= 2.2.4
Requires(pre):	apache-mod_php
Requires(pre):	kolab >= 2.1.0
Requires:	apache-conf >= 2.2.4
Requires:	apache-mod_dav >= 2.2.4
Requires:	apache-mod_ldap >= 2.2.4
Requires:	apache-mod_php
Requires:	apache-mod_ssl >= 2.2.4
Requires:	apache-mpm >= 2.2.4
Requires:	kolab >= 2.1.0
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
Requires:	php-smarty >= 2.6.3
Requires:	php-xml >= 5.2.2
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
Web based administration interface for The Kolab Groupware Server.

%prep

%setup -q

cp %{SOURCE1} dist_conf/mandriva

# cleanup
for i in `find . -type d -name CVS`  `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# fix perl_vendordir
perl -pi -e "s|perl_vendorlib|%{perl_vendorlib}|g" dist_conf/mandriva

# the main config file
find -type f | xargs perl -pi -e "s|\@kolab_php_module_prefix\@admin/include/config\.php|%{_sysconfdir}/kolab/webadmin/config\.php|g"
find -type f | xargs perl -pi -e "s|require_once\(\'config\.php\'\)\;|require_once\(\'%{_sysconfdir}/kolab/webadmin/config\.php\'\)\;|g"

# the Smarty config file and other related stuff...
find -type f | xargs perl -pi -e "s|require_once\(\'\@kolab_php_smarty_prefix\@/Smarty\.class\.php\'\)\;|require_once\(\'%{_datadir}/smarty/Smarty\.class\.php\'\)\;|g" 
find -type f | xargs perl -pi -e "s|require_once\(\'mysmarty\.php\'\)\;|require_once\(\'%{_sysconfdir}/kolab/webadmin/mysmarty\.php\'\)\;|g"
find -type f | xargs perl -pi -e "s|require_once\(\'\@kolab_php_module_prefix\@admin/include/mysmarty\.php\'\)\;|require_once\(\'%{_sysconfdir}/kolab/webadmin/mysmarty\.php\'\)\;|g"

find -type f | xargs perl -pi -e "s|\\\$php_dir/\@kolab_php_module_prefix\@admin/|%{kolab_webroot}/admin/|g"
perl -pi -e "s|\\\$basedir\.\'templates_c/\'\;|\'%{_localstatedir}/kolab/webadmin/templates_c/\'\;|g" php/admin/include/mysmarty.php.in
perl -pi -e "s|\\\$basedir\.\'configs/\'\;|\'%{_sysconfdir}/kolab/webadmin/smarty/\'\;|g" php/admin/include/mysmarty.php.in

# hard code some paths
find -type f | xargs perl -pi -e "s|\@kolab_php_module_prefix\@admin/include/|%{kolab_webroot}/admin/include/|g"
find -type f | xargs perl -pi -e "s|%{kolab_webroot}/admin/include/mysmarty\.php|%{_sysconfdir}/kolab/webadmin/mysmarty\.php|g"
find -type f | xargs perl -pi -e "s|require_once\(\'locale\.php\'\)\;|require_once\(\'%{kolab_webroot}/admin/include/locale\.php\'\)\;|g"
find -type f | xargs perl -pi -e "s|require_once\(\'mysmarty\.php\'\)|require_once\(\'%{_sysconfdir}/kolab/webadmin/mysmarty\.php\'\)|g"

# fix one /kolab bork66y thing
find . -type f|xargs perl -p -i -e "s|/kolab/bin/perl|%{_bindir}/perl|g"

# fix version
perl -pi -e "s|\@kolab_version\@|%{version}|g" www/admin/kolab/versions.php.in

# these won't be generated from the *.in files if they exist
rm -f php/admin/templates/page.tpl
rm -f php/admin/templates/versions.tpl

%build
aclocal; autoconf; automake

%configure2_5x \
    --with-dist=mandriva

%make

%install
rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_localstatedir}/kolab/webadmin/templates_c
install -d %{buildroot}%{_sysconfdir}/kolab/webadmin/smarty

perl -pi -e "s|^\\\$topdir = .*|\\\$topdir = \'/kolab/admin\'\;|g" %{buildroot}%{kolab_webroot}/admin/include/config.php
perl -pi -e "s|^\\\$php_dir = .*|\\\$php_dir = \'%{kolab_webroot}/admin\'\;|g" %{buildroot}%{kolab_webroot}/admin/include/config.php
perl -pi -e "s|^\\\$locale_dir = .*|\\\$locale_dir = \'%{kolab_webroot}/admin/locale/\'\;|g" %{buildroot}%{kolab_webroot}/admin/include/config.php

mv %{buildroot}%{kolab_webroot}/admin/include/config.php %{buildroot}%{_sysconfdir}/kolab/webadmin/
mv %{buildroot}%{kolab_webroot}/admin/include/mysmarty.php %{buildroot}%{_sysconfdir}/kolab/webadmin/

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
%dir %attr(0755,apache,apache) %{_localstatedir}/kolab/webadmin/templates_c
%dir %attr(0755,root,root) %{kolab_webroot}/admin
%dir %attr(0755,root,root) %{kolab_webroot}/admin/addressbook
%dir %attr(0755,root,root) %{kolab_webroot}/admin/administrator
%dir %attr(0755,root,root) %{kolab_webroot}/admin/distributionlist
%dir %attr(0755,root,root) %{kolab_webroot}/admin/include
%dir %attr(0755,root,root) %{kolab_webroot}/admin/kolab
%dir %attr(0755,root,root) %{kolab_webroot}/admin/maintainer
%dir %attr(0755,root,root) %{kolab_webroot}/admin/pics
%dir %attr(0755,root,root) %{kolab_webroot}/admin/service
%dir %attr(0755,root,root) %{kolab_webroot}/admin/sharedfolder
%dir %attr(0755,root,root) %{kolab_webroot}/admin/templates
%dir %attr(0755,root,root) %{kolab_webroot}/admin/user
%dir %attr(0755,root,root) %{kolab_webroot}/admin/domainmaintainer
%{kolab_webroot}/admin/locale
%attr(0644,root,root) %{kolab_webroot}/admin/addressbook/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/administrator/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/*.css
%attr(0644,root,root) %{kolab_webroot}/admin/distributionlist/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/include/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/kolab/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/maintainer/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/pics/*.png
%attr(0644,root,root) %{kolab_webroot}/admin/pics/*.jpg
%attr(0644,root,root) %{kolab_webroot}/admin/service/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/sharedfolder/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/templates/*.tpl
%attr(0644,root,root) %{kolab_webroot}/admin/user/*.php
%attr(0644,root,root) %{kolab_webroot}/admin/domainmaintainer/*.php
%attr(0644,root,root) %{kolab_webroot}/*.ico
