from django.db import transaction
from django.utils.translation import ugettext as _

from zerver.lib.actions import extract_recipients, create_stream_if_needed, bulk_add_subscriptions
from zerver.lib.avatar import get_avatar_url
from zerver.lib.request import REQ, has_request_variables, JsonableError
from zerver.lib.response import json_success
from zerver.models import UserProfile, InterviewGroup, ContractGroup


def do_get_interview_group(user_profile, interviewers_list, respondent, job_post_hash):
    """
    Returns existed or create new interview group
    @param user_profile: user_profile instance
    @param interviewers_list: ['user1@mail.com', 'user2@mail.com']
    @param respondent: 'user3@mail.com'
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
    """
    Returns user profile dict attributes for JSON response
    @param profile: user_profil
    @param stream: stream
    @return: member dict
    """
    avatar_url = get_avatar_url(
        profile.avatar_source,
        profile.email
    )
    member = {"full_name": profile.full_name,
              "is_bot": profile.is_bot,
              "is_active": profile.is_active,
              "email": profile.email,
              "avatar_url": avatar_url,
              "stream": stream.name}

    if profile.is_bot and profile.bot_owner is not None:
        member["bot_owner"] = profile.bot_owner.email

    return member


def get_interviews_responders(user_profile):
    """
    Returns list of all user_profile interview respondents
    @param user_profile: user_profile
    @return: list
    """
    group_list = user_profile.hire.all()
    members = []
    for group in group_list:
        member_dict = get_stream_profile_info(group.respondent, group.stream)
        member_dict['job_post'] = group.job_post_hash
        members.append(member_dict)
    return members


def get_interviews_interviewers(user_profile):
    """
    Returns list of all user_profiles interview interviewers
    @param user_profile: user_profile
    @return: list
    """
    group_list = user_profile.find_job.all()
    members = []
    for group in group_list:
        for interviewer in group.interviewers.all():
            member_dict = get_stream_profile_info(interviewer, group.stream)
            member_dict['job_post'] = group.job_post_hash
            members.append(member_dict)
    return members


@has_request_variables
def get_interviews_interviewers_backend(request, user_profile):
    """
    API endpoint to return all user profile interviewers
    """
    return json_success(
        {'interviewers': get_interviews_interviewers(user_profile)}
    )


@has_request_variables
def get_interviews_responders_backend(request, user_profile):
    """
    API endpoint to return all user profile interview responders
    """
    return json_success(
        {'respondents': get_interviews_responders(user_profile)}
    )


@has_request_variables
def get_interviews_members_backend(request, user_profile):
    """
    API endpoint to return combined list of all user profile interview responders and interviewers
    """
    return json_success(
        {
          'members': {
                'respondents': get_interviews_responders(user_profile),
                'interviewers': get_interviews_interviewers(user_profile)
          }
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
    """
    API endpoint to gets or creates interview group
    @param request: request
    @param user_profile: user_profile
    @param job_post_hash: string that represents job_post in marketplace
    @param respondent: respondent email
    @param interviewers: comma separated list of interviewers emails
    @return: JSON response with interview_group id and stream name related to interview
    """
    interview_group_instance = do_get_interview_group(
        user_profile=user_profile,
        interviewers_list=interviewers,
        respondent=respondent,
        job_post_hash=job_post_hash
    )
    result = dict()
    result["interview_group"] = interview_group_instance.stream.name
    result["stream"] = interview_group_instance.stream.id
    return json_success(result)


def do_get_contract_group(user_profile, owners, executor, contract_hash):
    """
    Returns existed or create new contract group
    @param user_profile: user_profile
    @param owners: ['user1@mail.com', 'user2@mail.com']
    @param executor: 'user3@mail.com'
    @param contract_hash: hash string that represents contract
    @return: contract_instance
    """
    try:
        executor_instance = UserProfile.objects.select_related().get(email__iexact=executor.strip())
    except UserProfile.DoesNotExist:
        raise JsonableError(_("Executor email: %s is not registered" % executor))

    (contract_group, created) = ContractGroup.objects.get_or_create(contract_hash=contract_hash)
    if created:
        with transaction.atomic():
            # Add contract owners to group
            owners_list_instances = UserProfile.objects.select_related().filter(email__in=owners)
            contract_group.owners.add(*owners_list_instances)

            # Create private stream for our InterviewGroup
            stream, created = create_stream_if_needed(
                user_profile.realm,
                'cnt_%d' % contract_group.id,
                invite_only=True
            )

            contract_group.executor = executor_instance
            contract_group.stream = stream
            contract_group.save()

            # Add Owners and Executor as stream subscribers
            subscribers = [owner for owner in owners_list_instances] + [executor_instance]

            bulk_add_subscriptions([stream], subscribers)

    return contract_group


def get_contracts_executors(user_profile):
    """
    Returns list of all user_profile contracts executors
    @param user_profile:
    @return: list
    """
    group_list = user_profile.contract_executors.all()
    members = []
    for group in group_list:
        members.append(get_stream_profile_info(group.executor, group.stream))
    return members


def get_contracts_owners(user_profile):
    """
    Returns list of all user_profile contract owners where user_profile is executor
    @param user_profile: user_profile
    @return: list
    """
    group_list = user_profile.contract_owners.all()
    members = []
    for group in group_list:
        for owner in group.owners.all():
            members.append(get_stream_profile_info(owner, group.stream))
    return members


@has_request_variables
def get_contracts_members_backend(request, user_profile):
    """
    API endpoint to return combined list of all user profile contracts owners and executors
    """
    return json_success(
        {
            'members': {
                'owners': get_contracts_owners(user_profile),
                'executors': get_contracts_executors(user_profile)
            }
        }
    )


@has_request_variables
def add_contract_group_backend(request,
                               user_profile,
                               contract_hash=REQ('contract_hash', lambda x: x.strip(), ''),
                               executor=REQ('executor'),
                               owners=REQ('owners', converter=extract_recipients, default=[]
                               )):

    """
    API endpoint to gets or creates contract group
    @param request: request
    @param user_profile: user_profile
    @param contract_hash: string that represent contract in marketplace
    @param executor: executor email
    @param owners: list of owners emails
    @return: JSON response with contract group id
    """
    contract_group_instance = do_get_contract_group(
        user_profile=user_profile,
        owners=owners,
        executor=executor,
        contract_hash=contract_hash
    )
    result = dict()
    result["contract_group"] = contract_group_instance.id
    result["stream"] = contract_group_instance.strem.name
    return json_success(result)
