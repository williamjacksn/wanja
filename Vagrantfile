# -*- mode: ruby -*-
# vi: set ft=ruby :

provision_script = <<END_OF_LINE
#!/usr/bin/env bash

aptitude update

aptitude --assume-yes install python-dev python-pip
pip install --upgrade pip
hash pip
pip install -r /vagrant/requirements.txt

END_OF_LINE

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "ubuntu/trusty64"
    # config.vm.box_check_update = false
    config.vm.network "forwarded_port", guest: 5000, host: 5000
    config.vm.provision :shell, :inline => provision_script
end
