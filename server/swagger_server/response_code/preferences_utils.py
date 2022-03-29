from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.preferences import FabricPreferences, EnumPreferenceTypes
from swagger_server.response_code import PEOPLE_PREFERENCES, PEOPLE_PROFILE_PREFERENCES
from swagger_server.database.models.profiles import FabricProfilesPeople
from swagger_server.models.preferences import Preferences

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
    - show_email: <bool>
    - show_eppn: <bool>
    - show_profile: <bool>
    - show_publications: <bool>
    - show_roles: <bool>
    - show_sshkeys: <bool>
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
