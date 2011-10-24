# Prevent brp-java-repack-jars from being run.
%define __jar_repack %{nil}

%global project felix
%global bundle org.apache.felix.framework
%global groupId org.apache.felix
%global artifactId %{bundle}

Name:    %{project}-framework
Version: 2.0.5
Release: 5
Summary: Apache Felix Framework

Group:   Development/Java
License: ASL 2.0
URL:     http://felix.apache.org
Source0: http://www.apache.org/dist/felix/%{bundle}-%{version}-project.tar.gz
Source1: %{name}.demap

# Remove <parent>
# Remove rat-maven-plugin
Patch0: %{bundle}-%{version}~pom.xml.patch

BuildArch: noarch

BuildRequires: java-devel >= 0:1.6.0
BuildRequires: jpackage-utils
BuildRequires: felix-osgi-compendium
BuildRequires: felix-osgi-core
BuildRequires: maven2
BuildRequires:    maven-compiler-plugin
BuildRequires:    maven-install-plugin
BuildRequires:    maven-invoker-plugin
BuildRequires:    maven-jar-plugin
BuildRequires:    maven-javadoc-plugin
BuildRequires:    maven-release-plugin
BuildRequires:    maven-resources-plugin
BuildRequires:    maven-surefire-plugin
# TODO check availability and use new names
#BuildRequires:    maven-bundle-plugin
# instead of
BuildRequires:    maven-plugin-bundle

Requires: felix-osgi-compendium
Requires: felix-osgi-core
Requires: java >= 0:1.6.0

Requires(post):   jpackage-utils
Requires(postun): jpackage-utils

%description
Apache Felix Framework Interfaces and Classes.

%package javadoc
Group:          Development/Java
Summary:        Javadoc for %{name}
Requires:       jpackage-utils

%description javadoc
API documentation for %{name}.

%global POM %{_mavenpomdir}/JPP.%{project}-%{bundle}.pom

%prep
%setup -q -n %{bundle}-%{version}
%patch0 -p1 -b .sav
# remove tests due to rat-maven-plugin is removed
%__rm -rf src/test/java/

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
%__mkdir_p $MAVEN_REPO_LOCAL
mvn-jpp -e \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven2.jpp.depmap.file="%{SOURCE1}" \
        install javadoc:javadoc

%install
# jars
install -d -m 0755 %{buildroot}%{_javadir}/%{project}
install -m 644 target/%{bundle}-%{version}.jar \
        %{buildroot}%{_javadir}/%{project}/%{bundle}.jar

%add_to_maven_depmap %{groupId} %{artifactId} %{version} JPP/%{project} %{bundle}

# poms
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml %{buildroot}%{POM}

# javadoc
install -d -m 0755 %{buildroot}%{_javadocdir}/%{name}
%__cp -pr target/site/api*/* %{buildroot}%{_javadocdir}/%{name}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :

%files
%defattr(-,root,root,-)
%{_javadir}/%{project}/*
%{POM}
%config(noreplace) %{_mavendepmapfragdir}/%{name}
%doc LICENSE

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}
%doc LICENSE

