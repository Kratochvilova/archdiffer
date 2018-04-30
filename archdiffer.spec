%define name archdiffer
%define version 1.1
%define unmangled_version 1.1
%define release 8

Summary: Web service for generic archive comparison
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
Url: https://github.com/Kratochvilova/archdiffer
Requires: %{name}-common, %{name}-flask-frontend, %{name}-backend

%description
UNKNOWN

%package common
Summary: %{name} common part
Requires: python3, python3-sqlalchemy
%description common
Common part for %{name}

%package flask-frontend
Summary: %{name} flask frontend
Requires: python3-flask, python3-flask-restful, python3-flask-openid, python3-celery
%description flask-frontend
Flask frontend for %{name}

%package backend
Summary: %{name} backend
Requires: python3-celery, rpmlint, python3-dnf, python3-rpm
Requires(pre): shadow-utils
%description backend
Backend for %{name}
%pre
getent group archdiffer-worker >/dev/null || groupadd -r archdiffer-worker
getent passwd archdiffer-worker >/dev/null || \
    useradd -r -g archdiffer-worker -d / -s /sbin/nologin \
    -c "Useful comment about the purpose of this account" archdiffer-worker
exit 0

%prep
%setup -n %{name}-%{unmangled_version}

%build
python3 setup-all.py build

%install
python3 setup-all.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files

%files common
%config %attr(0600, root, root) /etc/archdiffer.conf
%attr(0755, root, root) /usr/libexec/archdiffer/init_db
%attr(0755, root, root) /usr/libexec/archdiffer/init_db_rpmdiff
%{python3_sitelib}/archdiffer-*.egg-info
%{python3_sitelib}/archdiffer/*.py
%{python3_sitelib}/archdiffer/__pycache__/*
%{python3_sitelib}/archdiffer/plugins/rpmdiff/*.py
%{python3_sitelib}/archdiffer/plugins/rpmdiff/__pycache__/*

%files flask-frontend
/usr/share/archdiffer/archdiffer.wsgi
/etc/httpd/conf.d/archdiffer.conf
%{python3_sitelib}/archdiffer/flask_frontend/*.py
%{python3_sitelib}/archdiffer/flask_frontend/__pycache__/*
%{python3_sitelib}/archdiffer/flask_frontend/templates/*
%{python3_sitelib}/archdiffer/flask_frontend/static/*
%{python3_sitelib}/archdiffer/plugins/rpmdiff/flask_frontend/*.py
%{python3_sitelib}/archdiffer/plugins/rpmdiff/flask_frontend/__pycache__/*
%{python3_sitelib}/archdiffer/plugins/rpmdiff/flask_frontend/templates/*

%files backend
/lib/systemd/system/archdiffer-worker.service
%{python3_sitelib}/archdiffer/backend/*.py
%{python3_sitelib}/archdiffer/backend/__pycache__/*
%{python3_sitelib}/archdiffer/plugins/rpmdiff/worker/*.py
%{python3_sitelib}/archdiffer/plugins/rpmdiff/worker/__pycache__/*

