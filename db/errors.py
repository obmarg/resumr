'''
Contains the various database related exceptions
'''


class SectionNotFound(Exception):
    pass


class RepoNotFound(Exception):
    pass


class MasterNotFound(Exception):
    pass


class BrokenMaster(Exception):
    pass
