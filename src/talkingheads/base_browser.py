"""
This module provides a base class `BaseBrowser` for automating web interactions using the 
`undetected_chromedriver` package and Selenium WebDriver.

The `BaseBrowser` class establishes core for different chatbot interfaces, providing common 
features such as headless mode, incognito browsing, login functionality, and interaction with 
web elements. It also includes utility functions for handling timeouts, saving chat history, 
and performing custom pre- and post-load actions on webpages.

Key Features:
    - Browser automation using undetected_chromedriver and Selenium.
    - Configurable headless, incognito modes, and driver arguments.
    - Timeout management for page load and element interactions.
    - Automatic login and credential management using environment variables.
    - Logging and verbose mode for detailed tracking of actions.
    - Functions to find, wait for, and interact with web elements.
    - Chat history saving and automatic response logging.

The module also includes abstract methods (`login`, `interact`, `reset_thread`, etc.) 
that should be implemented by subclasses for specific automation workflows, like interacting 
with a chatbot or performing other automated web tasks.
"""

import abc
import os
import logging
import time
from datetime import datetime
from typing import Union, Dict, List

import undetected_chromedriver as uc
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import selenium.common.exceptions as Exceptions

from .object_map import markers
from .utils import detect_chrome_version, save_func_map


class BaseBrowser:
    """
    A base class for browser automation that includes login, interaction, and session management
    for various clients. This class provides essential browser functionality like loading web pages,
    managing timeouts, saving chat logs, and handling login processes, which can be customized
    for different clients.

    Args:
        client_name (str): Name of the client.
        url (str): URL to be used as the starting point of the session.
        uname_var (str): Environment variable name for the username.
        pwd_var (str): Environment variable name for the password.
        username (str, optional): Username (deprecated, environment variables recommended).
        password (str, optional): Password (deprecated, environment variables recommended).
        headless (bool, optional): Enables/disables headless mode. Default: True.
        cold_start (bool, optional): If True, load the page and return. Default: False.
        incognito (bool, optional): Enables incognito mode if True. Default: True.
        driver_arguments (list, optional): Additional arguments for the browser driver.
        driver_version (int, optional): Version of the ChromeDriver to use.
        auto_save (bool, optional): A boolean to enable/disable automatic saving. Default: False.
        save_path (str, optional): Path to save chat logs.
        verbose (bool, optional): A boolean to enable/disable logging. Default: False.
        credential_check (bool, optional): Enables/disables credential check. Default: True.
        skip_login (bool, optional): If True, skips the login procedure. Default: False.
        user_data_dir (str, optional): The directory path to user profile.
        uc_params (dict, optional): Additional parameters for undetected Chrome (uc.Chrome).
            Some examples : driver_executable_path, browser_executable_path

    Attributes:
        client_name (str): Client name provided during initialization.
        browser (uc.Chrome): The undetected Chrome browser instance.
        markers (dict): Markers used for locating elements on the page.
        logger (logging.Logger): Logger for the browser class.
        ready (bool): Whether the browser is fully initialized and ready.
        timeout_dur (int): Page load and element wait timeout duration.
        chat_history (pd.DataFrame): DataFrame that holds chat history.
    """

    def __init__(
        self,
        client_name: str,
        url: str,
        uname_var: Union[str, None] = None,
        pwd_var: Union[str, None] = None,
        username: Union[str, None] = None,
        password: Union[str, None] = None,
        headless: bool = True,
        cold_start: bool = False,
        incognito: bool = True,
        driver_arguments: Union[List, Dict] = None,
        driver_version: int = None,
        timeout_dur: int = 90,
        auto_save: bool = False,
        save_path: str = None,
        verbose: bool = False,
        credential_check: bool = True,
        skip_login: bool = False,
        user_data_dir: str = None,
        uc_params: dict = None,
        tag: str = None,
        multihead=False,
        sso: bool = False,
    ):
        self.client_name = client_name
        self.markers = markers[client_name]
        self.url = url
        self.uname_var = uname_var or f"{client_name}_UNAME"
        self.pwd_var = pwd_var or f"{client_name}_PWD"
        self.headless = headless
        self.ready = False
        self.browser = None
        self.auto_save = auto_save
        self.last_prompt = ""
        self.tag = tag or self.client_name
        self.timeout_dur = timeout_dur
        self.multihead = multihead
        self.interim_response = None
        self.sso = sso

        if credential_check:
            if username or password:
                logging.warning(
                    "The username and password parameters are deprecated and will be removed soon."
                    " Please adjust your environment variables to pass username and password."
                )

            username = username or os.environ.get(self.uname_var)
            password = password or os.environ.get(self.pwd_var)

            if not username:
                raise NameError(
                    f"Either provide username or set the environment variable {self.uname_var}"
                )

            if not password:
                raise NameError(
                    f"Either provide password or set the environment variable {self.pwd_var}"
                )

        # Create a new of the logger
        r_level = logging.getLogger().getEffectiveLevel()

        self.logger = logging.getLogger(self.tag)
        self.logger.setLevel(r_level)
        # If verbose is provided and the current log level is higher
        # than info, it will decrease logging level.
        if verbose and not self.logger.isEnabledFor(logging.INFO):
            self.logger.setLevel(logging.INFO)
            self.logger.info("Verbose mode active")
        options = uc.ChromeOptions()
        options.headless = self.headless
        if incognito:
            options.add_argument("--incognito")

        # chrome_prefs = {
        #     "profile.default_content_settings" : {"images": 2},
        #     "profile.managed_default_content_settings" : {"images": 2}
        # }

        # options.experimental_options["prefs"] = chrome_prefs

        if driver_arguments:
            if isinstance(driver_arguments, dict):
                driver_arguments = list(
                    map(
                        lambda kv: f"--{kv[0]}"
                        + ("" if kv[1] is True else f"={kv[1]}"),
                        driver_arguments.items(),
                    )
                )

            _ = list(map(options.add_argument, driver_arguments))

        self.logger.info("Loading undetected Chrome")
        uc_params = uc_params or {}
        self.browser = uc.Chrome(
            user_data_dir=user_data_dir,
            options=options,
            headless=headless,
            version_main=detect_chrome_version(driver_version),
            **uc_params,
        )
        # self.browser.set_page_load_timeout(timeout_dur)
        self.wait_object = WebDriverWait(self.browser, timeout_dur)

        agent = self.browser.execute_script("return navigator.userAgent")
        self.browser.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": agent.replace("Headless", "")}
        )

        self.logger.info("Loaded undetected Chrome")
        self.logger.info("Opening %s", self.client_name)

        self.preload_custom_func()
        self.browser.get(self.url)
        if cold_start:
            return

        self.postload_custom_func()
        if not self.pass_verification():
            raise RuntimeError("Verification failed, please check your connection.")

        if not skip_login:
            self.login(username, password, self.sso)

        self.logger.info("%s is ready to interact", self.client_name)
        self.ready = True
        self.chat_history = pd.DataFrame(columns=["role", "is_regen", "content"])
        self.set_save_path(save_path)

    def __del__(self):
        if self.browser is not None:
            self.browser.close()
            self.browser.quit()

        if self.auto_save:
            self.save()

    def set_timeout_dur(self, timeout_dur: int):
        """
        Sets the duration for page load and element wait timeout.

        Args:
            timeout_dur (int): The timeout duration in seconds.
        """

        self.browser.set_page_load_timeout(timeout_dur)
        self.wait_object = WebDriverWait(self.browser, timeout_dur)

    def set_save_path(self, save_path: str):
        """
        The file path to save the chat log. If not provided, a timestamped file
        with the default extension 'csv' is created in the current working directory.

        Args:
            save_path (str): The saving path
        """
        self.save_path = save_path or datetime.now().strftime(
            f"{self.tag}_%Y_%m_%d_%H_%M_%S.csv"
        )
        self.file_type = save_path.split(".")[-1] if save_path else "csv"

    def save(self) -> bool:
        """
        Saves the chat history to a file using the provided save path and file format.

        Returns:
            bool: True if the file was successfully saved, False otherwise.
        """
        save_func = save_func_map.get(self.file_type, None)
        if save_func:
            save_func = getattr(self.chat_history, save_func)
            save_func(self.save_path)
            self.logger.info("File saved to %s", self.save_path)
            return True

        self.logger.error("Unsupported file type %s", self.file_type)
        return False

    def find_or_fail(
        self,
        by: By,
        elem_query: str,
        return_type: str = "first",
        return_shadow: bool = False,
        fail_ok: bool = False,
        dom_element: WebElement = None,
    ) -> Union[WebElement, None]:
        """
        Finds elements based on the provided query and locator method.
        Raises an error if no element is found and fail_ok is False.

        Args:
            by (By): The method used to locate the element (e.g., By.ID, By.XPATH).
            elem_query (str): The query string for locating the element.
            return_type (str): Defines which element to return ('first', 'all', or 'last'). Default is 'first'.
            return_shadow (bool, optional): If True, returns the shadow root of the element. Default is False.
            fail_ok (bool): o not produce error if it is ok to fail.
            dom_element (WebElement): If set, finds within that element.
        Returns:
            WebElement: The found web element or None if not found.
        """

        if return_type not in {"first", "last", "all"}:
            return ValueError("Unrecognized return type")

        if dom_element is None:
            dom_element = self.browser.find_elements(by, elem_query)
        else:
            dom_element = dom_element.find_elements(by, elem_query)

        if not dom_element:
            if not fail_ok:
                self.logger.error(
                    " %s is not located. Please raise an issue with verbose=True",
                    elem_query,
                )
            else:
                self.logger.info(" %s is not located.", elem_query)
            return None

        self.logger.info(" %s is located.", elem_query)

        element = {
            "first": lambda x: x[0],
            "all": lambda x: x,
            "last": lambda x: x[-1],
        }[return_type](dom_element)

        if return_shadow and return_type == "all":
            self.logger.warning(
                "Returning shadow root of a list of elements is not implemented."
            )
        elif return_shadow:
            element = element.shadow_root

        return element

    def is_login_page(self):
        """
        Checks whether the login page is currently displayed.

        Returns:
            bool: True if the login button is not present, False otherwise.
        """
        login_button = self.browser.find_elements(By.XPATH, self.markers.login_xq)
        return len(login_button) == 1

    def wait_until_appear(
        self, by: By, elem_query: str, timeout_dur: int = None, fail_ok=False
    ) -> Union[WebElement, None]:
        """
        Waits until the specified web element appears on the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is present on the page.
        Once the element has appeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            elem_query (str): The elem_query string to locate the element.
            timeout_dur (int, optional): Waiting time before the timeout. Default: 15.
            fail_ok (bool, optional): If True, does not log an error when the element does not appear.

        Returns:
            WebElement | None: The web element if found, otherwise None.
        """
        self.logger.info("Waiting element %s to appear.", elem_query)
        element = None
        try:
            element = WebDriverWait(
                self.browser, timeout_dur or self.timeout_dur
            ).until(EC.presence_of_element_located((by, elem_query)))
            self.logger.info("Element %s appeared.", elem_query)
        except Exceptions.TimeoutException:
            if not fail_ok:
                self.logger.error(
                    "Element %s is not present, something is wrong.", elem_query
                )
        return element

    def wait_until_disappear(self, by: By, elem_query: str) -> bool:
        """
        Waits until the specified web element disappears from the page.

        This function continuously checks for the presence of a web element.
        It waits until the element is no longer present on the page.
        Once the element has disappeared, the function returns.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            elem_query (str): The elem_query string to locate the element.
            timeout_dur (int, optional): Waiting time before the timeout. Default: 15.

        Returns:
            (bool) : True if element disappears, false otherwise.
        """
        if self.multihead:
            return self._multihead_wait(by, elem_query)

        self.logger.info("Waiting element %s to disappear.", elem_query)
        try:
            self.wait_object.until(EC.invisibility_of_element_located((by, elem_query)))
            self.logger.info("Element %s disappeared.", elem_query)
            return True
        except Exceptions.TimeoutException:
            self.logger.info("Element %s still here, something is wrong.", elem_query)
            return False

    def _multihead_wait(self, by: By, elem_query: str, pool_time: float = 0.5) -> bool:
        """
        This is a temporary function to wait until the element disappears.

        A bug causes WebDriverWait to fail in conditions and this function mitigates the
        problem while a permanent solution is found.

        Args:
            by (selenium.webdriver.common.by.By): The method used to locate the element.
            elem_query (str): The elem_query string to locate the element.
            timeout_dur (int, optional): Waiting time before the timeout. Default: 15.

        Returns:
            (bool) : True if element disappears, false otherwise.
        """
        self.logger.info("Waiting element %s to disappear.", elem_query)

        for _ in range(int(self.timeout_dur / pool_time)):
            item = self.find_or_fail(by, elem_query, fail_ok=True)
            if not item:
                self.logger.debug("The item %s %s is not located", by, elem_query)
                return True
            logging.debug("The item is still present, waiting")
            time.sleep(pool_time)
        logging.error("Item is still present")
        return False

    def log_chat(
        self, prompt: str = None, response: str = None, regenerated: bool = False
    ) -> bool:
        """
        Log a chat interaction in the chat history.

        Args:
            prompt (str): The user's prompt to be logged.
            response (str): The response to the user's prompt to be logged.

        Returns:
            bool: True if the interaction is logged, False otherwise.
        """
        if not self.auto_save:
            return False

        if prompt:
            self.chat_history.loc[len(self.chat_history)] = [
                "user",
                regenerated,
                prompt,
            ]

        if response:
            self.chat_history.loc[len(self.chat_history)] = [
                self.client_name,
                regenerated,
                response,
            ]
        return True

    def preload_custom_func(self) -> None:
        """
        A function to implement custom instructions before loading the webpage
        """
        self.logger.debug("No custom preload function is implemented")

    def postload_custom_func(self) -> None:
        """
        A function to implement custom instructions after loading the webpage
        """
        self.logger.debug("No custom postload function is implemented")

    def pass_verification(self) -> bool:
        """
        Performs the verification process on the page if challenge is present.
        Returns:
            None
        """
        self.logger.info("The pass verification function is not implemented")
        return True

    def sso_login(self, username: str, password: str) -> bool:
        """
        Logs in using the SSO login process.
        """
        self.logger.info("The SSO login function is not implemented")
        return True

    @abc.abstractmethod
    def login(self, username: str, password: str, sso: bool = False) -> bool:
        """
        Performs the login process with the provided username and password.
        """
        self.logger.warning(
            "If you are creating a custom automation, please implement this method!"
        )

    @abc.abstractmethod
    def interact(self, prompt: str) -> str:
        """
        Abstract function to interact with the language model.
        """
        self.logger.warning(
            "If you are creating a custom automation, please implement this method!"
        )

    @abc.abstractmethod
    def reset_thread(self) -> bool:
        """
        Abstract function to open a new thread.
        """
        self.logger.warning(
            "Resetting thread is either not implemented or not available"
        )

    @abc.abstractmethod
    def regenerate_response(self) -> str:
        """
        Abstract function to regenerate the responses.
        """
        self.logger.warning(
            "Regenerating response is either not implemented or not available"
        )

    @abc.abstractmethod
    def switch_model(self, model_name: str) -> bool:
        """
        Abstract function to switch the model.

        Args:
            model_name: (str) = The name of the model.
        """
        self.logger.warning(
            "Switching model is either not implemented or not available"
        )
