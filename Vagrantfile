Vagrant.configure("2") do |config|
    config.vm.box = "windows2012r2min"

    config.vm.provider "virtualbox" do |v|
        v.memory = 4096
    end

    config.vm.network "forwarded_port", guest: 22, host: 2244
    config.vm.synced_folder ".", "/code", create: true
    config.vm.synced_folder ".provision", "/provision", create: true

    if File.directory?("../twisted")
        config.vm.synced_folder "../twisted", "/twisted"
    end

    config.vm.provision "system", type: "shell" do |provision|
        provision.inline = "C:\\code\\.ci\\vagrant\\system\\main.ps1"
    end

    config.vm.provision "software", type: "shell" do |provision|
        provision.inline = "C:\\code\\.ci\\vagrant\\software\\main.ps1"
    end

    config.vm.provision "sshd", type: "shell" do |provision|
        provision.inline = "C:\\code\\.ci\\vagrant\\sshd\\main.ps1"
    end

    config.vm.provision "python", type: "shell" do |provision|
        provision.inline = "C:\\code\\.ci\\vagrant\\python\\main.ps1"
    end

    config.vm.provision "install", type: "shell" do |provision|
        provision.inline = "C:\\code\\.ci\\vagrant\\install.ps1"
    end

    # FIXME: Sadly, this still needs some work
#     config.vm.provision "test", type: "shell" do |provision|
#         provision.inline = "C:\\code\\.ci\\vagrant\\test.ps1"
#     end
end
