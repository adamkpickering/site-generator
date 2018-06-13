#!/usr/bin/env python3

# ideas:
# - following compilation, scan for broken links
# - consider splitting directories and files

import os
import shutil
from jinja2 import Template, Environment, FileSystemLoader
from subprocess import run, PIPE, STDOUT


HEADER = '{% extends "base.html" %}\n{% block content %}\n'
FOOTER = '{% endblock %}\n'


class File(object):
    """Represents a file in a Directory"""

    def __init__(self, parent, file_name):
        self.parent = parent
        self.name, self.extension = file_name.split('.')
        self.content = self.get_content()
        print("initializing File {}".format(self.dest_path))

    def __repr__(self):
        return self.source_path
        #return self.name + '.' + self.extension

    def get_content(self):
        cmd = ['markdown', self.source_path]
        content = run(cmd, stdout=PIPE, stderr=STDOUT).stdout.decode()
        return content

    def compile(self, environment):
        print("compiling {}".format(self.dest_path))
        content = self.get_content()
        wrapped_content = HEADER + content + FOOTER
        #navigation = self.build_links()
        page = process_jinja2_template(environment, wrapped_content)
        with open(self.dest_path, 'w+') as fd:
            fd.write(page)

    @property
    def title(self):
        with open(self.source_path, 'r') as fd:
            title = fd.readline().split('#')[1].strip()
        return title

    @property
    def source_path(self):
        return os.path.join(self.parent.source_path, self.name + '.' + self.extension)

    @property
    def url_path(self):
        return os.path.join(self.parent.url_path, self.name + '.html')

    @property
    def dest_path(self):
        return os.path.join(self.parent.dest_path, self.name + '.html')


class Directory(object):
    """Represents the directory rolled in with it's index.md file"""

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.children = []
        self.index_path = os.path.join(self.source_path, 'index.md')
        print("initializing Directory {}".format(self.dest_path))
        self.content = self.get_content()
        self.parse_children()

    def __repr__(self):
        output = [self.name]
        for child in self.children:
            output.append(repr(child))
        return str(output)

    def get_content(self):
        cmd = ['markdown', os.path.join(self.source_path, 'index.md')]
        content = run(cmd, stdout=PIPE, stderr=STDOUT).stdout.decode()
        return content

    def parse_children(self):
        for walk in os.walk(self.source_path):
            for file in walk[2]:
                if file == 'index.md':
                    continue
                self.children.append(File(self, file))
            for directory in walk[1]:
                self.children.append(Directory(self, directory))
            break

    def build_links(self):
        links = []
        for child in self.children:
            links.append({
                'title': child.title,
                'href': child.url_path,
            })
        return links

    def compile(self, environment):
        print("compiling {}".format(self.dest_path))
        os.makedirs(self.dest_path, exist_ok=True)
        content = self.get_content()
        wrapped_content = HEADER + content + FOOTER
        navigation = self.build_links()
        page = process_jinja2_template(environment, wrapped_content, navigation=navigation)
        with open(os.path.join(self.dest_path, 'index.html'), 'w+') as fd:
            fd.write(page)
        for child in self.children:
            child.compile(environment)

    @property
    def title(self):
        # add handling for case where index.md doesn't exist
        with open(self.index_path, 'r') as fd:
            title = fd.readline().split('#')[1].strip()
        return title

    @property
    def source_path(self):
        return os.path.join(self.parent.source_path, self.name)

    @property
    def url_path(self):
        return os.path.join(self.parent.url_path, self.name + '/')

    @property
    def dest_path(self):
        return os.path.join(self.parent.dest_path, self.name + '/')


class Site(Directory):

    def __init__(self, source_directory, dest_directory):
        self.children = []
        self.source_directory = source_directory
        self.dest_directory = dest_directory
        print("initializing Site {}".format(source_directory))
        self.parse_children()

    def __repr__(self):
        output = []
        for child in self.children:
            output.append(repr(child))
        return str(output)

    def compile(self, environment):
        print("compiling {}".format(self.dest_path))
        content = self.get_content()
        wrapped_content = HEADER + content + FOOTER
        navigation = self.build_links()
        page = process_jinja2_template(environment, wrapped_content, navigation=navigation)
        with open(os.path.join(self.dest_path, 'index.html'), 'w+') as fd:
            fd.write(page)
        for child in self.children:
            child.compile(environment)

    def clean(self):
        for node in os.walk(self.dest_path):
            _, dirs, files = node
            break
        for dir in dirs:
            shutil.rmtree(os.path.join(self.dest_path, dir))
        for file in files:
            os.remove(os.path.join(self.dest_path, file))

    @property
    def source_path(self):
        return self.source_directory

    @property
    def url_path(self):
        return '/'

    @property
    def dest_path(self):
        return self.dest_directory


def process_jinja2_template(environment, content, **kwargs):
    template = environment.from_string(content)
    page = template.render(**kwargs)
    return page


if __name__ == "__main__":
    environment = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=False,
    )
    a = Site('markdown', 'site')
    a.clean()
    a.compile(environment)
