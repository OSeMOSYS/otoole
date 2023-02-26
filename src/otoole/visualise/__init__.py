"""Visualise different aspects of an OSeMOSYS model and data

Provides the following commands::

    otoole viz res <input_data_format> <path_to_input_data> <path_to_res_image> <path_to_user_config>

``otoole viz res`` generates an image of the reference energy system

"""
from .res import create_res

__all__ = ["create_res"]
