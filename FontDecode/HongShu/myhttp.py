import logging
import requests


def request_get(url, headers, retry_times=5):
    """
    :param url:
    :param headers:
    :param retry_times:
    :return:
    """
    for i in range(retry_times):
        try:
            resp = requests.get(url, headers=headers)
        except Exception as e:
            logging.warning('request error retry %s' % url)
            continue

        return resp


def request_post(url, data, headers, retry_times=5):
    """
    :param url:
    :param data:
    :param headers:
    :param retry_times:
    :return:
    """
    for i in range(retry_times):
        try:
            resp = requests.post(url, data, headers=headers)
        except Exception as e:
            logging.warning('request error retry %s' % url)
            continue
        return resp


def request(request_type, url, headers, data=None, retry_times=5, return_type="text"):
    """
    :param request_type:
    :param url:
    :param headers:
    :param data:
    :param retry_times:
    :param return_type:
    :return:
    """
    if request_type == 'get':
        resp = request_get(url, headers, retry_times)

    if request_type == 'post':
        resp = request_post(url, data, headers, retry_times)
    if not resp:
        return resp

    if return_type == 'text':
        return resp.text

    if return_type == 'json':
        try:
            resp = resp.json()
            return resp
        except Exception as e:
            logging.warning('parse json error %s' % str(e))
            return None
