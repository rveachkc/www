---
title: Automated Config Management
date: 2020-02-08 13:33:01 -0600
categories:
- Homelab
tags:
- Ansible
- CI/CD
- GitLab
header:
  overlay_image: /assets/images/2020/02/pi-web.jpg
  overlay_filter: 0.5
  teaser: /assets/images/2020/02/pi-web.jpg
---

I am certainly a technology enthusiast. My home is littered with computers and other electronic devices. Unfortunately, these often require attention, because neglected devices lead to problems. Doing this manually would quickly turn into hours of tedious inspection, configuration, and documentation, and that sound super boring. I've used [Ansible](https://docs.ansible.com/) for many years to do this at home, and it's about time I wrote up how I use it.

<figure class="media-text align-right">
  <img src="/assets/images/2020/02/ansible-term.png" alt="">
</figure>

[Ansible](https://docs.ansible.com/) is free and open source configuration management software, powered by Python, ssh, and YAML. The core is simple, but powerful. Unless you shell out some cash for Tower, it's still manual.

---

### My Solution

Enter **ansible-docker**, an image I created for automated Ansible execution using [GitLab CI](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/).

- Docker Hub [rveach/ansible](https://hub.docker.com/r/rveach/ansible)
- GitLab Source: [rveach/ansible-docker](https://gitlab.com/rveach/ansible-docker/)

While you can pull it and run it interactively, it's really meant for use in CI/CD environments. To use it, just create a separate repo, and structure it in this manner. The integration takes place in the .gitlab-ci.yml file.

```
playbooks/             # pull all ansible playbook stuff here
    site.yml           # or any other file
    group_vars/        # with group_vars and roles
    roles/             # just do whatever you've configured
                       # follow standard ansible best practices

ssh/                   # ssh info
    id_rsa             # private key
    id_rsa.pub         # keep the public key here too
    known_hosts        # known hosts file
    config             # ssh config file

hosts                  # hosts file
ansible.cfg            # ansible.cfg file
.gitlab-ci-yml         # define CI jobs here
```

### SSH Security

When performing configuration management over SSH, the remote user must be either privileged or have the ability to perform critical tasks as a privileged user. This is not to be taken lightly. In my environments, I do not allow SSH in through my firewall. Instead, I've [installed a GitLab runner](https://docs.gitlab.com/runner/install/) behind my firewalls in each location.

In addition to network security, this image allows you to include your own ssh keys, known_hosts file and ssh config file.

- The private key file name will default to id_rsa, but can be overridden with the environment variable `$SSH_KEY_NAME`.
- The private key file can be password protected, just supply the environment variable `$SSH_KEY_PASSPHRASE` to decrypt.
- The known_hosts file can be populated populated for each of your hosts using the output of `ssh-keyscan -H $REMOTE_HOST`. Alternatively, you can set `host_key_checking = False` in the ansible.cfg if you don't care to validate host keys.
- ...and of course, the ssh config file can be set up in any way necessary.

You may want to look into other standard ways of securing SSH, like this one on nixCraft: [Top 20 OpenSSH Server Best Security Practices](https://www.cyberciti.biz/tips/linux-unix-bsd-openssh-server-best-practices.html)

### Ansible Vault

When using sensitive information in an Ansible playbook, it's highly recommended to use [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) to encrypt those contents. The wrapper script has functionality to read a vault password from either the environment variable `$VAULT_PASSWORD` (recommended) or the command line argument `--vault-password`(not recommended for security reasons).

#### Home Servers

```yaml
deploy-homeservers:
  stage: deploy
  image: rveach/ansible:latest-arm
  script:
    - /usr/local/bin/run.py --playbooks site_homeservers.yml
  only:
    - master
    - homeservers
  except:
    variables:
      - $ANSIBLE_PLAYBOOK_LIST
  tags:
      - armhf
      - homelab
```

#### Digital Ocean Droplets

```yaml
deploy-droplets:
  stage: deploy
  image: rveach/ansible:latest
  script:
    - /usr/local/bin/run.py --playbooks site_droplets.yml
  only:
    - master
    - droplets
  except:
    variables:
      - $ANSIBLE_PLAYBOOK_LIST
  tags:
    - droplet
```

#### Dynamic Deploy

```yaml
deploy-dynamic:
  stage: deploy
  image: rveach/ansible:latest-arm
  script:
    - /usr/local/bin/run.py --playbooks ${ANSIBLE_PLAYBOOK_LIST}
  only:
    - master
  except:
    variables:
      - $ANSIBLE_PLAYBOOK_LIST == null
  tags:
      - armhf
      - homelab
```

These jobs provide flexibility in a few ways:

- Deploy Dynamic is executed when a playbook list is passed through an optional variable. This is mainly used when triggering CI tasks from other projects via the external API.
- The other tasks run for master, but can also be set up to run from other branches. I use this to speed up the feedback loop when actively working on a role.
- **Note:** I'm also pulling two different tags for the image. Until I spend some time to configure a multi-arch build, separate tags are needed for amd64 and arm. I just happen to use a dedicated Raspberry Pi 3B+ for my GitLab Runner at home.

---

### In Use:

Now, whenever I push to the repo, I know that Ansible will execute, and I rely on GitLab's notifications to let me know when there has been a failure.

<figure>
  <img src="/assets/images/2020/02/gitlab-jobs.png" alt="">
  <figcaption>Individual jobs in a Pipeline</figcaption>
</figure>

Should any individual job fail, the log is also available:

<figure>
  <img src="/assets/images/2020/02/ci-task-view.png" alt="">
  <figcaption>Ansible Log in CI job view</figcaption>
</figure>

### Scheduling Jobs

Of course, updates on repo push is only half the story. Any well managed environment should have configuration deployed on a schedule to automate updates and prevent configuration drift. Luckily, [GitLab CI allows you to schedule pipelines](https://gitlab.com/help/user/project/pipelines/schedules).

<figure>
  <img src="/assets/images/2020/02/pipeline-schedule.png" alt="">
  <figcaption>Scheduled Pipelines</figcaption>
</figure>

<figure>
  <img src="/assets/images/2020/02/edit-pipeline.png" alt="">
  <figcaption>Editing Pipeline Schedules</figcaption>
</figure>

---

In conclusion, it took me a bit of time to work out all the kinks on this, but once completed, it's been incredibly smooth. In writing this, I hope others can benefit from my work or find inspiration to create their own solution.

---

<a style="background-color:black;color:white;text-decoration:none;padding:4px 6px;font-family:-apple-system, BlinkMacSystemFont, &quot;San Francisco&quot;, &quot;Helvetica Neue&quot;, Helvetica, Ubuntu, Roboto, Noto, &quot;Segoe UI&quot;, Arial, sans-serif;font-size:12px;font-weight:bold;line-height:1.2;display:inline-block;border-radius:3px" href="https://unsplash.com/@hbtography?utm_medium=referral&amp;utm_campaign=photographer-credit&amp;utm_content=creditBadge" target="_blank" rel="noopener noreferrer" title="Download free do whatever you want high-resolution photos from Harrison Broadbent"><span style="display:inline-block;padding:2px 3px"><svg xmlns="http://www.w3.org/2000/svg" style="height:12px;width:auto;position:relative;vertical-align:middle;top:-2px;fill:white" viewBox="0 0 32 32"><title>unsplash-logo</title><path d="M10 9V0h12v9H10zm12 5h10v18H0V14h10v9h12v-9z"></path></svg></span><span style="display:inline-block;padding:2px 3px">Cover image by Harrison Broadbent</span></a>
