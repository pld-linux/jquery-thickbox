Summary:	ThickBox
Name:		jquery-thickbox
Version:	3.1
Release:	3
License:	MIT / GPL
Group:		Applications/WWW
Source0:	http://jquery.com/demo/thickbox/thickbox-code/thickbox.js
# Source0-md5:	1ef1a46c2b1b984cdc3332eb74bad1d5
Source1:	http://jquery.com/demo/thickbox/thickbox-code/thickbox.css
# Source1-md5:	9b2903ebee6d54b3e63ba927ea5dd498
Source2:	http://jquery.com/demo/thickbox/images/loadingAnimation.gif
# Source2-md5:	c33734a1bf58bec328ffa27872e96ae1
URL:		http://jquery.com/demo/thickbox/
Patch0:		no-global-css.patch
Patch1:		no-doctype.patch
Patch2:		animation-url.patch
Patch3:		hide-peek-trough-obj.patch
BuildRequires:	rpmbuild(macros) > 1.268
BuildRequires:	yuicompressor
Requires:	jquery
Requires:	webapps
Requires:	webserver(alias)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{name}

%description
ThickBox is a webpage UI dialog widget written in JavaScript on top of
the jQuery library. Its function is to show a single image, multiple
images, inline content, iframed content, or content served through
AJAX in a hybrid modal.

%prep
%setup -qcT
cp -a %{SOURCE0} .
cp -a %{SOURCE1} .
cp -a %{SOURCE2} .
%patch0 -p1
%patch1 -p0
%patch2 -p1
%patch3 -p0

# apache1/apache2 conf
cat > apache.conf <<'EOF'
Alias /js/thickbox %{_appdir}
<Directory %{_appdir}>
	Allow from all
</Directory>
EOF

# lighttpd conf
cat > lighttpd.conf <<'EOF'
alias.url += (
    "/js/thickbox" => "%{_appdir}",
)
EOF

%build
for a in *.js; do
	yuicompressor --charset UTF-8 --type js $a -o tmp
	mv tmp $a
done
for a in *.css; do
	yuicompressor --charset UTF-8 --type css $a -o tmp
	mv tmp $a
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}}
cp -a *.js *.css *.gif $RPM_BUILD_ROOT%{_appdir}

cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -a lighttpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%files
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%{_appdir}
