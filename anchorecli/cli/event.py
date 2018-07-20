import sys
import json
import click
import logging

import anchorecli.clients.apiexternal
import anchorecli.cli.utils

config = {}
_logger = logging.getLogger(__name__)

@click.group(name='event', short_help='Event operations')
@click.pass_obj
def event(ctx_config):
    global config
    config = ctx_config

    try:
        anchorecli.cli.utils.check_access(config)
    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'event', {}, err)
        sys.exit(2)


@event.command(name='list', short_help='List events')
@click.option('--since', default=None, required=False, help='ISO8601 formatted UTC timestamp to filter events that occurred after the timestamp')
@click.option('--before', default=None, required=False, help='ISO8601 formatted UTC timestamp to filter events that occurred before the timestamp')
@click.option('--level', default=None, required=False, help='Filter results based on the level, supported levels are info and error')
@click.option('--service', default=None, required=False, help='Filter events based on the originating service')
@click.option('--host', default=None, required=False, help='Filter events based on the originating host')
@click.option('--all', is_flag=True, default=False, required=False, help='Display all results. If not specified only the first 100 events are displayed')
@click.argument('resource', nargs=1, required=False)
def list(since=None, before=None, level=None, service=None, host=None, resource=None, all=False):
    """
    RESOURCE: Value can be a tag, image digest or repository name. Displays results related to the specific resource
    """
    ecode = 0

    try:
        if level:
            if level.upper() not in ['INFO', 'ERROR']:
                raise Exception('{} is an invalid value for --level. Supported values are \'info\' or \'error\''.format(level))
            level = level.upper()

        ret = anchorecli.clients.apiexternal.list_events(config, since=since, before=before, level=level, service=service, host=host, resource=resource, all=all)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            print anchorecli.cli.utils.format_output(config, 'event_list', {}, ret['payload'])
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'event_list', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)


@event.command(name='get', short_help='Get an event')
@click.argument('event_id', nargs=1)
def get(event_id):
    """
    EVENT_ID: ID of the event to be fetched
    """
    ecode = 0

    try:
        ret = anchorecli.clients.apiexternal.get_event(config, event_id=event_id)
        ecode = anchorecli.cli.utils.get_ecode(ret)
        if ret['success']:
            print anchorecli.cli.utils.format_output(config, 'event_get', {}, ret['payload'])
        else:
            raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'event_get', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)


@event.command(name='delete', short_help='Delete one or more events')
@click.option('--since', default=None, required=False, help='Specify an ISO8601 formatted UTC timestamp to delete events that occurred after the timestamp')
@click.option('--before', default=None, required=False, help='Specify an ISO8601 formatted UTC timestamp to delete events that occurred before the timestamp')
@click.option("--dontask", is_flag=True, help="Do not ask for confirmation when omitting event_id, since and before (i.e. delete all events)")
@click.argument('event_id', nargs=1, required=False)
def delete(since=None, before=None, dontask=False, event_id=None):
    """
    EVENT_ID: ID of the event to be deleted. --since and --before options will be ignored if this is specified

    NOTE: if no options are provided, delete (clear) all events in the engine.  To skip the prompt in this case, use the --dontask flag.
    """
    ecode = 0

    try:
        if event_id:
            ret = anchorecli.clients.apiexternal.delete_event(config, event_id=event_id)
        else:
            if not since and not before:
                if dontask:
                    answer = "y"
                else:
                    try:
                        answer = raw_input("Really delete (clear) all events? (y/N)")
                    except:
                        answer = "n"
            else:
                answer = "y"

            if 'y' == answer.lower():
                ret = anchorecli.clients.apiexternal.delete_events(config, since=since, before=before)

                ecode = anchorecli.cli.utils.get_ecode(ret)
                if ret['success']:
                    print anchorecli.cli.utils.format_output(config, 'event_delete', {}, ret['payload'])
                else:
                    raise Exception(json.dumps(ret['error'], indent=4))

    except Exception as err:
        print anchorecli.cli.utils.format_error_output(config, 'event_delete', {}, err)
        if not ecode:
            ecode = 2

    anchorecli.cli.utils.doexit(ecode)