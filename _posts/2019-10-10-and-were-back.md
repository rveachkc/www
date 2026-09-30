---
title: '....and we''re back'
date: 2019-10-10 18:56:20 -0500
categories:
- meta
tags:
- security
header:
  overlay_image: /assets/images/2019/10/clint-patterson-dYEuFB8KQJk-unsplash.jpg
  overlay_filter: 0.5
  teaser: /assets/images/2019/10/clint-patterson-dYEuFB8KQJk-unsplash.jpg
---

For anybody following along, this site has been down for a few months.

If you've been following along *really* closely, you might have noticed a few extra spammy blog posts showed up.

## I got hacked ¯\\\_(ツ)\_/¯

This blog has never been super critical, and admittedly, I was lax on security precautions, so I can't say I'm super surprised. I wanted to understand the problem and come back with a better solution, so I powered off the VM, conducted an investigation, built out some Ansible roles for a new one, and I'm back up and running finally, whew!

## What I know:

There was no unauthorized shell access to my web server. All access was obtained through exploiting the web application (WordPress).

Attackers likely gained access through uploading malicious PHP code, but I'm not going to rule out brute force attacks either.

## Preventing Future attacks:

I'm not going to spell out everything that is being done to prevent attacks in the future, because my methods may evolve, and there are already a lot of good articles out there on how to harden WordPress.

In short, here are some new things I'm doing:

- Enable Two Factor Authentication - [Plugin](https://www.wordfence.com/)
- Enable brute force attack protection - [Plugin](https://www.wordfence.com/)
- A few other tricks up my sleeve.....

## What about the old content?

I have the articles saved. I might re-upload a few more important posts at a later point in time, but I'm not in any hurry.

Cover Photo by [Clint Patterson](https://unsplash.com/@cbpsc1?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/s/photos/hacker?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)
