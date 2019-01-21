/bin/sh

sudo service klipper stop
make flash FLASH_DEVICE=/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A90860EZ-if00-port0
sudo service klipper start

