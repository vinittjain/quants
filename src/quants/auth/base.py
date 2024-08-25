from abc import ABC, abstractmethod


class BaseAuth(ABC):
    @abstractmethod
    def get_client(self) -> dict:
        """
        Get the headers required for authentication.

        :return: A dictionary of headers
        """
        pass

    @abstractmethod
    def get_spot(self) -> dict:
        """
        Get the spot for the authentication."""
        pass
