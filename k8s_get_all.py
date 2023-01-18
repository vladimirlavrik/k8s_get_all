from kubernetes import client, config
from pprint import pprint
from tabulate import tabulate
from kubernetes.client import ApiException


class Kubernetes:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.client = client
        self.client.ApiClient = client.ApiClient()

    def get_apis(self):
        apis = []
        for api in self.client.ApisApi().get_api_versions().groups:
            apis.append(api.preferred_version.group_version)
        return apis

    def get_full_apis_info(self):
        apis_info = []
        for item in self.get_apis():
            path = f'/apis/{item}'
            response = self.client.ApiClient.call_api(
                path,
                'GET',
                response_type='object'
            )
            for jtem in response[0]['resources']:
                if jtem['kind'] != 'MetricValueList' and '/' not in jtem['name']:
                    apis_info.append(
                        {
                            'plural': jtem['name'],
                            'namespaced': jtem['namespaced'],
                            'name': item.split('/')[0],
                            'version': item.split('/')[1]
                        }
                    )
        return apis_info

    def get_cr(self, apis, namespaced, namespace='default'):
        crs = []
        for item in apis:
            if item['namespaced']:
                if namespaced:
                    try:
                        _response = self.client.CustomObjectsApi().list_namespaced_custom_object(
                            item['name'],
                            item['version'],
                            namespace,
                            item['plural']
                        )
                        if _response['items']:
                            for res in _response['items']:
                                crs.append(
                                    [
                                        res['metadata']['name'],
                                        item['plural'],
                                        namespace
                                    ]
                                )
                    except ApiException:
                        pprint('GET is not allowed to {} !!!'.format(item['plural']))
                        continue
            else:
                if not namespaced:
                    try:
                        _response = self.client.CustomObjectsApi().list_cluster_custom_object(
                            item['name'],
                            item['version'],
                            item['plural']
                        )
                        if _response['items']:
                            for res in _response['items']:
                                crs.append(
                                    [
                                        res['metadata']['name'],
                                        item['plural'],
                                        "N/A"
                                    ]
                                )
                    except ApiException:
                        pprint('GET is not allowed to {} !!!'.format(item['plural']))
                        continue
        return crs


def print_table(data, headers):
    print(tabulate(data, headers))


def main():
    k = Kubernetes()
    result = k.get_cr(k.get_full_apis_info(), False, 'default')
    print_table(result, headers=['name', 'kind', 'namespace'])


if __name__ == '__main__':
    main()

