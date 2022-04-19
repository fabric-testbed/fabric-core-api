import os

from swagger_server.response_code.response_utils import CoreApiOptions

# People Options
PEOPLE_PREFERENCES = CoreApiOptions('people_preferences.json')
PEOPLE_PROFILE_OTHER_IDENTITY_TYPES = CoreApiOptions('people_profile_other_identity_types.json')
PEOPLE_PROFILE_PREFERENCES = CoreApiOptions('people_profile_preferences.json')
PEOPLE_PROFILE_PERSONALPAGE_TYPES = CoreApiOptions('people_profile_personal_page_types.json')

# Projects Options
PROJECTS_PREFERENCES = CoreApiOptions('projects_preferences.json')
PROJECTS_PROFILE_PREFERENCES = CoreApiOptions('projects_profile_preferences.json')
PROJECTS_TAGS = CoreApiOptions('projects_tags_base.json')
if os.getenv('CORE_API_DEPLOYMENT_TIER') == 'production':
    PROJECTS_TAGS = PROJECTS_TAGS + CoreApiOptions('projects_tags_production.json')
elif os.getenv('CORE_API_DEPLOYMENT_TIER') == 'beta':
    PROJECTS_TAGS = PROJECTS_TAGS + CoreApiOptions('projects_tags_beta.json')
else:
    PROJECTS_TAGS = PROJECTS_TAGS + CoreApiOptions('projects_tags_alpha.json')

# Publications Options
