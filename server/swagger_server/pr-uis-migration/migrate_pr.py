"""
migrate PR projects and tags data to core-api

Projects (match by uuid)
- description: update core-api to match PR value
- created: update core-api to match PR value
- modified: update core-api to match PR value

Tags (match by project_id, tag)
- ADD tag if tag from PR does not exist in core-api

"""
import json
from datetime import datetime

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.projects import FabricProjects, ProjectsTags

app.app_context().push()

# load pr_projects.json, pr_tags.json, pr_people.json
pr_projects_file = 'data/pr_projects.json'
pr_tags_file = 'data/pr_tags.json'
pr_people_file = 'data/pr_people.json'

with open(pr_projects_file, "r") as f:
    f_dict = json.load(f)
    pr_projects = f_dict.get('pr_projects', None)

with open(pr_tags_file, "r") as f:
    f_dict = json.load(f)
    pr_tags = f_dict.get('pr_tags', None)

with open(pr_people_file, "r") as f:
    f_dict = json.load(f)
    pr_people = f_dict.get('pr_people', None)


def date_parser(text) -> datetime:
    # format: 2022-05-11 17:19:00+00:00 or 2021-09-10 21:03:22.730968+00:00
    for fmt in ["%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S.%f%z"]:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError('No valid date format found')


# update fab_project from PR
def update_project_from_pr(fab_project: FabricProjects, pr_project: dict):
    """
    - active - project status
    - created - timestamp created (TimestampMixin)
    - created_by_uuid - uuid of person created_by (TrackingMixin)
    - description - project description
    - facility - project facility (default = FABRIC)
    - id - primary key (BaseMixin)
    - is_public - show/hide project in all public interfaces (default: True)
    - modified - timestamp modified (TimestampMixin)
    - modified_by_uuid - uuid of person modified_by (TrackingMixin)
    - name - project name
    - preferences - array of preference booleans
    - profile - foreignkey link to profile_projects
    - project_creators - one-to-many people (initially one person)
    - project_members - one-to-many people
    - project_owners - one-to-many people
    - tags - array of tag strings
    - uuid - unique universal identifier
    """
    # update description
    consoleLogger.info('- description: {0} --> {1}'.format(str(fab_project.description), pr_project.get('description')))
    fab_project.description = pr_project.get('description')
    db.session.commit()
    # update created
    consoleLogger.info('- created: {0} --> {1}'.format(str(fab_project.created), pr_project.get('created_time')))
    fab_project.created = date_parser(pr_project.get('created_time'))
    db.session.commit()
    # update modified
    consoleLogger.info('- modified: {0} --> {1}'.format(str(fab_project.modified), pr_project.get('modified')))
    if pr_project.get('modified').casefold() != "none":
        fab_project.modified = date_parser(pr_project.get('modified'))
    else:
        fab_project.modified = date_parser(pr_project.get('created_time'))
    db.session.commit()
    # update tags
    add_tags_to_project(fab_project=fab_project, pr_project=pr_project)


# add tags to projects in fabric-core-api
def add_tags_to_project(fab_project: FabricProjects, pr_project: dict):
    """
    - id - primary key (BaseMixin)
    - projects_id - foreignkey link to projects table
    - tag - tag as string
    """
    tags = [cdict for cdict in pr_tags if cdict['projects_id'] == pr_project.get('id')]
    if tags:
        for tag in tags:
            # check for duplicate tag
            if ProjectsTags.query.filter(
                    ProjectsTags.tag == tag.get('tag'), ProjectsTags.projects_id == fab_project.id
            ).first():
                consoleLogger.info('- tags: DUPLICATE {0}'.format(tag.get('tag')))
            # create new project tag
            else:
                p_tag = ProjectsTags()
                p_tag.projects_id = fab_project.id
                p_tag.tag = tag.get('tag')
                db.session.add(p_tag)
                db.session.commit()
                consoleLogger.info('- tags: ADD {0}'.format(tag.get('tag')))


# migrate UIS data to core-api
for pr_p in pr_projects:
    project = FabricProjects.query.filter_by(uuid=pr_p.get('uuid')).first()
    if project:
        consoleLogger.info('FOUND: {0}'.format(pr_p.get('uuid')))
        update_project_from_pr(fab_project=project, pr_project=pr_p)
    else:
        consoleLogger.warning('NOT FOUND: {0}'.format(pr_p.get('uuid')))
