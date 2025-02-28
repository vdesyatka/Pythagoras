import os
import pandas as pd

import string
from abc import *
from typing import Set
import boto3


import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
import jsonpickle.ext.pandas as jsonpickle_pandas
jsonpickle_numpy.register_handlers()
jsonpickle_pandas.register_handlers()

#
class SimpleDict(ABC):
    """Dict-like class that only accepts keys which are sequences of strings.

    An abstract class for a key-value store. It accepts keys in a form of
    either a single sting or a sequence (tuple, list, etc.) of strings.
    It imposes no restrictions on types of values in the key-value pairs.

    The API for the class resemples the API of Python's built-in Dict.
    """

    allowed_key_chars: Set = set(string.ascii_letters
                                 + string.digits + "()_-.=")

    def _normalize_key(self, key):
        """Check if a key meets requirements and return its standardized form.

        A key must be either a string or a sequence of non-empty strings.
        If it is a single string, it will be transformed into a tuple,
        consisting of this sole string.

        Each string in a sequence can contain only alphanumerical characters
        and characters from this list: ()_-.=
        """

        try:
            iter(key)
        except:
            raise KeyError(f"Key must be a string or a sequence of strings.")
        if isinstance(key, str):
            key = (key,)
        for s in key:
            assert isinstance(s,str), (
                    "Key must be a string or a sequence of strings.")
            assert len(set(s) - self.allowed_key_chars) == 0, (
                "Only the following chars are allowed in a key:"
                + str(self.allowed_key_chars))
            assert len(s), "Only non-empty strings are allowed in a key"
        return key

    @abstractmethod
    def __contains__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def _generic_iter(self, iter_type: str):
        assert iter_type in {"keys", "values", "items"}
        raise NotImplementedError

    def __iter__(self):
        return self._generic_iter("keys")

    def keys(self):
        return self._generic_iter("keys")

    def values(self):
        return self._generic_iter("values")

    def items(self):
        return self._generic_iter("items")

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def pop(self, key, default):
        if key in self:
            result = self[key]
            del self[key]
            return result
        else:
            return default

    def popitem(self):
        key = next(iter(self))
        result = self[key]
        del self[key]
        return result

    def __eq__(self, other):
        try:
            if len(self) != len(other):
                return False
            for k in other.keys():
                if self[k] != other[k]:
                    return False
            return True
        except:
            return False

    def __ne__(self, other):
        return not (self == other)

    def clear(self):
        for k in self.keys():
            del self[k]


class FileDirDict(SimpleDict):
    """ A persistent Dict that stores key-value pairs in local files.

    A new file is created for each key-value pair.
    A key is either a filename (without an extension),
    or a sequence of directory names that ends with a filename.
    A value can be any Python object, which is stored in a file.

    FileDirDict can store objects in binary files (as pickles)
    or in human-readable text files (using jsonpickles).
    """

    def __init__(self, dir_name: str = "FileDirDict", file_type: str = "pkl"):
        """A constructor defines location of the store and file format to use.

        dir_name is a directory that will contain all the files in
        the FileDirDict. If the directory does not exist, it will be created.

        file_type can take one of two values: "pkl" or "json".
        It defines which file format will be used by FileDirDict
        to store values.
        """

        self.file_type = file_type

        assert file_type in {"json", "pkl"}, (
            "file_type must be either pkl or json")
        assert not os.path.isfile(dir_name)
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        assert os.path.isdir(dir_name)

        self.base_dir = os.path.abspath(dir_name)

    def __len__(self):
        num_files = 0
        for subdir_info in os.walk(self.base_dir):
            files = subdir_info[2]
            files = [f_name for f_name in files
                     if f_name.endswith(self.file_type)]
            num_files += len(files)
        return num_files

    def clear(self):
        for subdir_info in os.walk(self.base_dir, topdown=False):
            (subdir_name, _, files) = subdir_info
            num_files = len(files)
            for f in files:
                if f.endswith(self.file_type):
                    os.remove(os.path.join(subdir_name, f))
            if (subdir_name != self.base_dir) and len(os.listdir(subdir_name)) == 0:
                os.rmdir(subdir_name)

    def _build_full_filename(self, key, create_subdirs=False):
        key = self._normalize_key(key)
        key = [self.base_dir] + list(key)
        dir_names = key[:-1]

        if create_subdirs:
            current_dir = key[0]
            for dir_name in key[1:-1]:
                new_dir = os.path.join(current_dir, dir_name)
                if not os.path.isdir(new_dir):
                    os.mkdir(new_dir)
                current_dir = new_dir

        file_name = key[-1] + "." + self.file_type
        return os.path.join(*dir_names, file_name)

    def _read_from_file(self, file_name: str):
        if self.file_type == "pkl":
            result = pd.read_pickle(file_name)
        elif self.file_type == "json":
            with open(file_name, 'r') as f:
                result = jsonpickle.loads(f.read())
        else:
            raise ValueError("file_type must be either pkl or json")
        return result

    def _save_to_file(self, file_name: str, value):
        if self.file_type == "pkl":
            pd.to_pickle(value, file_name)
        elif self.file_type == "json":
            with open(file_name, 'w') as f:
                f.write(jsonpickle.dumps(value, indent=4))
        else:
            raise ValueError("file_type must be either pkl or json")

    def __contains__(self, key):
        filename = self._build_full_filename(key)
        return os.path.isfile(filename)

    def __getitem__(self, key):
        filename = self._build_full_filename(key)
        if not os.path.isfile(filename):
            raise KeyError(f"File {filename} does not exist")
        result = self._read_from_file(filename)
        return result

    def __setitem__(self, key, value):
        filename = self._build_full_filename(key, create_subdirs=True)
        self._save_to_file(filename, value)

    def __delitem__(self, key):
        filename = self._build_full_filename(key)
        os.remove(filename)

    def _generic_iter(self, iter_type: str):
        assert iter_type in {"keys", "values", "items"}
        walk_results = os.walk(self.base_dir)
        ext_len = len(self.file_type) + 1

        def splitter(path: str):
            result = []
            if path == ".":
                return result
            while True:
                head, tail = os.path.split(path)
                result = [tail] + result
                path = head
                if len(head) == 0:
                    break
            return tuple(result)

        def step():
            for dir_name, _, files in walk_results:
                for f in files:
                    if f.endswith(self.file_type):
                        prefix_key = os.path.relpath(
                            dir_name, start=self.base_dir)

                        result_key = (*splitter(prefix_key), f[:-ext_len])

                        if iter_type == "keys":
                            yield result_key
                        elif iter_type == "values":
                            yield self[result_key]
                        else:
                            yield (result_key, self[result_key])

        return step()


class S3_Dict(SimpleDict):
    """ A persistent Dict that stores key-value pairs as S3 objects.

        A new object is created for each key-value pair.
        A key is either an objectname (a 'filename' without an extension),
        or a sequence of folder names (object name prefixes) that ends
        with an objectname. A value can be any Python object,
        which is stored in an object.

        S3_Dict can store objects in binary objects (as pickles)
        or in human-readable texts objects (using jsonpickles).
        """


    def __init__(self, bucket_name: str
                 , region:str = None
                 , dir_name: str = "S3_Dict"
                 , file_type: str = "pkl"):
        """A constructor defines location of the store and object format to use.

        bucket_name and region define an S3 location of the storage
        that will contain all the objects in the S3_Dict.
        If the bucket does not exist, it will be created.

        dir_name is a local directory that will be used to store tmp files.

        file_type can take one of two values: "pkl" or "json".
        It defines which object format will be used by S3_Dict
        to store values.
        """

        self.file_type = file_type
        self.local_cache = FileDirDict(dir_name = dir_name, file_type = file_type)

        if region is None:
            self.s3_client = boto3.client('s3')
        else:
            self.s3_client = boto3.client('s3', region_name=region)

        self.bucket = self.s3_client.create_bucket(Bucket=bucket_name)
        self.bucket_name = bucket_name

    def _build_full_objectname(self, key):
        key = self._normalize_key(key)
        objectname =  "/".join(key)+ "." + self.file_type
        return objectname

    def __contains__(self, key):
        try:
            obj_name = self._build_full_objectname(key)
            self.s3_client.head_object(Bucket=self.bucket_name, Key=obj_name)
            return True
        except:
            return False

    def __getitem__(self, key):
        obj_name = self._build_full_objectname(key)
        file_name = self.local_cache._build_full_filename(key, create_subdirs=True)
        self.s3_client.download_file(self.bucket_name, obj_name, file_name)
        result =  self.local_cache[key]
        del self.local_cache[key]
        return result

    def __setitem__(self, key, value):
        obj_name = self._build_full_objectname(key)
        file_name = self.local_cache._build_full_filename(key, create_subdirs=True)
        self.local_cache[key]=value
        self.s3_client.upload_file(file_name, self.bucket_name, obj_name)
        del self.local_cache[key]

    def __delitem__(self, key):
        obj_name = self._build_full_objectname(key)
        self.s3_client.delete_object(Bucket = self.bucket_name, Key = obj_name)

    def __len__(self):
        num_files = 0
        suffix = "." + self.file_type

        paginator = self.s3_client.get_paginator("list_objects")
        page_iterator = paginator.paginate(Bucket=self.bucket_name)

        for page in page_iterator:
            if "Contents" in page:
                for key in page["Contents"]:
                    obj_name = key["Key"]
                    if obj_name.endswith(suffix):
                        num_files += 1

        return num_files

    def _generic_iter(self, iter_type: str):
        assert iter_type in {"keys", "values", "items"}
        suffix = "." + self.file_type

        ext_len = len(self.file_type) + 1

        def splitter(full_name: str):
            result = full_name.split(sep="/")
            result[-1] = result[-1][:-ext_len]
            return tuple(result)

        def step():
            paginator = self.s3_client.get_paginator("list_objects")
            page_iterator = paginator.paginate(Bucket=self.bucket_name)
            for page in page_iterator:
                if "Contents" in page:
                    for key in page["Contents"]:
                        obj_name = key["Key"]
                        if not obj_name.endswith(suffix):
                            continue
                        obj_key = splitter(obj_name)
                        if iter_type == "keys":
                            yield obj_key
                        elif iter_type == "values":
                            yield self[obj_key]
                        else:
                            yield (obj_key, self[obj_key])

        return step()


class ImmutableS3_LocallyCached_Dict(S3_Dict):
    """ A persistent Dict that stores immutable key-value pairs as S3 objects, and caches them locally.

        A new object is created for each key-value pair.
        A key is either an objectname (a 'filename' without an extension),
        or a sequence of folder names (object name prefixes) that ends
        with an objectname. A value can be any Python object,
        which is stored in an object.

        Once the key-value pair is created, it can't be deleted or changed.

        The key-value pairs are stored in S3 backed, and also cached locally as files.

        ImmutableS3_LocallyCached_Dict can store objects in binary objects (as pickles)
        or in human-readable texts objects (using jsonpickles).
        """


    def __init__(self, bucket_name: str, region: str = None, dir_name: str = "S3_Dict", file_type: str = "pkl"):
        """A constructor defines location of the store, local cache, and object format to use.

        bucket_name and region define an S3 location of the storage
        that will contain all the objects in the S3_Dict.
        If the bucket does not exist, it will be created.

        dir_name is a local directory that will be used to store cached files.

        file_type can take one of two values: "pkl" or "json".
        It defines which object format will be used by S3_Dict
        to store values.
        """

        super().__init__(bucket_name, region, dir_name, file_type)
        self._enforce_immutability = True
        """ _enforce_immutability only exists for testing purposes, its value should never be changed"""

    def __contains__(self, key):
        return self.local_cache.__contains__(key) or super().__contains__(key)

    def __getitem__(self, key):
        obj_name = self._build_full_objectname(key)
        file_name = self.local_cache._build_full_filename(key, create_subdirs=True)
        try:
            if not os.path.isfile(file_name):
                self.s3_client.download_file(self.bucket_name, obj_name, file_name)
        except:
            raise KeyError(f"Object {file_name} does not exist or could not be accessed")
        result =  self.local_cache[key]
        return result

    def __setitem__(self, key, value):
        if self._enforce_immutability and self.__contains__(key):
            raise KeyError(f"Key {key} is already present in ImmutableS3_LocallyCached_Dict, value can't be changed.")
        obj_name = self._build_full_objectname(key)
        file_name = self.local_cache._build_full_filename(key, create_subdirs=True)
        self.local_cache[key]=value
        self.s3_client.upload_file(file_name, self.bucket_name, obj_name)

    def __delitem__(self, key):
        if self._enforce_immutability:
            raise KeyError(f"Can't delete {key}: operation is not allowed for immitable Dict.")
        else:
            super().__delitem__(key)
            if key in self.local_cache:
                del self.local_cache[key]