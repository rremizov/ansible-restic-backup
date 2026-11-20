Restic Backup
=============

Configure restic repository and create backups on schedule.

Features
--------

- Uses [restic](https://github.com/restic/restic) to create versioned, deduplicated and encrypted backups.

Caveats
-------

- Hooks are rendered verbatim into the on-disk scripts (`~/bin/*.sh`, 0700 root). Never embed secret material in a hook — deploy it as a file and point `password_file`/`password_command` at it.
- Dropping `check_cron_hour` from a `present` entry removes the check script but leaves its cron line (no "was deployed" marker to key on) — `state: absent` removes both.

Requirements
------------

- Debian

Role Vars
---------

**[defaults/main.yml](defaults/main.yml)**
