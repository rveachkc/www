---
title: Alert for Open Garage Door
date: 2020-01-13 17:44:00 -0600
categories:
- Home Automation
tags:
- Home Assistant
- Home Automation
- Home Security
- MyQ
- Pushover
header:
  overlay_image: /assets/images/2020/01/vivint-solar-HASgVRE48KY-unsplash-cropped.jpg
  overlay_filter: 0.5
  teaser: /assets/images/2020/01/vivint-solar-HASgVRE48KY-unsplash-cropped.jpg
---

In my area, there have been many recent reports of thieves driving through neighborhoods. They have been peeking in garages and trying car door handles, looking for easy items to steal. In most situations, it looks like closed garage doors and locked cars are left alone.

I've personally set up an alert, so my phone is notified after my garage door has been left open for a certain amount of time. This helps me sleep better, and a recent event at a friends house has spurred me to share the knowledge. While there are *many* ways to do this, I will detail two methods.

Note that many systems, including the two listed below are capable of much more. They can even be made to shut the door automatically. Personally, if my house is going to think for itself, I prefer it lets me know what it thinks vs acting on it's own. Be mindful, [Alarm Fatigue](https://en.wikipedia.org/wiki/Alarm_fatigue) is a real thing! Try to minimize the number of false alarms based on your own lifestyle and habits.

## MyQ Garage Door Alerts

Many recent Liftmaster and Chamberlain garage door openers come with [MyQ technology](https://www.myq.com/) enabled. These openers connect via WiFi, and can be controlled via a mobile app. Without needing too much technical expertise, these can be enabled and actively monitored all with the MyQ app.

I'm using MyQ, because the openers that came with my house had this available. They're an excellent option for most people, but they do rely on a cloud system, which may bother some people. The following guide assumes that the app is already installed and the opener is connected.

<figure class="media-text align-right">
  <img src="/assets/images/2020/01/myq_ss1_show_menu.png" alt="location of the myq menu button">
</figure>

1. Open up the app and select the menu button

<figure class="media-text align-right">
  <img src="/assets/images/2020/01/myq_ss2_show_alerts.png" alt="myq menu, select alerts">
</figure>

2\. In the MyQ app menu, select Alerts.

<figure class="media-text align-right">
  <img src="/assets/images/2020/01/myq_ss3_show_alert_options.png" alt="myq alert rule definition">
</figure>

3\. You should then be able to create a new alert. To do this

- Give the alert a name
- Sent me an alert when the: Garage door is open
- For longer than: Set the desired time frame here
- By default, this will be enabled all times and days.
- By default, alerts are sent via push notification to the app, but can also be sent via email.
- By default, the alert is enabled. This option allows you to disable the alert.

<figure class="media-text align-right">
  <img src="/assets/images/2020/01/myq_ss4_bingo.png" alt="myq notification picture">
</figure>

4\. Test the alert!

- Just open up the door, and make sure you get an alert.
- Note: at the time of writing, it was *very* cold outside, so the alert as tested was set to only 2 minutes. The app should respect the value set in step 3.

## Home Assistant Garage Door Alerts

Home automation is a fairly recent hobby of mine, and I've chosen [Home Assistant](https://www.home-assistant.io/) as my main hub. Unlike most home hubs, it is software only and can be installed on most computers or single board computers, such as a Raspberry Pi. It is configured mainly using yaml based files, but the development team has been working a config model that allows everything to be completed via the web frontend.

To start with the install, it is best to ensure that some common entities are enabled as well as the myq cover. We can also add our notifier here. There are many examples, but my example shows [Pushover](https://pushover.net/).

```yaml
---
# the following 4 items are enabled for config and troubleshooting
config:
frontend:
logbook:
system_health:

# enable myq as a cover.
# this example accepts the username and password as
# environment variables.
cover:
  - platform: myq
    username: !env_var MYQ_USERNAME
    password: !env_var MYQ_PASSWORD
    type: liftmaster

# configure a notifier
# this example shows pushover, by any one of many can be used.
notify:
  - name: ryan_pushover
    platform: pushover
    api_key: !env_var PO_API_KEY
    user_key: !env_var PO_USER_KEY
```

Once enabled, restart Home Assistant and navigate to Developer Tools, States, then find the cover entries. In my case,

<figure class="media-text align-right">
  <img src="/assets/images/2020/01/Screenshot_20200113_012657.png" alt="">
</figure>

Once enabled:

- Restart Home Assistant
- Navigate to Developer Tools, States
- Find the cover entries, and record the names.
- In this screenshot, I've recorded cover.hobby_2 and cover.main_door_2

Once we have the entity names, open back up the configuration.yaml and add an alert the one below anywhere that makes sense:

```yaml
alert:
  garage_door_open:
    name: garage_door_is_open
    entity_id: cover.main_door_2
    state: 'open'
    repeat:
      - 10
      - 60
    can_acknowledge: true
    skip_first: true
    message: "The main garage door has been left open."
    done_message: "The main garage door is now closed."
    notifiers:
      - ryan_pushover
```

This config will do the following:

- Monitor the entity cover.main_door_2, triggering off the 'open' state.
- It will alert at 10 minutes, then every 60 minutes after that.
- It can be acknowledged
- Skip first prevents an alert from being sent on initial open and only begins to send messages at 10 minutes.
- Messages to be sent on alert and resolution are defined.
- This will notify the pushover notifier configured above.

<figure class="media-text align-left">
  <img src="/assets/images/2020/01/Screenshot_20200113-014027_Pushover.jpg" alt="">
</figure>

Next, test the alert by leaving the garage door open.

Bingo! We have success!

---

Cover Photo by [Vivint Solar](https://unsplash.com/@vivintsolar?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/s/photos/garage?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)
