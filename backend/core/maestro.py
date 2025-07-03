"""
Classes to communicate with the Orchestration app
"""

import base64
import json
import os
from typing import Any
from urllib.parse import urljoin

import requests


class Maestro:

    def __init__(self, url):
        self.url = url
        self.api = MaestroApi(self.url)

    def get_processes(self) -> list:
        """Returns list of processes

        Returns:
            list: processes list
        """

        url = f"{self.url}/api/processes/"
        _response = self.api.get_request(url)
        return self.__handle_action(_response)  # type: ignore

    def start(self, pipeline, config=None) -> dict[str, Any]:  # type: ignore
        """Start process in Orchestration app.

        Args:
            pipeline (str): pipeline name.
            config (dict, optional): pipeline config. Defaults to None.

        Returns:
            dict: process info
        """

        url = f"{self.url}/api/processes/"

        if config:
            config = json.dumps(config)

        payload = json.dumps(
            {
                "pipeline": pipeline,
                "used_config": config,
            }
        )

        _response = self.api.post_request(url, payload=payload)
        return self.__handle_action(_response)  # type: ignore

    def status(self, orchest_process_id) -> dict:
        """Get process status in Orchestration app.

        Args:
            orchest_process_id (int): orchestration process ID

        Returns:
            dict: process status
        """

        url = f"{self.url}/api/processes/{orchest_process_id}/status/"
        _response = self.api.get_request(url)
        return self.__handle_action(_response)  # type: ignore

    def stop(self, orchest_process_id) -> dict:
        """Stop process in Orchestration app.

        Args:
            orchest_process_id (int): orchestration process ID

        Returns:
            dict: process info
        """

        url = f"{self.url}/api/processes/{orchest_process_id}/stop/"
        _response = self.api.get_request(url)
        return self.__handle_action(_response)  # type: ignore

    def pipelines(self) -> dict:
        """Gets pipelines in Orchestration app.

        Returns:
            dict: pipelines
        """

        url = f"{self.url}/api/pipelines/"
        _response = self.api.get_request(url)
        return self.__handle_action(_response)  # type: ignore

    def sysinfo(self) -> dict:
        """Gets Orchestration app information.

        Returns:
            dict: Orchestration app information
        """

        url = f"{self.url}/api/sysinfo/"
        _response = self.api.get_request(url)
        return self.__handle_action(_response)  # type: ignore

    def __handle_action(self, _response) -> dict:
        """Handle actions related to orchestration processing control

        Args:
            _response (request.Response): Response object

        Returns:
            dict
        """

        if "success" in _response and _response.get("success") is False:
            raise requests.exceptions.RequestException(_response)

        return _response.get("data")


class MaestroApi:
    """Responsible for managing all requests to the Orchestration app."""

    def __init__(self, url):
        """Initializes communication with the Orchestration app.

        Args:
            url (str): orchestration url.
        """

        self.__url = url
        self.__token = self.get_token()

    @staticmethod
    def __get_credential() -> bytes:
        """Returns a credential to obtain a valid token in the orchestration
        app.

        Returns:
            credential
        """

        client_id = os.getenv("ORCHEST_CLIENT_ID")
        client_secret = os.getenv("ORCHEST_CLIENT_SECRET")

        raw_credential = "{0}:{1}".format(client_id, client_secret)
        return base64.b64encode(raw_credential.encode("utf-8"))

    def __check_response(self, api_response) -> dict:
        """Checks for possible HTTP errors in the response.

        Args:
            api_response (request.Response): Response object

        Returns:
            dict: response content.
        """
        status_code = api_response.status_code

        data = {
            "status_code": status_code,
            "message": str(),
            "data": str(),
            "response_object": api_response,
        }

        content_type = api_response.headers.get("content-type", "")

        if 200 <= status_code < 300:
            data.update({"success": True, "message": "Request completed"})
            if status_code != 204 and content_type.strip().startswith(
                "application/json"
            ):
                data.update({"data": api_response.json()})
        else:
            if content_type.strip().startswith("application/json"):
                content = api_response.json()
                detail = content.get("detail", content)
                message = content.get("error", detail)
            else:
                message = api_response.text
            data.update({"success": False, "message": message})

        return data

    def __send_request(
        self,
        prerequest,
        stream=False,
        timeout=None,
        verify=True,
        cert=None,
        proxies=None,
    ) -> dict:
        """Sends PreparedRequest object.

        Args:
            prerequest (requests.PreparedRequest): PreparedRequest object
            stream (optional): Whether to stream the request content.
            timeout (float or tuple) (optional): How long to wait for the
                server to send data before giving up, as a float, or a
                (connect timeout, read timeout) tuple.
            verify (optional): Either a boolean, in which case it controls
                whether we verify the servers TLS certificate, or a string,
                in which case it must be a path to a CA bundle to use
            cert (optional): Any user-provided SSL certificate to be trusted.
            proxies (optional): The proxies dictionary to apply to the request.

        Returns:
            dict: response content

            Example: {
                "status_code": int,
                "message": str,
                "data": str,
                "success": bool,
                "response_object": request.Response
            }
        """

        data = {
            "success": False,
            "message": "",
            "response_object": None,
        }

        try:
            api_session = requests.Session()
            api_response = api_session.send(
                prerequest,
                stream=stream,
                timeout=timeout,
                verify=verify,
                cert=cert,
                proxies=proxies,
            )
            data.update(self.__check_response(api_response))
        except requests.exceptions.HTTPError as errh:
            message = f"Http Error: {errh}"
            data.update(
                {
                    "success": False,
                    "message": message,
                    "error": requests.exceptions.HTTPError,
                }
            )
        except requests.exceptions.ConnectionError as errc:
            message = f"Connection Error: {errc}"
            data.update(
                {
                    "success": False,
                    "message": message,
                    "error": requests.exceptions.ConnectionError,
                }
            )
        except requests.exceptions.Timeout as errt:
            message = f"Timeout Error: {errt}"
            data.update(
                {
                    "success": False,
                    "message": message,
                    "error": requests.exceptions.Timeout,
                }
            )
        except requests.exceptions.RequestException as err:
            message = f"Request Error: {err}"
            data.update(
                {
                    "success": False,
                    "message": message,
                    "error": requests.exceptions.RequestException,
                }
            )

        return data

    def get_default_headers(self):
        """Gets default header to Orchestration app."""

        token_type = self.__token.get("token_type")
        token = self.__token.get("access_token")
        authorization = f"{token_type} {token}"

        headers = requests.utils.default_headers()
        headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": authorization,
            }
        )

        return headers

    def get_request(self, url, params=None, headers=None) -> dict:
        """Get a record from the API.

        Args:
            url (str): url to get
            params (dict, optional): params to get. Defaults to None.
            headers (dict, optional): dictionary of headers to send.
                Defaults to None.

        Returns:
            dict: data of the request.
        """

        # if not headers or not isinstance(headers, dict):
        if not headers:
            headers = self.get_default_headers()

        _response = requests.Request("GET", url, params=params, headers=headers)
        return self.__send_request(_response.prepare())

    def post_request(self, url, payload, headers=None) -> dict:
        """Posts a record to the API.

        Args:
            url (str): url to post.
            payload (str): payload to post.
            headers (dict, optional): dictionary of headers to send.
                Defaults to None.

        Returns:
            dict: data of the request.
        """

        # if not headers or not isinstance(headers, dict):
        if not headers:
            headers = self.get_default_headers()

        req = requests.Request(
            "POST",
            url,
            data=payload,
            headers=headers,
        )
        return self.__send_request(req.prepare())

    def options_request(self, url, headers=None) -> dict:
        """Returns the options and settings for a given endpoint.

        Args:
            url (str): url to get
            params (dict, optional): params to get. Defaults to None.
            headers (dict, optional): dictionary of headers to send.
                Defaults to None.

        Returns:
            dict: data of the request.
        """

        if not headers or not isinstance(headers, dict):
            headers = self.get_default_headers()

        req = requests.Request(
            "OPTIONS",
            url,
            headers=headers,
        )
        return self.__send_request(req.prepare())

    def delete_request(self, url, headers=None) -> dict:
        """Remove a record from the API.

        Args:
            url (str): url to delete with the record id.
            headers (dict, optional): dictionary of headers to send.
                Defaults to None.

        Returns:
            dict: status and message of the request.
        """

        req = requests.Request(
            "DELETE",
            url,
            headers=headers,
        )
        _response = self.__send_request(req.prepare())

        if _response.get("status_code") == 400:
            return {
                "success": False,
                "message": "The server failed to perform the operation.",
                "status_code": 400,
            }

        return _response

    def get_token(self) -> dict:
        """Gets access token in Orchestration app

        Returns:
            dict: _description_
        """

        credential = self.__get_credential()
        token_url = urljoin(self.__url, "o/token/")
        token_auth = f"Basic {credential.decode()}"
        payload = "grant_type=client_credentials"

        headers = requests.utils.default_headers()
        headers.update(
            {
                "Cache-Control": "no-cache",
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": token_auth,
            }
        )

        _response = self.post_request(token_url, payload, headers=headers)

        if "success" in _response and _response.get("success") is False:
            cls_err = _response.get("error", requests.exceptions.RequestException)
            raise cls_err(_response.get("message"))

        return _response.get("data")  # type: ignore

    def token_is_valid(self):
        """
        Checks if the token is valid, otherwise stops class initialization.
        """
        # TODO
        return True


if __name__ == "__main__":
    maestro = Maestro("http://orchestrator")
    processes = maestro.get_processes()
    print(processes)
