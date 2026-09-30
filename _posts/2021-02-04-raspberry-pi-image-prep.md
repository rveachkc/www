---
title: Raspberry Pi Image Prep
date: 2021-02-04 18:38:24 -0600
categories:
- Homelab
- Raspberry Pi
tags:
- Automation
- Linux
- Python
- Raspberry Pi
header:
  overlay_image: /assets/images/2021/02/vishnu-mohanan-rZKdS0wI8Ks-unsplash.jpg
  overlay_filter: 0.5
  teaser: /assets/images/2021/02/vishnu-mohanan-rZKdS0wI8Ks-unsplash.jpg
---

<figure>
  <img src="/assets/images/2021/02/vishnu-mohanan-rZKdS0wI8Ks-unsplash.jpg" alt="Raspberry Pi">
  <figcaption>Photo by <a href="https://unsplash.com/@vishnumaiea?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Vishnu Mohanan</a> on <a href="https://unsplash.com/s/photos/raspberry-pi?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></figcaption>
</figure>

Over the years, I've set up a *lot* of Raspberry Pi's, which usually requires I pull out a spare keyboard and monitor to do basic configuration, which gets really annoying.

Inspired by the [PiBakery](https://www.pibakery.org/) project, I decided to do something about it. Introducing [pi-image-prep](https://pypi.org/project/pi-image-prep/):

<figure>
  <img src="/assets/images/2021/02/pi-image-prep.gif" alt="Animation showing the script in use">
  <figcaption><a rel="noreferrer noopener" href="https://asciinema.org/a/389175" target="_blank">View on Asciinema for a larger video</a></figcaption>
</figure>

This is a simple python script to help prepare a raspberry pi image in a matter of minutes. Currently, it can do the following:

- Set system locale
- Set system timezone
- Set passwords for root and pi users
- Add authorized keys for root and pi users
- Enable ssh
- Set hostname
- Enable WiFi
- Install packages by name

In order to do this, it will mount both boot and root partitions within a temporary location on the host computer.

Some changes such as the hostname, SSH, WiFi, and authorized keys are implemented on the image directly. Many others can only be implemented after the first boot. These are handled by placing a temporary script within `/etc/cron.d/`.

In particular, note there is a very small window in which a Raspberry Pi could be connected to the network with the default pi user password. In practice, this would be extremely difficult to exploit, except in a situation where the password change fails for an unexpected reason.

This script is designed to run only on Linux systems, and requires root *(for now)*, and can be installed via pip:

```
sudo pip3 install pi-image-prep
```

Visit the following locations for more information:

- [pypi.org/project/pi-image-prep/](https://pypi.org/project/pi-image-prep/) for download and usage information
- [gitlab.com/rveach/pi-image-prep](https://gitlab.com/rveach/pi-image-prep/) for the source or to report bugs
