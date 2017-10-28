# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.require_version ">= 1.9.7"

Vagrant.configure(2) do |config|
    config.vm.box = "debian/stretch64"
    config.vm.synced_folder ".", "/vagrant", disabled: true

    config.vm.define :findex do |aio|
        aio.vm.host_name = "elasticsearch.findex"
        aio.vm.network "private_network", ip:"192.168.1.13"
        aio.vm.network "forwarded_port", guest: 22, host: 2203, host_ip: "127.0.0.1", id: 'ssh'
        aio.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "2048"]
            vb.customize ["modifyvm", :id, "--cpus", "1"]
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
            vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
        end
        aio.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/all_in_one.yml"
            ansible.inventory_path = "ansible/development.inventory"
        end
    end

    config.vm.define :gui_dev do |gui_config|
        gui_config.vm.host_name = "gui"
        gui_config.vm.network "private_network", ip:"192.168.1.10"
        gui_config.vm.network "forwarded_port", guest: 22, host: 2201, host_ip: "127.0.0.1", id: 'ssh'
        gui_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "1024"]
            vb.customize ["modifyvm", :id, "--cpus", "1"]
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
            vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
        end
        gui_config.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/gui.yml"
            ansible.inventory_path = "ansible/development.inventory"
        end
    end

    config.vm.define :postgres_dev do |postgres_config|
        postgres_config.vm.host_name = "postgres.findex"
        postgres_config.vm.network "private_network", ip:"192.168.1.11"
        postgres_config.vm.network "forwarded_port", guest: 22, host: 2205, host_ip: "127.0.0.1", id: 'ssh'
        postgres_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "2048"]
            vb.customize ["modifyvm", :id, "--cpus", "2"]
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
            vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
        end
        postgres_config.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/postgres.yml"
            ansible.inventory_path = "ansible/development.inventory"
        end
    end

    config.vm.define :elasticsearch_dev do |elasticsearch_config|
        elasticsearch_config.vm.host_name = "elasticsearch.findex"
        elasticsearch_config.vm.network "private_network", ip:"192.168.1.12"
        elasticsearch_config.vm.network "forwarded_port", guest: 22, host: 2202, host_ip: "127.0.0.1", id: 'ssh'
        elasticsearch_config.vm.provider :virtualbox do |vb|
            vb.customize ["modifyvm", :id, "--memory", "2048"]
            vb.customize ["modifyvm", :id, "--cpus", "1"]
            vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
            vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
        end
        elasticsearch_config.vm.provision "ansible" do |ansible|
            ansible.verbose = "v"
            ansible.playbook = "ansible/elasticsearch.yml"
            ansible.inventory_path = "ansible/development.inventory"
        end
    end
end
