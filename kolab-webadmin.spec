%define snap 20050910

%define kolab_webroot /var/www/html/kolab
%define kolab_version 1.9.5

%define _requires_exceptions pear(

Summary:	Kolab Groupware Web Administration
Name:		kolab-webadmin
License:	GPL
Version:	0.4.9
Release:	%mkrel 0.%{snap}.2
Group:		System/Servers
URL:		http://www.kolab.org
Source0:	%{name}-%{version}-%{snap}.tar.bz2
Source1:	Mandriva
Patch0:		kolab-webadmin-0.4.9-antibork.diff
Patch1:		kolab-webadmin-0.4.9-italian_locales_too.diff
# $PHP_SELF only exists if register_globals = on, so let's 
# use $_SERVER['PHP_SELF'] instead
Patch2:		kolab-webadmin-0.4.9-phpself.patch
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Requires(pre):	rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.0.54 apache-mpm-prefork >= 2.0.54 apache-mod_php
Requires(pre):	kolab >= 1.9.5
Requires:	kolab >= 1.9.5
Requires:	apache-conf >= 2.0.54 apache-mpm-prefork >= 2.0.54 apache-mod_php
Requires:	php-smarty php-pear-Net_Sieve
Requires:	locales-de locales-fr locales-it locales-nl
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
This package contains the Kolab Web Administration.

%prep

%setup -q -n kolab-webadmin
rm -rf CVS
mv kolab-webadmin/* .

%patch0 -p1
%patch1 -p0
%patch2 -p1

# fix attribs
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;
	
# cleanup
for i in `find . -type d -name CVS`  `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# fix one /kolab borky thing
find . -type f|xargs perl -p -i -e "s|/kolab/bin/perl|%{_bindir}/perl|g"

# fix version
perl -pi -e "s|\@kolab_version\@|%{kolab_version}|g" www/admin/kolab/versions.php

mkdir -p dist_conf
cp %{SOURCE1} dist_conf/Mandriva

%build

touch NEWS README AUTHORS ChangeLog
autoreconf -f -i

%configure \
    --enable-wsdocrootdir=%{kolab_webroot} \
    --enable-phpdir=/var/www/php/kolab \
    --enable-dist=Mandriva

make

%install
rm -rf %{buildroot}

%makeinstall_std \
    webserver_usr=`id -un`

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/
cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf <<EOF
php_value include_path '.:%{_datadir}/pear:%{kolab_webroot}:%{_datadir}/smarty'
EOF

install -d %{buildroot}%{kolab_webroot}/admin/include
install -d %{buildroot}%{kolab_webroot}/admin/locale
install -d %{buildroot}%{kolab_webroot}/admin/templates
install -d %{buildroot}%{kolab_webroot}/admin/templates_c

mv %{buildroot}/var/www/php/kolab/admin/include/* %{buildroot}%{kolab_webroot}/admin/include/
mv %{buildroot}/var/www/php/kolab/admin/locale/* %{buildroot}%{kolab_webroot}/admin/locale/
mv %{buildroot}/var/www/php/kolab/admin/templates/* %{buildroot}%{kolab_webroot}/admin/templates/

cat > %{buildroot}%{kolab_webroot}/admin/include/config.php << EOF
<?php
\$topdir = '/kolab/admin';
\$kolab_prefix = '';
\$php_dir = '%{kolab_webroot}/admin';
\$locale_dir = '%{kolab_webroot}/admin/locale/';
?>
EOF

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
%doc ChangeLog COPYING
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%dir %attr(0755,apache,apache) %{kolab_webroot}/admin/templates_c
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



