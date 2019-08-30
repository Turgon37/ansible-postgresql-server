# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
lookup: postgresql_query
short_description: execute a postgresql query and return its result as a lookup data
description:
  - This lookup execute a query on a postgresql database and returns the result.
options:
  query:
    description: The postgresSQL query string
  database:
    description: The database name to connect to
    default: postgres
  login_user:
    description: The login used to connect to database
    default: postgres
  login_password:
    description: The password used to connect to database
    default: ''
  login_host:
    description: the host to connect to (default localhost)
  login_unix_socket:
    description: the host socket to connect to (default localhost)
  port:
    description: The port used to connect to server
    default: 5432
  parameters:
    description: Dict of key value parameters for query (see psycopg2 doc)
  unzip_columns:
    description: List of column names to unzip before to return as a result
  unstringify_json_columns:
    description: List of stringified JSON column to unstringify before return as a result
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

import datetime
import json
import zlib

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    POSTGRESQLDB_FOUND = False
else:
    POSTGRESQLDB_FOUND = True


def prepare_connection_params(**params):
    params_map = {
        "login_host":"host",
        "login_user":"user",
        "login_password":"password",
        "port":"port"
    }
    kw = dict((params_map[k], v) for (k, v) in params.items() if k in params_map and v != '')

    # If a login_unix_socket is specified, incorporate it here.
    is_localhost = "host" not in kw or kw["host"] == "" or kw["host"] == "localhost"
    if is_localhost and params["login_unix_socket"] != "":
        kw["host"] = params["login_unix_socket"]

    return kw


class LookupModule(LookupBase):

    def run(self, terms,
            query, database='postgres',
            login_user='postgres', login_password='', login_host='',
            login_unix_socket='', port=5432,
            parameters=dict(),
            unzip_columns=[],
            unstringify_json_columns=[],
            variables=None, 
            **kwargs):
        if not POSTGRESQLDB_FOUND:
            raise AnsibleError('This lookup plugin require psycopg2 python module')

        cursor = None
        db_params = prepare_connection_params(login_user=login_user,
                                              login_password=login_password,
                                              login_host=login_host,
                                              login_unix_socket=login_unix_socket,
                                              port=port)
        results = []
        for key in parameters:
            if isinstance(parameters[key], list):
                parameters[key] = tuple(parameters[key])

        try:
            db_connection = psycopg2.connect(database=database, **db_params)
            # Enable autocommit so we can create databases
            if psycopg2.__version__ >= '2.4.2':
                db_connection.autocommit = True
            else:
                db_connection.set_isolation_level(psycopg2
                                                  .extensions
                                                  .ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, parameters)

            for item in cursor.fetchall():
                #
                for key in item:
                    if isinstance(item[key], datetime.datetime):
                        item[key] = str(item[key])

                # decompress binary datas
                for key in unzip_columns:
                    if key not in item:
                        continue
                    item[key] = zlib.decompress(item[key])

                for key in unstringify_json_columns:
                    if key not in item:
                        continue
                    item[key] = json.loads(item[key])

                results.append(json.dumps(item))
        except psycopg2.ProgrammingError as ex:
            raise AnsibleError('database error: the query did not produce any resultset, {}'.format(str(ex)))
        except psycopg2.DatabaseError as ex:
            raise AnsibleError('database error: {}'.format(str(ex)))
        except TypeError as ex:
            raise AnsibleError('parameters error: {}'.format(str(ex)))
        finally:
            if cursor:
                cursor.connection.rollback()
        return results

