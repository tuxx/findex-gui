# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.require_version ">= 1.9.7"

Vagrant.configure(2) do |config|
    config.vm.box = "debian/jessie64"
    config.vm.synced_folder ".", "/vagrant", disabled: true

    config.vm.define :gui do |gui_config|
        gui_config.vm.host_name = "gui"
        gui_config.vm.network "private_network", ip:"192.168.1.10"
        gui_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "2048"]
            vb.customize ["modifyvm", :id, "--cpus", "1"]
        end
        gui_config.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/gui.yml"
        end
    end

    config.vm.define :db do |db_config|
        db_config.vm.host_name = "db"
        db_config.vm.network "private_network", ip:"192.168.1.11"
        db_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "2048"]
            vb.customize ["modifyvm", :id, "--cpus", "2"]
        end
    end

    config.vm.define :amqp do |amqp_config|
        amqp_config.vm.host_name = "db"
        amqp_config.vm.network "private_network", ip:"192.168.1.12"
        amqp_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "512"]
            vb.customize ["modifyvm", :id, "--cpus", "1"]
        end
    end
end
