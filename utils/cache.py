from typing import Callable

import streamlit as st


def cache_data(func: Callable, cache_name: str) -> Callable:
    """
    Cache the output of a function using Streamlit's cache.

    Args:
        func (Callable): The function to cache.
        cache_name (str): Name for the cached item, must be unique for each
            cache declaration. (use `f"{func.__name__}_{param_name1}_{param_name2}"`)

    Returns:
        Callable: The decorated function with caching.
    """

    def wrapper(*args, **kwargs):
        # Check if the function output exists in the cache
        if cache_name in st.session_state:
            return st.session_state[cache_name]

        # If not, compute the function output and save it in the cache
        result = func(*args, **kwargs)
        st.session_state[cache_name] = result
        return result

    return wrapper
