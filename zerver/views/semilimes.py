from django.db import transaction
from django.utils.translation import ugettext as _

from zerver.lib.actions import extract_recipients, create_stream_if_needed, bulk_add_subscriptions
from zerver.lib.avatar import get_avatar_url
from zerver.lib.request import REQ, has_request_variables, JsonableError
from zerver.lib.response import json_success
from zerver.models import UserProfile, InterviewGroup


def do_get_interview_group(user_profile, interviewers_list, respondent, job_post_hash):
    """
    Return existed or create new interview group
    @param user_profile: user_profile instance
    @param interviewers_list: ['user1@mail.com', 'user2@mail.com']
    @param respondent: 'user2@mail.com'
    @param job_post_hash: job post hash
    @return: interview group
    """
    try:
        respondent_instance = UserProfile.objects.select_related().get(email__iexact=respondent.strip())
    except UserProfile.DoesNotExist:
        raise JsonableError(_("Respondent email: %s is not registered" % respondent))

    (interview_group, created) = InterviewGroup.objects.get_or_create(
        job_post_hash=job_post_hash,
        respondent_id=respondent_instance.id
    )
    if created:
        with transaction.atomic():
            # Add interviewers to group
            interviewers_list_instances = UserProfile.objects.\
                select_related().filter(email__in=interviewers_list)
            interview_group.interviewers.add(*interviewers_list_instances)

            # Create private stream for our InterviewGroup
            stream, created = create_stream_if_needed(
                user_profile.realm,
                'intv_%d' % interview_group.id,
                invite_only=True
            )

            interview_group.stream = stream
            interview_group.save()

            # Add Interviewers and respondent as stream subscribers
            subscribers = [
                interviewer for interviewer in interview_group.interviewers.all()
                ] + [interview_group.respondent]

            bulk_add_subscriptions([stream], subscribers)

    return interview_group


def get_stream_profile_info(profile, stream):
    avatar_url = get_avatar_url(
        profile.avatar_source,
        profile.email
    )
    member = {"full_name": profile.full_name,
              "is_bot": profile.is_bot,
              "is_active": profile.is_active,
              "email": profile.email,
              "avatar_url": avatar_url,
              "stream": stream.id}

    if profile.is_bot and profile.bot_owner is not None:
        member["bot_owner"] = profile.bot_owner.email

    return member


def get_interviews_responders(user_profile):
    group_list = user_profile.hire.all()
    members = []
    for group in group_list:
        members.append(get_stream_profile_info(group.respondent, group.stream))
    return members


def get_interviews_interviewers(user_profile):
    group_list = user_profile.find_job.all()
    members = []
    for group in group_list:
        for interviewer in group.interviewers.all():
            members.append(get_stream_profile_info(interviewer, group.stream))
    return members


@has_request_variables
def get_interviews_interviewers_backend(request, user_profile):
    return json_success(
        {'interviewers': get_interviews_interviewers(user_profile)}
    )


@has_request_variables
def get_interviews_responders_backend(request, user_profile):
    return json_success(
        {'respondents': get_interviews_responders(user_profile)}
    )


@has_request_variables
def get_interviews_members_backend(request, user_profile):
    return json_success(
        {
            'respondents': get_interviews_responders(user_profile),
            'interviewers': get_interviews_interviewers(user_profile)
        }
    )


@has_request_variables
def add_interview_group_backend(request,
                                user_profile,
                                job_post_hash=REQ(
                                    'job_post_hash', lambda x: x.strip(), ''),
                                respondent=REQ('respondent'),
                                interviewers=REQ(
                                    'interviewers',
                                    converter=extract_recipients,
                                    default=[]
                                )):
    interview_group_instance = do_get_interview_group(
        user_profile=user_profile,
        interviewers_list=interviewers,
        respondent=respondent,
        job_post_hash=job_post_hash
    )
    result = dict()
    result["interview_group"] = interview_group_instance.id
    return json_success(result)


# @has_request_variables
# def add_contract_group_backend(request,
#                                user_profile,
#                                contract_hash=REQ('contract_hash', lambda x: x.strip(), ''),
#                                executor=REQ('executor'),
#                                owners=REQ('owners', converter=extract_recipients, default=[]
#                                )):
#
#     interview_group_instance = do_get_interview_group(
#         user_profile=user_profile,
#         interviewers_list=interviewers,
#         respondent=respondent,
#         job_post_hash=job_post_hash
#     )
#     result = dict()
#     result["interview_group"] = interview_group_instance.id
#     return json_success(result)
#
