from zerver.lib.avatar import get_avatar_url
from zerver.lib.response import json_success


def get_interviews_responders(user_profile):
    group_list = user_profile.hire.all()
    members = []
    for group in group_list:
        profile = group.respondent

        avatar_url = get_avatar_url(
            profile.avatar_source,
            profile.email
        )
        member = {"full_name": profile.full_name,
                  "is_bot": profile.is_bot,
                  "is_active": profile.is_active,
                  "is_admin": (profile in admins),
                  "email": profile.email,
                  "avatar_url": avatar_url,
                  "huddle": group.huddle.hash}

        if profile.is_bot and profile.bot_owner is not None:
            member["bot_owner"] = profile.bot_owner.email

        members.append(member)
    return members


def get_interviews_responders_backend(request, user_profile):
    return json_success(
        {'respondents': get_interviews_responders(user_profile)}
    )

def create_interview_group(request, user_profile):
    pass

