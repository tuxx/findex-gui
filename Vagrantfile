# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.require_version ">= 1.9.7"

Vagrant.configure(2) do |config|
    config.vm.box = "debian/stretch64"
    config.vm.synced_folder ".", "/vagrant", disabled: true

    config.vm.define :gui do |gui_config|
        gui_config.vm.host_name = "gui"
        gui_config.vm.network "private_network", ip:"192.168.1.10"
        gui_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "1024"]
            vb.customize ["modifyvm", :id, "--cpus", "1"]
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
        end
        gui_config.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/gui.yml"
        end
    end

    config.vm.define :postgres do |postgres_config|
        postgres_config.vm.host_name = "postgres.findex"
        postgres_config.vm.network "private_network", ip:"192.168.1.11"
        postgres_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "2048"]
            vb.customize ["modifyvm", :id, "--cpus", "2"]
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
        end
        postgres_config.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/postgres.yml"
        end
    end

    config.vm.define :elasticsearch do |elasticsearch_config|
        elasticsearch_config.vm.host_name = "elasticsearch.findex"
        elasticsearch_config.vm.network "private_network", ip:"192.168.1.12"
        elasticsearch_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "2048"]
            vb.customize ["modifyvm", :id, "--cpus", "1"]
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
        end
        elasticsearch_config.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/elasticsearch.yml"
        end
    end
end
