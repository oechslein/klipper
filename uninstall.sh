/bin/sh

# Stop Klipper Service
echo "###Stopping Klipper Service.."
echo
sudo service klipper stop

# Remove Klipper from Startup
echo "####Removing Klipper from Startup.."
echo
sudo update-rc.d  -f klipper remove

# Remove Klipper from Services
echo "####Removing Klipper Service"
echo
sudo rm -f /etc/init.d/klipper /etc/default/klipper


