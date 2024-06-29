# SPDX-License-Identifier: GPL-2.0-only
# out-of-tree module, Kbuild contents first:
ifneq ($(KERNELRELEASE),)
obj-m += gna.o
gna-y := gna_device.o gna_hw.o gna_ioctl.o gna_mem.o gna_pci.o gna_request.o gna_score.o
ccflags-y += -I$(src)/include/
else
# normal out-of-tree Makefile follows
KDIR ?= /lib/modules/`uname -r`/build

default:
	$(MAKE) -C $(KDIR) M=$$PWD

# replicate all four targets here for convinience
modules:
	$(MAKE) -C $(KDIR) M=$$PWD modules
modules_install:
	# TODO: Install the uapi header here?
	$(MAKE) -C $(KDIR) M=$$PWD modules_install
clean:
	$(MAKE) -C $(KDIR) M=$$PWD clean
help:
	$(MAKE) -C $(KDIR) M=$$PWD help

endif
