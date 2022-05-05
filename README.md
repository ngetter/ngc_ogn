# ngc_ogn

## New RPi installation
### Preperations

#### black list the comatitive rlt-sdr drivers
```bash
cat >> /etc/modprobe.d/rtl-glidernet-blacklist.conf <<EOF
blacklist rtl2832
blacklist r820t
blacklist rtl2830
blacklist dvb_usb_rtl28xxu
EOF
```

### rtl-sdr drivers
for installation of the rtl-sdr please read
[https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)

```bash
sudo apt-get update
sudo apt-get install rtl-sdr
```

Instructions for installing the RTL-SDR drivers manually from source can be found at http://sdr.osmocom.org/trac/wiki/rtl-sdr. Repeated below is the code:
```bash
sudo apt-get -y install git g++ gcc make cmake build-essential libconfig-dev libjpeg-dev libusb-1.0-0-dev
git clone git://git.osmocom.org/rtl-sdr.git
cd rtl-sdr/
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
sudo ldconfig
```
After installing the libraries you will likely need to unload the DVB-T drivers, which Linux uses by default. To unload them temporarily type "sudo rmmod dvb_usb_rtl28xxu" into terminal. This solution is only temporary as when you replug the dongle or restart the PC, the DVB-T drivers will be reloaded. For a permanent solution, create a text file "rtlsdr.conf" in /etc/modprobe.d and add the line "blacklist dvb_usb_rtl28xxu". You can use the one line command shown below to automatically write and create this file.

echo 'blacklist dvb_usb_rtl28xxu' | sudo tee – append /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

Now you can restart your device. After it boots up again run "rtl_test" at the terminal with the RTL-SDR plugged in. It should start running.

## binaries

### install required libraries

```bash
sudo apt-get -y install libconfig9 libjpeg8 libfftw3-dev lynx ntpdate ntp
```

### Download the binary and unpack it
``` bash
wget http://download.glidernet.org/rpi-gpu/rtlsdr-ogn-bin-RPI-GPU-latest.tgz
tar xvzf rtlsdr-ogn-bin-RPI-GPU-latest.tgz
```
### Create named pipe

```bash
cd rtlsdr-ogn
mkfifo ogn-rf.fifo
```

### Set file permissions (only on Pi for GPU usage)

The following five lines are only necessary if you are running the GPU code on Raspberry PI.

```bash
sudo chown root gsm_scan
sudo chmod a+s gsm_scan
sudo chown root ogn-rf
sudo chmod a+s  ogn-rf
```

## Install as service

```bash
sudo apt-get -y install procserv telnet 
sudo wget http://download.glidernet.org/common/service/rtlsdr-ogn -O /etc/init.d/rtlsdr-ogn
sudo wget http://download.glidernet.org/common/service/rtlsdr-ogn.conf -O /etc/rtlsdr-ogn.conf
sudo chmod +x /etc/init.d/rtlsdr-ogn
sudo update-rc.d rtlsdr-ogn defaults
```

### Edit Configuration file

```bash
sudo nano /etc/rtlsdr-ogn.conf
```

```bash
#shellbox configuration file
#Starts commands inside a "box" with a telnet-like server.
#Contact the shell with: telnet <hostname> <port>
#Syntax:
#port  user     directory                 command       args
50000  pi /home/pi/rtlsdr-ogn    ./ogn-rf     NGC.conf
50001  pi /home/pi/rtlsdr-ogn    ./ogn-decode NGC.conf
## Refference
```

Raspberry Pi Installation fro Open glide network site: http://wiki.glidernet.org/wiki:raspberry-pi-installation
