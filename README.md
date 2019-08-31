Ansible Role PostgreSQL
========

[![Build Status](https://travis-ci.org/Turgon37/ansible-postgresql-server.svg?branch=master)](https://travis-ci.org/Turgon37/ansible-postgresql-server)
[![License](https://img.shields.io/badge/license-MIT%20License-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Ansible Role](https://img.shields.io/badge/ansible%20role-Turgon37.postgresql_server-blue.svg)](https://galaxy.ansible.com/Turgon37/postgresql_server/)

## Description

:grey_exclamation: Before using this role, please know that all my Ansible roles are fully written and accustomed to my IT infrastructure. So, even if they are as generic as possible they will not necessarily fill your needs, I advice you to carrefully analyse what they do and evaluate their capability to be installed securely on your servers.

This roles can install and configure a PostgreSQL database.

## Requirements

Require Ansible >= 2.4

### Dependencies

## OS Family

This role is available for Debian

## Features

At this day the role can be used to :

  * install PostgreSQL
  * configure main service
     * configure pg_hba

## Configuration

### Role variables

All variables which can be overridden are stored in [defaults/main.yml](defaults/main.yml) file as well as in table below. To see default values please refer to this file.

| Name                                     | Types/Values      | Description                                                             |
| ---------------------------------------- | ------------------|-------------------------------------------------------------------------|
| `postgresql_server__data_directory`      | Path              | The root database directory                                             |
| `postgresql_server__listen_addresses`    | List of addresses | List of addresses on which the server will listen for connections       |
| `postgresql_server__roles`               | Dict of role/user | Dict of user/role to ensure in postgresql server                        |
| `postgresql_server__databases`           |                   |                                                                         |
| `postgresql_server__service_restartable` | Boolean           | Allow or not ansible to restart the database on changes that require it |

#### PostgreSQL role/user

## Example

### Playbook

* Install and configure a non built-in exporter type as follows :

```yaml
- hosts: all
  roles:
    - role: turgon37.postgresql_server
      vars:
        postgresql_server__listen_addresses:
          - 10.1.1.2
          - 127.0.0.1
        postgresql_server__hba_rules_host:
          - type: host
            database: app1
            user: app1
            address: 10.1.1.1/32
            method: md5
        postgresql_server__roles:
          admin:
            password: '{{ vault__admin }}'
            profile: admin

          app1:
            password: '{{ vault__app1 }}'
            profile: simple-applicative-user

          app1ro:
            password: '{{ vault__app1ro }}'
            profile: simple-applicative-user
            privileges:
              - database: app1
                type: database
                privs: CONNECT
              - database: app1
                type: schema
                objs: public
                privs: USAGE
              - database: app1
                objs: ALL_IN_SCHEMA
                privs: SELECT
        postgresql_server__databases:
          app1:
            owner: app1
```
