Vagrant
=======

Vagrant is used by the pywincffi project to facilitate testing
and development on non-windows platforms.  While the project
does have continuous integration hooked up to commits and pull
requests Vagrant can help with local development.  The information
below details the general steps needed to get Vagrant up and running.

Prerequisites
-------------

Before starting, you will need a pieces of software preinstalled on
your system:

    * `Vagrant <https://www.vagrantup.com/>`_ - The software
      used to launch and provision the virtual machine image.
    * `Packer <https://www.packer.io/>`_ - Used to build a
      virtual machine image, referred to as a box, which Vagrant can then
      use.

Building The Base Virtual Machine Image
---------------------------------------

In order to effectively run and test pywincffi you must have access to a Windows
host, various versions of Python and a couple of different compilers.  While
you can rely on continuous integration to provide this it's faster to test
locally usually.

The install process for the various dependencies besides the operating system
will be covered in another section.  This section will cover setting up the
base machine image itself so

#. Use git to clone the packer templates:

   .. code-block:: console

      git clone https://github.com/mwrock/packer-templates.git

   This repository contains all the code necessary to build our base
   image.  For some extra information on how this works you can see
   this article:

      http://www.hurryupandwait.io/blog/creating-windows-base-images-for-virtualbox-and-hyper-v-using-packer-boxstarter-and-vagrant

#. Run packer.  This will generate the box image which vagrant will need
   to spin up a virtual machine.

   .. code-block:: console

      cd packer-templates
      packer build -force -only virtualbox-iso ./vbox-2012r2.json

   The above will take a while to run but when it finishes you should
   end up with a file on disk with a .box extension such as
   ``windows2012r2min-virtualbox.box``

#. Add the box image to vagrant:

   .. code-block:: console

      vagrant box add windows2012r2min-virtualbox.box --name windows2012r2min

At this point, you should have everything you need to launch vagrant with
a Windows image.

.. note::

   The box that was generated is using an evaluation copy of Windows 2012 R2
   Standard which expires in 180 days.  You will either need to add a license
   for the operating system or repeat the steps outlined above.


Running Vagrant
---------------

Vagrant is responsible for running the virtual machine itself as well as
installing and downloading the necessary software for pywincffi.  The process
for launching vagrant is:

.. code-block:: console

   cd <path to clone of pywincffi>
   vagrant up --provider virtualbox

This will start up the virtual machine, download the necessary software and
get it installed on the system.

.. important::

   At certain points during the install you will be required to perform
   some manual steps.  This is because certain software, such as Visual
   Studio express editions, can't easily be installed in an unattended
   manner.

Rerunning The Provisioning Step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you might need to execute the provisioning process again.  This
could be because one of the steps failed when running ``vagrant up``, you've
added a new step to the Vagrantfile or you've modified a step in
``.ci/vagrant/``.

To reexecute the provisioning process on a running VM run:

.. code-block:: console

   vagrant provision

To restart the VM and execute the provisioning process run:

.. code-block:: console

   vagrant reload --provision


Adding SSH Authorized Keys
~~~~~~~~~~~~~~~~~~~~~~~~~~

SSH for the Windows VM is setup to use key based authentication.  To
provide you own set of keys, create a file at
``.ci/vagrant/files/authorized_keys`` with your own public key(s).


Testing PyWinCFFI
-----------------

.. TODO::

    * vagrant deploy?
    * PyCharm remote interpreter?

