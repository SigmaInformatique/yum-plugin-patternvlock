yum-plugin-patternvlock
=======================

Yum's plugin forcing the usage of some packages versions or excluding some others versions from a pattern list

License & Copyright
-------------------

yum-plugin-patternvlock is licensed under [GPL v2](http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt).
Please, see the [LICENSE](https://github.com/SigmaInformatique/yum-plugin-patternvlock/blob/master/LICENSE) file for details.

Packaging and installing
------------------------

To make your own package:
```
user@host# gem install easyfpm
user@host# git clone https://github.com/SigmaInformatique/yum-plugin-patternvlock.git
user@host# easyfpm --config-file yum-plugin-patternvlock/_easyfpm/easyfpm.cfg --pkg-src-dir yum-plugin-patternvlock --pkg-output-dir /tmp 
easyfpm --config-file yum-plugin-patternvlock/_easyfpm/easyfpm.cfg --pkg-src-dir yum-plugin-patternvlock --pkg-output-dir /tmp
no value for epoch is set, defaulting to nil
no value for epoch is set, defaulting to nil
Created package /tmp/easyfpm-output-dir20150826-8275-1bi6es/yum-plugin-patternvlock-0.1-1.noarch.rpm
Created package /tmp/easyfpm-output-dir20150826-8275-uospjx/yum-plugin-patternvlock-0.1-1.noarch.rpm
Package moved to /tmp/yum-plugin-patternvlock-0.1-1.el6.noarch.rpm
no value for epoch is set, defaulting to nil
no value for epoch is set, defaulting to nil
Created package /tmp/easyfpm-output-dir20150826-8275-fln2lb/yum-plugin-patternvlock-0.1-1.noarch.rpm
Package moved to /tmp/yum-plugin-patternvlock-0.1-1.el7.noarch.rpm
user@host#
```
Then, you have to deploy the wanted package(s) on your repository or on your server.

if you have your own repository:
```
[root@server# ~] yum install yum-plugin-patternvlock
```
or installing it with rpm:
```
[root@server# ~] rpm -ivh /tmp/yum-plugin-patternvlock-0.1-1.el6.noarch.rpm
```

Example of use
--------------

We have the Puppetlabs repository in our sources. We don't want puppet version 3.8, just want to stay in the 3.7 branch for the moment. However, we do not want the latest version: 3.7.5

```
[root@testinstallcentos ~]# rpm -qa puppet
puppet-3.6.2-1.el6.noarch
[root@testinstallcentos ~]# 
```

We have puppet installed and have to upgrade it (source puppetlabs repository).

```
[root@testinstallcentos ~]# yum update
Loaded plugins: security
Setting up Update Process
sigma                                                  |  951 B     00:00     
sigma-tests                                            |  951 B     00:00     
Resolving Dependencies
--> Running transaction check
---> Package puppet.noarch 0:3.6.2-1.el6 will be updated
---> Package puppet.noarch 0:3.8.2-1.el6 will be an update
--> Finished Dependency Resolution

Dependencies Resolved

==============================================================================
 Package      Arch         Version            Repository                 Size
==============================================================================
Updating:
 puppet       noarch       3.8.2-1.el6        puppetlabs-products       1.6 M

Transaction Summary
==============================================================================
Upgrade       1 Package(s)

Total download size: 1.6 M
Is this ok [y/N]: n
Exiting on user Command
Your transaction was saved, rerun it with:
 yum load-transaction /tmp/yum_save_tx-2015-09-10-09-25iEPflI.yumtx
[root@testinstallcentos ~]#
```

The 3.8.x version is not validated for us, we only want a 3.7.x version.

```
[root@testinstallcentos ~]# yum patternvlock add 'puppet-3.7.*'
Loaded plugins: patternvlock, security
patternvlock: 1 pattern(s) added
[root@testinstallcentos ~]# yum patternvlock list
Loaded plugins: patternvlock, security
puppet-3.7.*
patternvlock list done
[root@testinstallcentos ~]# cat /etc/yum/pluginconf.d/patternvlock.list

# Added pattern lock on Thu Sep 10 09:37:35 2015
puppet-3.7.*
[root@testinstallcentos ~]# 
```

Let’s look what we can have now:

```
[root@testinstallcentos ~]# yum update
Loaded plugins: patternvlock, security
Setting up Update Process
sigma                                                  |  951 B     00:00     
sigma-tests                                            |  951 B     00:00     
Resolving Dependencies
--> Running transaction check
---> Package puppet.noarch 0:3.6.2-1.el6 will be updated
---> Package puppet.noarch 0:3.7.5-1.el6 will be an update
--> Finished Dependency Resolution

Dependencies Resolved

==============================================================================
 Package      Arch         Version            Repository                 Size
==============================================================================
Updating:
 puppet       noarch       3.7.5-1.el6        puppetlabs-products       1.6 M

Transaction Summary
==============================================================================
Upgrade       1 Package(s)

Total download size: 1.6 M
Is this ok [y/N]: n
Exiting on user Command
Your transaction was saved, rerun it with:
 yum load-transaction /tmp/yum_save_tx-2015-09-10-09-38mn2o80.yumtx
[root@testinstallcentos ~]#
```

Not bad, but if we don’t want the version 3.7.5 (for example, because of a known bug)

```
[root@testinstallcentos ~]# yum patternvlock exclude 'puppet-3.7.5'
Loaded plugins: patternvlock, security
patternvlock: 1 exclusion(s) added
[root@testinstallcentos ~]# yum patternvlock list
Loaded plugins: patternvlock, security
puppet-3.7.*
!puppet-3.7.5
patternvlock list done
[root@testinstallcentos ~]# 
```

Now, let see what yum can give us.

```
[root@testinstallcentos ~]# yum update
Loaded plugins: patternvlock, security
Setting up Update Process
sigma                                                  |  951 B     00:00     
sigma-tests                                            |  951 B     00:00     
Resolving Dependencies
--> Running transaction check
---> Package puppet.noarch 0:3.6.2-1.el6 will be updated
---> Package puppet.noarch 0:3.7.4-1.el6 will be an update
--> Finished Dependency Resolution

Dependencies Resolved

==============================================================================
 Package      Arch         Version            Repository                 Size
==============================================================================
Updating:
 puppet       noarch       3.7.4-1.el6        puppetlabs-products       1.6 M

Transaction Summary
==============================================================================
Upgrade       1 Package(s)

Total download size: 1.6 M
Is this ok [y/N]: y
Downloading Packages:
puppet-3.7.4-1.el6.noarch.rpm                          | 1.6 MB     00:05     
Running rpm_check_debug
Running Transaction Test
Transaction Test Succeeded
Running Transaction
  Updating   : puppet-3.7.4-1.el6.noarch                                  1/2 
  Cleanup    : puppet-3.6.2-1.el6.noarch                                  2/2 
  Verifying  : puppet-3.7.4-1.el6.noarch                                  1/2 
  Verifying  : puppet-3.6.2-1.el6.noarch                                  2/2 

Updated:
  puppet.noarch 0:3.7.4-1.el6                                                 

Complete!
[root@testinstallcentos ~]#
```

That’s ok, we made our update, let's try if everything is ok:

```
[root@testinstallcentos ~]# yum update
Loaded plugins: patternvlock, security
Setting up Update Process
sigma                                                  |  951 B     00:00     
sigma-tests                                            |  951 B     00:00     
No Packages marked for Update
[root@testinstallcentos ~]#
```

Now, we made a mistake in our tests, we can stop the blacklist for puppet-3.7.5:

```
[root@testinstallcentos ~]# yum patternvlock list
Loaded plugins: patternvlock, security
puppet-3.7.*
!puppet-3.7.5
patternvlock list done
[root@testinstallcentos ~]# yum patternvlock delete '!puppet-3.7.5'
Loaded plugins: patternvlock, security
Deleting patternvlock for: !puppet-3.7.5
patternvlock deleted: 1
[root@testinstallcentos ~]#
```

Ok, let’s try:

```
[root@testinstallcentos ~]# yum update
Loaded plugins: patternvlock, security
Setting up Update Process
sigma                                                  |  951 B     00:00     
sigma-tests                                            |  951 B     00:00     
Resolving Dependencies
--> Running transaction check
---> Package puppet.noarch 0:3.7.4-1.el6 will be updated
---> Package puppet.noarch 0:3.7.5-1.el6 will be an update
--> Finished Dependency Resolution

Dependencies Resolved

==============================================================================
 Package      Arch         Version            Repository                 Size
==============================================================================
Updating:
 puppet       noarch       3.7.5-1.el6        puppetlabs-products       1.6 M

Transaction Summary
==============================================================================
Upgrade       1 Package(s)

Total download size: 1.6 M
Is this ok [y/N]: y
Downloading Packages:
puppet-3.7.5-1.el6.noarch.rpm                          | 1.6 MB     00:03     
Running rpm_check_debug
Running Transaction Test
Transaction Test Succeeded
Running Transaction
  Updating   : puppet-3.7.5-1.el6.noarch                                  1/2 
  Cleanup    : puppet-3.7.4-1.el6.noarch                                  2/2 
  Verifying  : puppet-3.7.5-1.el6.noarch                                  1/2 
  Verifying  : puppet-3.7.4-1.el6.noarch                                  2/2 

Updated:
  puppet.noarch 0:3.7.5-1.el6                                                 

Complete!
[root@testinstallcentos ~]#
```

Job is done :-)

Want to contribute ?
--------------------
Please, see the [CONTRIBUTING](https://github.com/SigmaInformatique/yum-plugin-patternvlock/blob/master/CONTRIBUTING.md) file.

Found a bug?
------------
Please, use the [GitHub issues](https://github.com/SigmaInformatique/yum-plugin-patternvlock/issues).
