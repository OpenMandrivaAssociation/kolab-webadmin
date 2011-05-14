%define kolab_version		2.2.4
%define _requires_exceptions 	pear(/usr/share/php/smarty/Smarty.class.php)\\|pear(/etc/kolab/session_vars.php)
%define kolab_webroot 		/var/www/html/kolab
%define kolab_statedir		/var/www/html/kolab


Summary:	Kolab Groupware Server Web Administration Interface
Name:		kolab-webadmin
License:	GPL
Version:	%{kolab_version}
Release:	%mkrel 4
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

