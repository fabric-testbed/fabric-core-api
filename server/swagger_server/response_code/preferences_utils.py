from typing import Union

from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.preferences import FabricPreferences, EnumPreferenceTypes
from swagger_server.database.models.profiles import FabricProfilesPeople, FabricProfilesProjects
from swagger_server.database.models.projects import FabricProjects
from swagger_server.models.preferences import Preferences
from swagger_server.response_code import PEOPLE_PREFERENCES, PEOPLE_PROFILE_PREFERENCES, PROJECTS_PREFERENCES, \
    PROJECTS_PROFILE_PREFERENCES

"""
FabricPreferences model (* denotes required)
- created - timestamp created (TimestampMixin)
- id - primary key (BaseMixin)
- * key - string
- modified - timestamp modified (TimestampMixin)
- people_id - foreignkey link to people table (nullable)
- profiles_people_id - foreignkey link to profiles_people table (nullable)
- profiles_projects_id - foreignkey link to profiles_projects table (nullable)
- projects_id - foreignkey link to projects table (nullable)
- * type - string:['people', 'projects', 'profiles_people', 'profiles_projects']
- * value - boolean
"""


def create_people_preferences(fab_person: FabricPeople = None) -> None:
    pref_type = EnumPreferenceTypes.people
    for option in PEOPLE_PREFERENCES.options:
        pref = FabricPreferences()
        pref.key = option
        pref.value = True
        pref.type = pref_type
        pref.people_id = fab_person.id
        db.session.add(pref)
        db.session.commit()
        fab_person.preferences.append(pref)
    db.session.commit()


def get_people_preferences(fab_person: FabricPeople = None) -> Preferences:
    """
    People Preferences - default = True
    - show_email - show/hide email in all interfaces
    - show_eppn - show/hide eppn in all interfaces
    - show_profile - show/hide profile in all interfaces
    - show_publications - show/hide publications in all interfaces
    - show_roles - show/hide roles in all interfaces
    - show_sshkeys - show/hide sshkeys in all interfaces
    """
    preferences = Preferences()
    for p in fab_person.preferences:
        preferences.__setattr__(p.key, p.value)

    return preferences


def create_profile_people_preferences(fab_profile: FabricProfilesPeople = None) -> None:
    pref_type = EnumPreferenceTypes.profiles_people
    for option in PEOPLE_PROFILE_PREFERENCES.options:
        pref = FabricPreferences()
        pref.key = option
        pref.value = True
        pref.type = pref_type
        pref.profiles_people_id = fab_profile.id
        db.session.add(pref)
        db.session.commit()
        fab_profile.preferences.append(pref)
    db.session.commit()


def create_projects_preferences(fab_project: FabricProjects = None) -> None:
    pref_type = EnumPreferenceTypes.projects
    for option in PROJECTS_PREFERENCES.options:
        pref = FabricPreferences()
        pref.key = option
        pref.value = True
        pref.type = pref_type
        pref.people_id = fab_project.id
        db.session.add(pref)
        db.session.commit()
        fab_project.preferences.append(pref)
    db.session.commit()


def create_profile_projects_preferences(fab_profile: FabricProfilesProjects = None) -> None:
    pref_type = EnumPreferenceTypes.profiles_projects
    for option in PROJECTS_PROFILE_PREFERENCES.options:
        pref = FabricPreferences()
        pref.key = option
        pref.value = True
        pref.type = pref_type
        pref.profiles_projects_id = fab_profile.id
        db.session.add(pref)
        db.session.commit()
        fab_profile.preferences.append(pref)
    db.session.commit()


def get_fabric_preferences(fab_object: Union[FabricPeople, FabricProjects] = None) -> Preferences:
    preferences = Preferences()
    for p in fab_object.preferences:
        preferences.__setattr__(p.key, p.value)

    return preferences


def get_projects_preferences(fab_project: FabricProjects = None) -> Preferences:
    """
    Projects Preferences - default = True
    - show_profile - show/hide profile in all interfaces
    - show_project_members - show/hide project_members in all interfaces
    - show_project_owners - show/hide project_owners in all interfaces
    - show_publications - show/hide publications in all interfaces
    """
    preferences = Preferences()
    for p in fab_project.preferences:
        preferences.__setattr__(p.key, p.value)

    return preferences
