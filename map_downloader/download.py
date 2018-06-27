import requests
import os
import socket


def write_to_file(path, data):
    f = open(path, 'wb')
    f.write(data)
    f.close()


def get_robot_uuid():
    username = os.path.expanduser("~").split('/')[-1]
    return username + '@' + socket.gethostname()


class Conf_downloader():
    def __init__(self, worker_uuid):
        print ("Attempting data download for " + worker_uuid)
        self.base_url = 'http://192.168.10.241'
        self.uuid = worker_uuid
        self.worker_data = None
        self.configs = None
        self.default_map = None

    def get_worker_data(self):
        url = self.base_url + ':10602/scheduler/v0/workers?uuid=' + self.uuid
        response = requests.get(url)
        self.worker_data = response.json()
        if len(self.worker_data) < 1:
            print ("Worker with " + str(self.uuid) + " uuid not found on Server, exiting...")
            exit(1)
        else:
            self.worker_data = self.worker_data[0]

    def download_semantics(self, path=None, filename='semantics.yaml'):
        default_map = self.configs.get('default_map')
        semantic_url = self.base_url + ':10605/management/export?ext=yaml&download=true&defaultmap=' + default_map
        semantic_data = requests.get(semantic_url).text
        home = os.path.expanduser("~")
        dest_folder = home + '/' + 'semantics'
        if os.path.isdir(dest_folder) is False:
            print "Creating semantic folder under " + dest_folder
            os.makedirs(dest_folder)
        dest_file_path = dest_folder + '/' + filename
        write_to_file(dest_file_path, semantic_data)
        print("Successfully saved semantics under " + dest_file_path)


    def load_n_check_configs(self):
        if 'configs' in self.worker_data:
            self.configs = self.worker_data.get('configs')
            self.default_map = self.configs.get('default')
        else:
            print ("Worker with " + str(self.uuid) + " does not have configs on Server, exiting...")
            exit(2)

    def download_task_definition(self, filename='tasks_definition.yaml'):
        url = self.base_url + ':10605/taskdefinition'
        tasks_definition_data = requests.post(url, json=self.configs.get('args_task_definition')).text
        home = os.path.expanduser("~")
        dest_folder = home + '/' + '.ros/' + 'gopher/' + 'rocon'
        if os.path.isdir(dest_folder) is False:
            print "Creating tasks_definition folder under " + dest_folder
            os.makedirs(dest_folder)
        dest_file_path = dest_folder + '/' + filename
        write_to_file(dest_file_path, tasks_definition_data)
        print("Successfully saved tasks definition under " + dest_file_path)

    def apply_locked_maps(self, map_list):
        locked_maps_dict = self.configs.get('map_lock')
        if locked_maps_dict is not None:
            for map in map_list:
                if map.get('uuid') in locked_maps_dict:
                    uuid = map.get('uuid')
                    img_path = locked_maps_dict[uuid].get('gridmap')
                    nvmap_path = locked_maps_dict[uuid].get('nvmap')
                    metadata_path = locked_maps_dict[uuid].get('metadata')

                    if img_path is not None:
                        map['img_path'] = img_path
                    if nvmap_path is not None:
                        map['map_data']['nvmap_path'] = nvmap_path
                    if metadata_path is not None:
                        map['map_data']['metadata_path'] = metadata_path
        return map_list

    def debug_map_list(self, map_list):
        for map in map_list:
            print('--------------------------------')
            print map.get('uuid')
            print map.get('img_path')
            print map.get('map_data').get('nvmap_path')
            print map.get('map_data').get('metadata_path')

    def download_maps(self):
        map_list_url = self.base_url + ':10605/configuration/maps' #':10605/public/' #
        map_list = requests.get(map_list_url).json()
        map_list = self.apply_locked_maps(map_list)

        base_dl_url = self.base_url + ':10605/public/'
        for map in map_list:
            img_path = map.get('img_path')
            nvmap_path = map.get('map_data').get('nvmap_path')
            metadata_path = map.get('map_data').get('metadata_path')

            home = os.path.expanduser("~")
            dest_folder = home + '/' + '.ros/' + 'gopher/' + 'maps/'
            if os.path.isdir(dest_folder) is False:
                print "Creating map folder under " + dest_folder
                os.makedirs(dest_folder)

            file_path = dest_folder + map.get('uuid')

            saved = []
            if img_path is not None:
                map_img = requests.get(base_dl_url + img_path)
                write_to_file(file_path + '.png', map_img.content)
                saved.append(file_path + '.png')

            if nvmap_path is not None:
                nvmap = requests.get(base_dl_url + nvmap_path)
                write_to_file(file_path + '.nvmap', nvmap.content)
                saved.append(file_path + '.nvmap')

            if metadata_path is not None:
                metadata = requests.get(base_dl_url + metadata_path)
                write_to_file(file_path + '.grid', metadata.content)
                saved.append(file_path + '.grid')

            for file_saved in saved:
                print ("Map related file successfully saved under " + file_saved)

    def process(self):
        self.get_worker_data()
        self.load_n_check_configs()
        self.download_semantics()
        self.download_task_definition()
        self.download_maps()
