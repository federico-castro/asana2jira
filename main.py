import json
import csv

RESOURCE_TYPE_MAP = {
    'Bug': 'bug',
    'Test Case': 'task',
    'Epic': 'epic',
    'Story': 'story',
    'Default': 'task',
}

PRIORITY_MAP = {
    'P0': 'Highest',
    'P1': 'High',
    'P2': 'Medium',
    'P3': 'Low',
    'P4': 'Lowest',
}


def asana_json_to_jira_csvs():
    users = set()
    issues = []

    with open('./data.json') as f:
        data = json.load(f)

    issues_data = data.get('data', [])

    print(f"Preparing CSV files to import {len(issues_data)} issues to JIRA.")

    headers = ['Project', 'Issue Type', 'Priority', 'Summary', 'Description', 'Assignee',
               'Status', 'Date Created', 'Date Modified']

    labels_count = 0

    for index, issue in enumerate(issues_data):
        assignee = (issue.get('assignee', {}) or {}).get('name')

        summary = issue['name']
        description = issue['notes']
        modified_at = issue['modified_at']
        created_at = issue['created_at']

        completed = issue['completed']

        asana_permalink_url = issue['permalink_url']
        description = description + '\n' if description else description
        description += f'* Asana Permalink Url: {asana_permalink_url}\n* Asana Assignee: {assignee or "No Assignee"}'

        _memberships = (issue.get('memberships', []) or [])
        _section = _memberships[0]['section'] if _memberships else None
        _name = _section['name'] if _section else None
        is_in_progress = _name if _name else None

        if is_in_progress == 'In progress':
            status = 'In Progress'
        elif completed:
            status = 'Done'
        else:
            status = 'To Do'

        custom_fields = {}
        for asana_custom_field in issue['custom_fields']:
            field_name = asana_custom_field['name']
            display_value = asana_custom_field['display_value']
            custom_fields[field_name] = display_value

        issue_type = custom_fields.get('IT', 'Default') or 'Default'  # Could be None, double check.
        issue_type = RESOURCE_TYPE_MAP.get(issue_type) if issue_type is not None else 'task'

        priority = custom_fields.get('Priority', '')
        priority = PRIORITY_MAP.get(priority, 'Medium')

        team = custom_fields.get('Dev Type', '')

        aux_tag = []
        tags = [tag['name'] for tag in issue['tags']]
        for tag in tags:
            if ',' in tag:
                aux_tag += [e.strip() for e in tag.split(',')]
            else:
                aux_tag += [tag]
        tags = aux_tag[:]
        tags.append(team)
        tags.append(status)

        labels_count = max(labels_count, len(tags))

        if assignee:
            users.add(assignee)

        # ['Project', 'Issue Type', 'Priority', 'Summary', 'Description', 'Assignee', 'Status', 'Date Created', 'Date Modified']
        issue_row = ['ACENG', issue_type, priority, summary, description, assignee, status, created_at, modified_at, tags]
        issues.append(issue_row)

    headers += (['labels'] * labels_count)

    with open('./issues.csv', 'w+') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(headers)

        for issue in issues:
            row = issue[:-1]
            labels = issue[-1][:]
            labels = [e.strip() if e else '' for e in labels]
            labels += ['']*(labels_count - len(labels))
            row += labels
            csv_writer.writerow(row)


asana_json_to_jira_csvs()
