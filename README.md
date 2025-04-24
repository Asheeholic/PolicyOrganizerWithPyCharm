# NetBackup Policy Organizer
## Policy analyzer web server

- python 3.10
- Bootstrap 5.0
- for NetBackup 8.0 ~ 10.5.0.1 (not all tested yet)

### Ver 1.2

- Added option of Network Backup (Standard : Follow NFS Mounts, Windows : Backup network drvs)
- changed All fonts to consolas.
- fixed DailyWindows style
- fixed undefined network backup option (such as oracle, vmware)
- fixed empty clients (such astest policy, etc)
- and deleted testArea
- added gitignore