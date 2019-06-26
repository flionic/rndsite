import logging
import re
import sys

__author__ = "Alexey Flionic (flionicj@gmail.com)"
__version__ = "0.2.0"
__copyright__ = "Copyright (c) 2012-2019 Flionic"
# Use of this source code is governed by the MIT license.
# import rnd; a = rnd.RandomizeSiteAttrs('rabota_html.zip')
# import rnd; a = rnd.RandomizeSiteAttrs('vizitka.zip')
__license__ = "MIT"
import fileinput
import os
import random
import shutil
import string
import zipfile

import arrow
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-18s %(name)s | %(levelname)-6s | %(message)s',
                    # format='%(asctime)s %(name)-12s: %(levelname)-8s | %(message)s',
                    datefmt='%b %d %H:%M:%S',
                    filename=os.path.realpath(f'{arrow.now().strftime("rsa_%Y%m%d.log")}'),
                    filemode='a+')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class RandomizeSiteAttrs:
    def __init__(self, in_zip, source_types='html', work_types='html css js', out_path=None, debug=True):
        self.in_zip = in_zip
        if source_types is not None:
            self.source_types = source_types
        if work_types is not None:
            self.work_types = work_types
        if out_path is not None:
            # self.out_path = out_path
            self.out_path = os.path.join(out_path, 'rsa')
        else:
            # self.out_path = os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(in_zip))), 'rsa')
            self.out_path = os.path.join(os.path.realpath(in_zip), 'rsa')
        print(self.out_path)
        os.makedirs(self.out_path) if not os.path.exists(self.out_path) else None
        if debug is not None and debug is True:
            console.setLevel(logging.DEBUG)
        else:
            console.setLevel(logging.INFO)
        self.project_name = os.path.basename(self.in_zip)[:-4]
        self.project_title = f"{self.project_name}_rsa_%Y%m%d-%H%M%S"
        self.start_time = arrow.now()
        # self.logger = set_logger(debug)
        self.logger = logging.getLogger(f'{self.project_name}')
        self.source_files = []
        self.work_files = []
        self.job_attrs = []
        self.attrs_map = {}
        self.out_zip = None
        self.out_name = None
        self.end_time = None

        self.logger.info(f'Start RandomizeSiteAttrs for {self.project_name}')

        self.unzip_site()
        self.get_job_files()
        self.get_src_attrs()
        self.replace_attrs()
        self.zip_site()
        self.rm_job_temp()
        self.job_done()

    # def set_logger(self, debug):
    #     logging.basicConfig(level=logging.DEBUG,
    #                         format='%(asctime)-18s %(name)s | %(levelname)-6s | %(message)s',
    #                         # format='%(asctime)s %(name)-12s: %(levelname)-8s | %(message)s',
    #                         datefmt='%b %d %H:%M:%S',
    #                         filename=os.path.join(self.out_path, f'{arrow.now().strftime("rsa_%Y%m%d.log")}'),
    #                         filemode='a+')
    #     console = logging.StreamHandler()
    #     if debug is not None and debug is True:
    #         console.setLevel(logging.DEBUG)
    #         formatter = logging.Formatter('%(name)-2s | %(levelname)-2s | %(message)s')
    #     else:
    #         console.setLevel(logging.INFO)
    #         formatter = logging.Formatter('%(message)s')
    #     console.setFormatter(formatter)
    #     logging.getLogger('').addHandler(console)
    #     return logging.getLogger(f'RSA')

    def job_done(self):
        self.end_time = arrow.utcnow()
        self.logger.info(f'Done for {self.start_time.humanize(only_distance=True)}.')
        return {'zip_name': self.out_name}

    def unzip_site(self):
        self.logger.info(f'Unzip source..')
        with zipfile.ZipFile(self.in_zip, "r") as zip_ref:
            zip_ref.extractall(self.project_name)

    def zip_site(self):
        self.logger.info(f'Make RSA zip..')
        self.out_name = f'{arrow.now().strftime(self.project_title)}.zip'
        self.out_zip = os.path.join(self.out_path, self.out_name)
        with zipfile.ZipFile(self.out_zip, "w") as zip_file:
            for dirname, subdirs, files in os.walk(self.project_name):
                zip_file.write(dirname)
                for filename in files:
                    zip_file.write(os.path.join(dirname, filename))
        self.logger.info(f'RSA zip: {self.out_zip}')

    def get_job_files(self):
        self.logger.info(f'Find files for work..')
        for path, subdirs, files in os.walk(self.project_name):
            for name in files:
                type_ = name[name.rfind('.') + 1:]
                file_ = os.path.join(path, name)
                if type_ in self.source_types.split(' '):
                    self.logger.debug(f'\tFound new source file: {file_}')
                    self.source_files.append(file_)
                if type_ in self.work_types.split(' '):
                    self.logger.debug(f'\tFound new work file: {file_}')
                    self.work_files.append(file_)

    def rm_job_temp(self):
        self.logger.info(f'Remove temp directory..')
        shutil.rmtree(self.project_name)

    @staticmethod
    def attr_gen():
        return str(''.join(random.choice(string.ascii_letters) for _ in range(random.randint(8, 15))))

    def get_src_attrs(self):
        self.logger.info('Get source tags..')
        for job_file in self.source_files:
            self.logger.debug(f'\tOpen {job_file} in html parser')
            with open(job_file) as fp:
                soup = BeautifulSoup(fp, "html.parser")
            for element in soup.find_all(class_=True):
                self.logger.debug(f'\t\tFound class: {element["class"]}')
                self.job_attrs.extend(element["class"])
            for element in soup.find_all(id=True):
                self.logger.debug(f'\t\tFound id: {element["id"]}')
                self.job_attrs.extend([element["id"]])

    # TODO: отдельно сгенерировать карту атрибутов, открывать файл и циклом по нему проходиться, привязать регулярки к типу файла
    def replace_attrs(self):
        self.logger.info('Randomize tags..')
        attrs_cnt = len(set(self.job_attrs))
        for idx, attr_ in enumerate(list(set(self.job_attrs))):
            new_attr = self.attr_gen()
            self.attrs_map[attr_] = new_attr
            # sys.stdout.write("\033[K") # sys.stdout.write("\033[F") # print("\033[H\033[J") # os.system('clear')
            print(f'\033[FRandomize tags.. {(idx+1)/attrs_cnt:.1%}')
            self.logger.debug(f'\tTag {idx+1}/{len(set(self.job_attrs))}: {attr_} -> {new_attr}')
            with fileinput.FileInput(tuple(self.work_files), inplace=True) as file:
                # self.logger.info(f'Parse lines from {file.filename()}')
                for line in file:
                    line = re.sub(f'(?P<start>(?:id|class)=\"){attr_}(?P<end>\")', f'\g<start>{new_attr}\g<end>', line)
                    line = re.sub(f'(?P<start>class.*?[\s\"])({attr_})(?P<end>[\s\"].*?\>)', f'\g<start>{new_attr}\g<end>', line)
                    line = re.sub(f'(?P<attr>[\.#])({attr_})(?P<end>[\"\'\s\.#:,{"{"}])', f'\g<attr>{new_attr}\g<end>', line)
                    print(line, end='')
