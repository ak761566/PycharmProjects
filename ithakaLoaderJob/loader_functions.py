import json
import requests



# LOADER_ENDPOINT = "http://pr2ptgpprd43.ithaka.org:9500/loader/job/multistepjob/v1/submitwithjsonandparams/LoaderJob"

loader_endpoint = "http://pr2ptgpprd43.ithaka.org:9500/loader/job/multistepjob/v1/submitwithjsonandparams/LoaderJob"
status_endpoint = "http://pr2ptgpprd43.ithaka.org:9500/loader/job/v1/status/"

HEADERS = {
    "accept": "*/*",
    "Content-Type": "application/json",
}

class LoaderFunction:
    def __init__(self):

        self.loader_end_point = ''
        self.status_end_point = ''

    def set_loader_end_point(self, loader_end_point):
        self.loader_end_point = loader_end_point

    def set_status_endpoint(self, status_end_point):
        self.status_end_point = status_end_point

    def get_loader_end_point(self):
        return self.loader_end_point

    def get_status_end_point(self):
        return self.status_end_point

    def save_json_data(self, property_file_name, loader_profile_name):

        JSON_DATA = {
            "configSourceType": "GIT",
            "propertyFileName": property_file_name,
            "loaderProfileFileName": loader_profile_name
        }

        LOADER_ENDPOINT = {
            "loader_endpoint": self.get_loader_end_point(),
            "status_endpoint": self.get_status_end_point(),

        }


        with open("loader_config.json", "w") as config_file:
            json.dump(JSON_DATA, config_file, indent=4)

        with open("endpoint_config.json", "w") as endpoint_file:
            json.dump(LOADER_ENDPOINT, endpoint_file, indent=4)

        return JSON_DATA

    def run_loader(self, json_data):
        # loader_run_response = requests.post(LOADER_ENDPOINT, json=json_data, headers=HEADERS)
        loader_run_response = requests.post(self.get_loader_end_point(), json=json_data, headers=HEADERS)

        loader_response_data = {
            "jobId": loader_run_response.json()["jobId"],
            "jobStatus": loader_run_response.json()['jobStatus'],
        }

        is_loader_ran = False
        if len(loader_run_response.json()["jobId"]) != 0:
            is_loader_ran = True
            with open("job_id.json", "w") as job_id_file:
                json.dump(loader_response_data, job_id_file, indent=4)

        return  is_loader_ran


    def check_job_status(self, job_id):
        JOB_ID = job_id

        # LOADER_JOB_STATUS_ENDPOINT = f"http://pr2ptgpprd43.ithaka.org:9500/loader/job/v1/status/{JOB_ID}"

        if len(self.get_status_end_point()) == 0:
            with open("endpoint_config.json", "r") as config_file:
                data = json.load(config_file)
                #print(data["status_endpoint"])

            self.set_status_endpoint(data["status_endpoint"])

        LOADER_JOB_STATUS_ENDPOINT = self.get_status_end_point() + JOB_ID

        job_response = requests.get(LOADER_JOB_STATUS_ENDPOINT)
        return job_response
