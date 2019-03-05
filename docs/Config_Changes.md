This document covers recent software changes to the config file that
are not backwards compatible. It is a good idea to review this
document when upgrading the Klipper software.

All dates in this document are approximate.

# Changes

20190228: Users of SPI or I2C on SAMD21 boards must now specify the
bus pins via a [samd_sercom] config section.

20190224: The bed_shape option has been removed from bed_mesh.  The
radius option has been renamed to bed_radius.  Users with round beds
should supply the bed_radius and round_probe_count options.

20190107: The i2c_address parameter in the mcp4451 config section
changed. This is a common setting on Smoothieboards. The new value is
half the old value (88 should be changed to 44, and 90 should be
changed to 45).

20181220: Klipper v0.7.0 released
