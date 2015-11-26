Vagrant.configure("2") do |config|
    config.vm.box = "windows2012r2min"

    config.vm.provider "virtualbox" do |v|
        v.memory = 4096
    end

    config.vm.synced_folder ".", "/code", create: true
    config.vm.synced_folder ".provision", "/provision", create: true

    # Copy files used to perform the provisioning process
    # into the virtual machine.
    config.vm.provision "file",
        source: "./.ci/vagrant/functions.ps1",
        destination: "C:\\provision\\scripts\\functions.ps1"
    config.vm.provision "file",
        source: "./.ci/vagrant/install-python.ps1",
        destination: "C:\\provision\\scripts\\install-python.ps1"
    config.vm.provision "file",
        source: "./.ci/vagrant/install-visual-studio.ps1",
        destination: "C:\\provision\\scripts\\install-visual-studio.ps1"

    # Install dependencies
    config.vm.provision "shell",
        inline: "C:\\provision\\scripts\\install-visual-studio.ps1"
    config.vm.provision "shell",
        inline: "C:\\provision\\scripts\\install-python.ps1"
end
