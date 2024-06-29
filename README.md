Intel GNA DRM driver for Linux
==============================

(as an out-of-tree kernel module)
---------------------------------

This is the Linux kernel driver for the Intel GNA hardware. A corresponding [userspace library](https://github.com/intel/gna) provides an API for using the hardware, which I have also packaged in [xanderlent/intel-gna-rpm](https://github.com/xanderlent/intel-gna-rpm).

This code is derived from Intel engineer Maciej Kwapulinski's v5 patch series to the dri-devel mailing list, available [at kernel.org's lore public-inbox instance](https://lore.kernel.org/dri-devel/20221020175334.1820519-1-maciej.kwapulinski@linux.intel.com/), and [which applies cleanly to linux v6.0](https://github.com/xanderlent/linux/tree/intel-gna-patches-v5-on-linux-v6.0).

I [forward-ported the patch series to Linux v6.9](https://github.com/xanderlent/linux/tree/intel-gna-patches-v5-forward-ported-linux-v6.9), fixing the code with respect to a change in the internal DRM GEM API and making sure every patch in the series builds cleanly. I then ported the code to build as an out-of-tree module.
