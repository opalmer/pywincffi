Vagrant.configure("2") do |config|
    config.vm.box = "windows2012r2min"

    config.vm.provider "virtualbox" do |v|
        v.memory = 4096
    end

    config.vm.network "forwarded_port", guest: 22, host: 2244
    config.vm.synced_folder ".", "/code", create: true
    config.vm.synced_folder ".provision", "/provision", create: true

    config.vm.provision "provision", type: "shell" do |provision|
        provision.inline = "C:\\code\\.ci\\vagrant\\provision\\main.ps1"
    end

    config.vm.provision "python", type: "shell" do |provision|
        provision.inline = "C:\\code\\.ci\\vagrant\\python\\main.ps1"
    end
end
