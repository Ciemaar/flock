from abc import ABCMeta, abstractmethod
from typing import Any, Iterable


class CCBase(metaclass=ABCMeta):
    @abstractmethod
    def check(self, path):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.
        """
        pass

    @abstractmethod
    def shear(self, record_errors=False) -> Any:
        """
        Convert this Mapping into a simple dict

        :param record_errors: if True any exception raised will be stored in place of the result that caused it rather
        than continuing up the call stack

        :return: a dict() representation of this Aggregator
        """
        pass

    @abstractmethod
    def __call__(self):
        """
        Call must be specified so that FlockMappings can be nested within eachother

        :return: self
        """
        pass

    def clear_cache(self):
        pass

    def get_relatives(self) -> Iterable:
        return ()
