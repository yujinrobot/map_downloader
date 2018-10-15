import requests
import os
import socket
import shutil


def write_to_file(path, data, binary=True):
    if binary is True:
        f = open(path, 'wb')
    else:
        f = open(path, "w")
    f.write(data)
    f.close()


def get_robot_uuid():
    username = os.path.expanduser("~").split('/')[-1]
    return username + '@' + socket.gethostname()


class Conf_downloader():
    def __init__(self, worker_uuid, skip_map=False):
        print ("Attempting to download data for " + worker_uuid)
        self.hostname = 'concert'
        self.base_url = 'http://' + self.hostname
        self.show_target()
        self.uuid = worker_uuid
        self.worker_data = None
        self.configs = None
        self.default_map = None
        self.skip_map = skip_map

    def show_target(self):
        try:
            ip = socket.gethostbyname(self.hostname)
        except socket.gaierror:
            print("hostname : " + self.hostname +" cannot be resolved. Please ensure that the hostname and IP are"
                                                 "correctly set in /etc/host file.")
        print("Attempting to connect to " + self.base_url + " with ip: " + ip)

    def get_worker_data(self):
        url = self.base_url + ':10602/scheduler/v0/workers?uuid=' + self.uuid
        response = requests.get(url)
        self.worker_data = response.json()
        if len(self.worker_data) < 1:
            print ("Worker with " + str(self.uuid) + " uuid not found on Server!")
            self.generate_worker_on_concert()
            exit(1)
        else:
            self.worker_data = self.worker_data[0]

    def generate_worker_on_concert(self):
        print("Generating worker on concert server...")
        username = self.uuid.split('@')[0]
        requests.put('http://concert:10602/scheduler/v0/workers/',
                     json={'uuid': self.uuid, 'name': username})
        print("Worker successfully generated... Please configure your new robot on concert server"
              "(fleet management UI > worker configuration)")

    def download_semantics(self, path=None, filename='semantics.yaml'):
        try:
            default_map = self.configs.get('default_map')
            semantic_url = self.base_url + ':10605/management/export?ext=yaml&download=true&defaultmap=' + default_map
            semantic_data = requests.get(semantic_url)
            semantic_data.raise_for_status()
        except requests.HTTPError as err:
            print ("Failed to download semantic file :" + semantic_data.text.encode('utf-8')
                   + " HTTP error: " + str(err))
            return

        home = os.path.expanduser("~")
        dest_folder = home + '/' + 'semantics'
        if os.path.isdir(dest_folder) is False:
            print "Creating semantic folder under " + dest_folder
            os.makedirs(dest_folder)
        dest_file_path = dest_folder + '/' + filename
        write_to_file(dest_file_path, semantic_data.text.encode('utf-8'))
        print("Successfully saved semantics under " + dest_file_path)

    def load_n_check_configs(self):
        if 'configs' in self.worker_data:
            self.configs = self.worker_data.get('configs')
            self.default_map = self.configs.get('default')
        else:
            print ("Worker with " + str(self.uuid) + " does not have configs on Server, exiting...")
            exit(2)

    def download_task_definition(self, filename='task_definition.yaml'):
        try:
            url = self.base_url + ':10605/taskdefinition'
            tasks_definition_data = requests.post(url, json=self.configs.get('args_task_definition'))
            tasks_definition_data.raise_for_status()
        except requests.HTTPError as err:
            print ("Failed to download task definition file : " + tasks_definition_data.text.encode('utf-8')
                   + " HTTP error: " + str(err))
            return

        home = os.path.expanduser("~")
        dest_folder = home + '/' + '.ros/' + 'gopher/' + 'rocon'
        if os.path.isdir(dest_folder) is False:
            print "Creating tasks_definition folder under " + dest_folder
            os.makedirs(dest_folder)
        dest_file_path = dest_folder + '/' + filename
        write_to_file(dest_file_path, tasks_definition_data.text.encode('utf-8'))
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

    def verify_map(self, map):
        if map.get("site_id") is None:
            return False
        else:
            return True

    def copy_dslam_file_to_map_name(self, map_name):
        home = os.path.expanduser("~")
        map_folder_path = home + '/' + '.ros/' + 'gopher/' + 'maps/'
        file_list = os.listdir(map_folder_path)
        for file in file_list:
            if file.split('.')[-1] == 'dslam':
                to_copy_path = map_folder_path + file
                dest_path = map_folder_path + map_name + ".dslam"
                try:
                    shutil.copy(to_copy_path, dest_path)
                except shutil.Error:
                    pass
                return
        print("No .dslam file has been found under " + map_folder_path + " please add one and retry")

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

            if self.verify_map(map) is True:
                saved = []
                self.copy_dslam_file_to_map_name(map.get('uuid'))
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
            else:
                print('Map with uuid: ' + map.get('uuid') + ' won\'t be downloaded as it does not define'
                                                            ' a site_id')

    def download_armarker(self):
        map_list_url = self.base_url + ':10605/configuration/maps'
        map_list = requests.get(map_list_url).json()

        home = os.path.expanduser("~")
        dest_folder = home + '/' + '.ros/' + 'gopher/' + 'hps/'
        if os.path.isdir(dest_folder) is False:
            print "Creating hps folder under " + dest_folder
            os.makedirs(dest_folder)

        for map in map_list:
            if self.verify_map(map):
                try:
                    url = self.base_url + ':10605/armarker/' + str(map.get('id'))
                    armarker_data = requests.post(url)
                    armarker_data.raise_for_status()
                except requests.HTTPError as err:
                    print ("Failed to download AR Marker file : " + armarker_data.text + " HTTP error: " + str(err))
                    continue
                dest_file_path = dest_folder + map.get('uuid') + '.ar_marker.hp'
                write_to_file(dest_file_path, armarker_data.text)
                print("Successfully saved hps file under " + dest_file_path)
            else:
                print('AR Marker belongs to Map with uuid: ' + map.get('uuid') + ' won\'t be downloaded as it does not'
                                                                ' define a site_id')

    def process(self):
        print self.get_worker_data()
        self.load_n_check_configs()
        self.download_semantics()
        self.download_task_definition()
        if self.skip_map is False:
            self.download_maps()
        else:
            print("SKIPPING MAP DOWNLOAD !")
        self.download_armarker()
