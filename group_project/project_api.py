''' API calls with respect group projects'''
import json
import datetime

from .json_requests import GET, POST, PUT, DELETE
from .api_error import api_error_protect

WORKGROUP_API = 'api/workgroups'
PEER_REVIEW_API = 'api/peer_reviews'
WORKGROUP_REVIEW_API = 'api/workgroup_reviews'
USERS_API = 'api/users'
SUBMISSION_API = 'api/submissions'

def _build_date_field(json_date_string_value):
    ''' converts json date string to date object '''
    try:
        return datetime.datetime.strptime(
            json_date_string_value,
            '%Y-%m-%dT%H:%M:%SZ'
        )
    except ValueError:
        return None

class ProjectAPI(object):

    _api_server_address = None

    def __init__(self, address):
        self._api_server_address = address

    @api_error_protect
    def get_peer_review_items_for_group(self, group_id):
        response = GET(
            '{}/{}/{}/peer_reviews/'.format(
                self._api_server_address,
                WORKGROUP_API,
                group_id
            )
        )
        return json.loads(response.read())


    @api_error_protect
    def update_peer_review_assessment(self, question_data):
        response = PUT(
            '{}/{}/{}/'.format(
                self._api_server_address,
                PEER_REVIEW_API,
                question_data['id']
            ),
            question_data
        )
        return json.loads(response.read())


    @api_error_protect
    def create_peer_review_assessment(self, question_data):
        response = POST(
            '{}/{}/'.format(
                self._api_server_address,
                PEER_REVIEW_API
            ),
            question_data
        )
        return json.loads(response.read())

    @api_error_protect
    def delete_peer_review_assessment(self, assessment_id):
        response = DELETE(
            '{}/{}/{}/'.format(
                self._api_server_address,
                PEER_REVIEW_API,
                assessment_id
            )
        )

    @api_error_protect
    def get_workgroup_review_items_for_group(self, group_id):
        response = GET(
            '{}/{}/{}/workgroup_reviews/'.format(
                self._api_server_address,
                WORKGROUP_API,
                group_id
            )
        )
        return json.loads(response.read())


    @api_error_protect
    def update_workgroup_review_assessment(self, question_data):
        response = PUT(
            '{}/{}/{}/'.format(
                self._api_server_address,
                WORKGROUP_REVIEW_API,
                question_data['id']
            ),
            question_data
        )
        return json.loads(response.read())


    @api_error_protect
    def create_workgroup_review_assessment(self, question_data):
        response = POST(
            '{}/{}/'.format(
                self._api_server_address,
                WORKGROUP_REVIEW_API
            ),
            question_data
        )
        return json.loads(response.read())

    @api_error_protect
    def delete_workgroup_review_assessment(self, assessment_id):
        response = DELETE(
            '{}/{}/{}/'.format(
                self._api_server_address,
                WORKGROUP_REVIEW_API,
                assessment_id
            )
        )

    def get_peer_review_items(self, reviewer_id, peer_id, group_id):
        group_peer_items = self.get_peer_review_items_for_group(group_id)
        return [pri for pri in group_peer_items if pri['reviewer'] == reviewer_id and (pri['user'] == peer_id or pri['user'] == int(peer_id))]

    def get_user_peer_review_items(self, user_id, group_id):
        group_peer_items = self.get_peer_review_items_for_group(group_id)
        return [pri for pri in group_peer_items if pri['user'] == user_id or pri['user'] == int(user_id)]

    def submit_peer_review_items(self, reviewer_id, peer_id, group_id, data):
        # get any data already there
        current_data = {pi['question']: pi for pi in self.get_peer_review_items(reviewer_id, peer_id, group_id)}
        for k,v in data.iteritems():
            if k in current_data:
                question_data = current_data[k]

                if question_data['answer'] != v:
                    if len(v) > 0:
                        # update with relevant data
                        del question_data['created']
                        del question_data['modified']
                        question_data['answer'] = v

                        self.update_peer_review_assessment(question_data)
                    else:
                        self.delete_peer_review_assessment(question_data['id'])

            elif len(v) > 0:
                question_data = {
                    "question": k,
                    "answer": v,
                    "workgroup": group_id,
                    "user": peer_id,
                    "reviewer": reviewer_id,
                }
                self.create_peer_review_assessment(question_data)

    def get_workgroup_review_items(self, reviewer_id, group_id):
        group_review_items = self.get_workgroup_review_items_for_group(group_id)
        return [gri for gri in group_review_items if gri['reviewer'] == reviewer_id]

    def submit_workgroup_review_items(self, reviewer_id, group_id, data):
        # get any data already there
        current_data = {ri['question']: ri for ri in self.get_workgroup_review_items(reviewer_id, group_id)}
        for k,v in data.iteritems():
            if k in current_data:
                question_data = current_data[k]

                if question_data['answer'] != v:
                    if len(v) > 0:
                        # update with relevant data
                        del question_data['created']
                        del question_data['modified']
                        question_data['answer'] = v

                        self.update_workgroup_review_assessment(question_data)
                    else:
                        self.delete_workgroup_review_assessment(question_data['id'])

            elif len(v) > 0:
                question_data = {
                    "question": k,
                    "answer": v,
                    "workgroup": group_id,
                    "reviewer": reviewer_id,
                }
                self.create_workgroup_review_assessment(question_data)


    @api_error_protect
    def get_workgroup_by_id(self, group_id):
        response = GET(
            '{}/{}/{}/'.format(
                self._api_server_address,
                WORKGROUP_API,
                group_id
            )
        )
        return json.loads(response.read())

    @api_error_protect
    def get_user_workgroup_for_course(self, user_id, course_id):
        response = GET(
            '{}/{}/{}/workgroups/?course={}'.format(
                self._api_server_address,
                USERS_API,
                user_id,
                course_id
            )
        )

        workgroups_list = json.loads(response.read())

        if workgroups_list['count'] < 1:
            return None

        return self.get_workgroup_by_id(workgroups_list['results'][0]['id'])

    @api_error_protect
    def get_user_details(self, user_id):
        response = GET(
            '{}/{}/{}'.format(
                self._api_server_address,
                USERS_API,
                user_id,
            )
        )
        return json.loads(response.read())

    @api_error_protect
    def get_group_grade(self, group_id):
        print "Faking final grade"
        # TODO: get final grade from api_call
        return "80"

    @api_error_protect
    def create_submission(self, submit_hash):
        response = POST(
            '{}/{}/'.format(
                self._api_server_address,
                SUBMISSION_API
            ),
            submit_hash
        )

        return json.loads(response.read())

    @api_error_protect
    def get_workgroup_submissions(self, group_id):
        response = GET(
            '{}/{}/{}/submissions/'.format(
                self._api_server_address,
                WORKGROUP_API,
                group_id,
            )
        )

        return json.loads(response.read())


    def get_latest_workgroup_submissions_by_id(self, group_id):
        submission_list = self.get_workgroup_submissions(group_id)

        submissions_by_id = {}
        for submission in submission_list:
            submission_id = submission['document_id']
            if submission_id in submissions_by_id:
                last_modified = _build_date_field(submissions_by_id[submission_id]["modified"])
                this_modified = _build_date_field(submission["modified"])
                if this_modified > last_modified:
                    submissions_by_id[submission["document_id"]] = submission
            else:
                submissions_by_id[submission["document_id"]] = submission

        return submissions_by_id


