#
# Conditional build:
%bcond_without	legacy		# do not build legacy webserver alias

Summary:	ThickBox
Name:		jquery-thickbox
Version:	3.1
Release:	9
License:	MIT / GPL
Group:		Applications/WWW
Source0:	http://jquery.com/demo/thickbox/thickbox-code/thickbox.js
# Source0-md5:	1ef1a46c2b1b984cdc3332eb74bad1d5
Source1:	http://jquery.com/demo/thickbox/thickbox-code/thickbox.css
# Source1-md5:	9b2903ebee6d54b3e63ba927ea5dd498
Source2:	http://jquery.com/demo/thickbox/images/loadingAnimation.gif
# Source2-md5:	c33734a1bf58bec328ffa27872e96ae1
Source3:	http://jquery.com/demo/thickbox/images/macFFBgHack.png
# Source3-md5:	6e63d8058c61e28953cc285de8d5c37d
URL:		http://jquery.com/demo/thickbox/
Patch0:		no-global-css.patch
Patch1:		no-doctype.patch
Patch2:		animation-url.patch
Patch3:		hide-peek-trough-obj.patch
Patch4:		translation.patch
BuildRequires:	js
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	yuicompressor
Requires:	jquery >= 1.2.6-2
Requires:	webapps
Requires:	webserver(alias)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/jquery/thickbox
%define		_legacydir	%{_datadir}/%{name}

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
cp -a %{SOURCE3} .
%patch0 -p1
%patch1 -p0
%patch2 -p1
%patch3 -p0
%patch4 -p0

# Apache 1.3 / Apache 2.x config
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
install -d build
for js in *.js; do
	yuicompressor --charset UTF-8 --type js $js -o build/$js
	js -C -f build/$a
done
for css in *.css; do
	yuicompressor --charset UTF-8 --type css $css -o build/$css
done
cp -a *.gif *.png build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_appdir}
cp -a build/* $RPM_BUILD_ROOT%{_appdir}

%if %{with legacy}
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_legacydir}}
cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -a lighttpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf
for a in $RPM_BUILD_ROOT%{_appdir}/*; do
	ln -s %{_appdir}/$(basename $a) $RPM_BUILD_ROOT%{_legacydir}
done
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with legacy}
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
%endif

%files
%defattr(644,root,root,755)
%{_appdir}

%if %{with legacy}
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%{_legacydir}
%endif
