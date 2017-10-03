import re
import time
import resources
import os
import bq_utils

ACHILLES_ANALYSIS = 'achilles_analysis'
ACHILLES_RESULTS = 'achilles_results'
ACHILLES_RESULTS_DIST = 'achilles_results_dist'
ACHILLES_TABLES = [ACHILLES_ANALYSIS, ACHILLES_RESULTS, ACHILLES_RESULTS_DIST]
ACHILLES_DML_SQL_PATH = os.path.join(resources.resource_path, 'achilles_dml.sql')
COMMAND_SEP = ';'
PREFIX_PLACEHOLDER = 'synpuf_100.'
TEMP_PREFIX = 'temp.'
END_OF_IMPORTING_LOOKUP_MARKER = 'end of importing values into analysis lookup'
TEMP_TABLE_PATTERN = re.compile('\s*INTO\s+([^\s]+)')
TRUNCATE_TABLE_PATTERN = re.compile('\s*truncate\s+table\s+([^\s]+)')
DROP_TABLE_PATTERN = re.compile('\s*drop\s+table\s+([^\s]+)')


def _is_commented_line(s):
    s = s.strip()
    return s == '' or s.startswith('--')


def is_commented_block(s):
    ls = s.split('\n')
    return all(map(_is_commented_line, ls))


def is_active_command(s):
    return not is_commented_block(s)


def get_commands(sql_path):
    """

    """
    with open(sql_path, 'r') as f:
        text = f.read()
        commands = text.split(COMMAND_SEP)
        return filter(is_active_command, commands)


def qualify_tables(command, hpo_id):
    def temp_repl(m):
        table_name = m.group(1).replace('.', '_')
        return bq_utils.get_table_id(hpo_id, table_name)

    # TODO ensure this remains consistent with bq_utils.get_table_id
    table_prefix = hpo_id + '_'
    command = command.replace(PREFIX_PLACEHOLDER, table_prefix)
    command = re.sub('(temp.[^\s])', temp_repl, command)
    return command


def _get_load_analysis_commands(hpo_id):
    raw_commands = get_commands(ACHILLES_DML_SQL_PATH)
    commands = map(lambda cmd: qualify_tables(cmd, hpo_id), raw_commands)
    for command in commands:
        if END_OF_IMPORTING_LOOKUP_MARKER in command.lower():
            break
        yield command


def _get_run_analysis_commands(hpo_id):
    raw_commands = get_commands(ACHILLES_DML_SQL_PATH)
    commands = map(lambda cmd: qualify_tables(cmd, hpo_id), raw_commands)
    i = 0
    for command in commands:
        if END_OF_IMPORTING_LOOKUP_MARKER in command.lower():
            break
        i += 1
    return commands[i:]


def load_analyses(hpo_id):
    commands = _get_load_analysis_commands(hpo_id)
    for command in commands:
        bq_utils.query(command)


def run_analyses(hpo_id):
    commands = _get_run_analysis_commands(hpo_id)
    for command in commands:
        print 'Running `%s`...\n' % command
        if is_to_temp_table(command):
            table_id = get_temp_table_name(command)
            query = get_temp_table_query(command)
            bq_utils.query(query, False, table_id)
            time.sleep(6)
        elif is_truncate(command):
            table_id = get_truncate_table_name(command)
            query = 'DELETE FROM %s WHERE TRUE' % table_id
            bq_utils.query(query)
        elif is_drop(command):
            table_id = get_drop_table_name(command)
            bq_utils.delete_table(table_id)
        else:
            bq_utils.query(command)


def is_to_temp_table(q):
    return 'INTO' in q


def get_temp_table_name(q):
    match = TEMP_TABLE_PATTERN.search(q)
    return match.group(1)


def get_temp_table_query(q):
    table_name = get_temp_table_name(q)
    i = q.index(table_name)
    return q[i + len(table_name):].strip()


def is_truncate(q):
    return 'truncate' in q.lower()


def get_truncate_table_name(q):
    match = TRUNCATE_TABLE_PATTERN.search(q)
    return match.group(1)


def is_drop(q):
    return 'drop' in q.lower()


def get_drop_table_name(q):
    match = DROP_TABLE_PATTERN.search(q)
    return match.group(1)


def create_tables(hpo_id, drop_existing=False):
    """
    Create the achilles related tables
    :param hpo_id: associated hpo id
    :param drop_existing: if True, drop existing tables
    :return:
    """
    for table_name in ACHILLES_TABLES:
        table_id = bq_utils.get_table_id(hpo_id, table_name)
        bq_utils.create_standard_table(table_name, table_id, drop_existing)
