"""Class definition for ChatGPTClient"""

import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as Exceptions

from .. import BaseBrowser


class ChatGPTClient(BaseBrowser):
    """ChatGPTClient class to interact with ChatGPT"""

    def __init__(self, **kwargs):
        super().__init__(client_name="ChatGPT", url="https://chatgpt.com", **kwargs)

    def postload_custom_func(self):
        today_str = datetime.today().strftime("%Y-%m-%d")
        self.browser.execute_script(
            f"window.localStorage.setItem('oai/apps/hasSeenOnboarding/chat', {today_str});"
            "window.localStorage.setItem('oai/apps/hasUserContextFirstTime/2023-06-29', true);"
            "window.localStorage.setItem('oai/apps/announcement/customInstructions', 1694012515508);"
        )

    def pass_verification(self, max_trial: int = 10, wait_time: int = 1) -> bool:
        """
        Performs the verification process on the page if challenge is present.

        This function checks if the login page is displayed in the browser.
        In that case, it looks for the verification button.
        This process is repeated until the login page is no longer displayed.

        Returns: None
        """
        for _ in range(max_trial):
            verify_button = self.browser.find_elements(By.ID, "challenge-stage")
            if not verify_button:
                break
            try:
                verify_button[0].click()
                self.logger.info("Clicked verification button")
            except Exceptions.ElementNotInteractableException:
                self.logger.info("Verification button is not present or clickable")
            time.sleep(wait_time)
        else:
            self.logger.error("It is not possible to pass verification")
            return False

        return True

    def login(self, username: str, password: str, sso : bool) -> bool:
        """
        Performs the login process with the provided username and password.

        This function operates on the login page.
        It finds and clicks the login button,
        fills in the email and password textboxes

        Args:
            username (str): The username to be entered.
            password (str): The password to be entered.

        Returns:
            None
        """

        # Find login button, click it

        login_button = self.wait_until_appear(By.XPATH, self.markers.login_xq)
        self.wait_object.until(EC.element_to_be_clickable(login_button))
        login_button.click()

        # login_button = self.find_or_fail(By.XPATH, self.markers.login_xq, fail_ok=True)
        # login_button.click()
        self.logger.info("Clicked login button for the first time.")

        if sso:
            self.logger.info("SSO login is selected")
            sso_button = self.wait_until_appear(By.XPATH, '//button[@class="social-btn"][span/img[@alt="Google logo"]]').click()
            self.logger.info("Clicked SSO login button")
            sso_gmail = self.wait_until_appear(By.XPATH, '//input[@type="email"]')
            sso_gmail.send_keys('anandeshsharma@gmail.com')
            time.sleep(10)
            self.browser.find_element(By.XPATH, '//button[span[text()="Next"]]').click()
            sso_pass = self.wait_until_appear(By.XPATH, '//input[@type="password"]')
            sso_pass.send_keys('Rock4494@')
            self.browser.find_element(By.XPATH, '//button[span[text()="Next"]]').click()

            time.sleep(5)
            
            
            return True

        for _ in range(5):
            email_box = self.wait_until_appear(
                By.XPATH, self.markers.email_xq, 5, fail_ok=True
            )
            if email_box:
                self.logger.info("Username area has found")
                break
            login_button = self.find_or_fail(
                By.XPATH, self.markers.login_xq, fail_ok=True
            )
            if login_button:
                login_button.click()
                self.logger.info("Trying to click login button once more")
        else:
            self.logger.error("Can't reach email page")
            return False

        email_box.send_keys(username)
        self.logger.info("Filled email box")

        # Click continue
        continue_button = self.wait_until_appear(By.XPATH, self.markers.continue_xq)
        continue_button.click()
        self.logger.info("Clicked continue button")

        # Find password textbox, enter password
        pass_box = self.wait_until_appear(By.ID, self.markers.pwd_iq)
        pass_box.send_keys(password)
        self.logger.info("Filled password box")
        # Click continue
        
        continue_button = self.wait_until_appear(By.XPATH, self.markers.continue_xq)
        continue_button.click()
        self.logger.info("Clicked continue in password page")

        try:
            # Pass introduction
            WebDriverWait(self.browser, 2).until(
                EC.presence_of_element_located((By.XPATH, self.markers.tutorial_xq))
            ).click()

            self.logger.info("Info screen passed")
        except Exceptions.TimeoutException:
            self.logger.info("Info screen skipped")
        except Exception as err:
            self.logger.error("Something unexpected happened: %s", err)
            return False

        text_area = self.wait_until_appear(By.TAG_NAME, self.markers.textarea_tq)

        if text_area is not None:
            self.logger.info("Login is not successful.")
            return True

        self.logger.error("Login is not successful.")
        return False

    def get_last_response(
        self, num_step: int = 200, period: float = 0.5, same_answer_limit=3
    ) -> str:
        """
        Continuously checks for a response in a chatbox-like element and
            returns the last received response.

        Args:
            num_step (int): Number of cycles to check for updates to the response.
                Defaults to 200.
            period (float): Sleep time between each step, representing the delay between each check.
                Defaults to 0.5 seconds.
            same_answer_limit (int): The maximum number of times the same response can
                be observed before concluding that the response is complete. Defaults to 3.

        Returns:
            str: The last valid response from the chatbox element.
                If no response is found, an empty string is returned.

        Behavior:
            - The function first waits for the chatbox element to appear on the page.
            - It continuously checks for updates to the response in the chatbox.
            - The response is checked continuously, `period` seconds between each check.
            - If the response remains the same for more than `same_answer_limit` consecutive times,
                the loop breaks, assuming the response is complete.
            - If no response is found, it returns an empty string.
            - If a response is found, it returns the last detected response.
        """

        self.logger.info("Checking the response")

        self.interim_response = None
        self.wait_until_appear(By.XPATH, self.markers.chatbox_xq)
        counter = 0
        for _ in range(num_step):
            time.sleep(period)
            l_response = self.find_or_fail(
                By.XPATH, self.markers.chatbox_xq, return_type="last"
            ).text
            if l_response and l_response == self.interim_response:
                counter += 1
            if counter > same_answer_limit:
                break
            self.interim_response = l_response

        if not self.interim_response:
            self.logger.error("There is no response, something is wrong")
            return ""

        self.logger.info("response is ready")
        return self.interim_response

    def interact(self, prompt: str) -> str:
        """Sends a prompt and retrieves the response from the ChatGPT system.

        This function interacts with the ChatGPT.
        It takes the prompt as input and sends it to the system.
        The prompt may contain multiple lines separated by '\\n'.
        In this case, the function simulates pressing SHIFT+ENTER for each line.
        Upon arrival of the interaction, the function waits for the response.
        Once the response is ready, the function will return the response.

        Args:
            prompt (str): The interaction text.

        Returns:
            str: The generated response.
        """

        text_area = self.wait_until_appear(By.XPATH, self.markers.textarea_xq)
        if not text_area:
            raise RuntimeError(
                "Unable to find the text prompt area. Please raise an issue with verbose=True"
            )
        for each_line in prompt.split("\n"):
            text_area.send_keys(each_line)
            text_area.send_keys(Keys.SHIFT + Keys.ENTER)
        text_area.send_keys(Keys.RETURN)

        response = self.get_last_response()

        self.log_chat(prompt=prompt, response=response)
        return response

    def reset_thread(self) -> bool:
        """Function to close the current thread and start new one"""
        self.browser.get(self.url)
        text_area = self.wait_until_appear(By.TAG_NAME, self.markers.textarea_tq)
        if text_area:
            return True
        self.logger.error(
            "Couldn't reset the conversation. Please raise an issue with verbose=True"
        )
        return False

    def regenerate_response(self) -> str:
        """
        Clicks the regenerate button to generate a new response
            and returns the new response.

        Args:
            None

        Returns:
            str: The newly generated response text. If the regeneration fails, returns an empty string.
        """
        regen_button = self.find_or_fail(
            By.XPATH, self.markers.regen_1_xq, return_type="first"
        )
        if not regen_button:
            return ""
        regen_button.click()
        self.logger.info("Clicked regenerate button")

        try_again_button = self.find_or_fail(
            By.XPATH, self.markers.regen_2_xq, return_type="last"
        )
        if not try_again_button:
            return ""
        try_again_button.click()
        self.logger.info("Clicked Try again button")

        response = self.get_last_response()
        if not response:
            self.logger.error("Regeneration failed")
            return ""

        self.log_chat(response=response, regenerated=True)
        return response

    def switch_model(self, model_name: str) -> bool:
        """
        Switch the model for ChatGPT+ users.

        Args:
            model_name: str = The name of the model, either GPT-3.5 or GPT-4

        Returns:
            bool: True on success, False on fail
        """
        if model_name in ["GPT-3.5", "GPT-4"]:
            self.logger.info("Switching model to %s", model_name)
            try:
                self.browser.find_element(
                    By.XPATH, self.markers.gpt_xq.format(model_name)
                ).click()
                return True
            except Exceptions.NoSuchElementException:
                self.logger.error("Button is not present")
        else:
            self.logger.error("Model name is not ")
        return False

    def open_custom_instruction_tab(self) -> bool:
        """Opens the modal to access custom interactions.

        Returns:
            bool: True if the process is successful, False otherwise
        """

        menu_button = self.find_or_fail(By.XPATH, self.markers.menu_xq)
        menu_button.click()
        custom_button = self.find_or_fail(By.XPATH, self.markers.custom_xq)
        custom_button.click()
        custom_tutorial = self.find_or_fail(
            By.XPATH, self.markers.cust_tut_xq, fail_ok=True
        )
        if custom_tutorial:
            custom_tutorial.click()

        custom_switch = self.find_or_fail(By.XPATH, self.markers.cust_toggle_xq)
        if not custom_switch:
            return False

        # If disabled, enable custom interactions
        if custom_switch.get_attribute("data-state") == "checked":
            self.logger.info("Custom instructions is enabled")
        else:
            custom_switch.click()
        time.sleep(0.2)

        return True

    def get_custom_instruction(self, mode: str) -> str:
        """Gets custom instructions

        Args:
            mode (str): Either 'extra_information' or 'modulation'. Check OpenAI help pages.
        """
        if mode not in ["extra_information", "modulation"]:
            self.logger.error(
                "Given mode is unrecognized. Either provide extra_information or modulation"
            )
            return ""
        if not self.open_custom_instruction_tab():
            return ""
        text_areas = self.find_or_fail(
            By.XPATH, self.markers.cust_txt_xq, return_type="all"
        )
        text = text_areas[{"extra_information": 0, "modulation": 1}[mode]].text
        self.logger.info("Custom instruction is obtained: %s", text)

        save_button = self.find_or_fail(By.XPATH, self.markers.cust_cancel_xq)
        save_button.click()
        return text

    def set_custom_instruction(self, mode: str, instruction: str):
        """Sets custom instructions

        Args:
            mode (str): Either 'extra_information' or 'modulation'. Check OpenAI help pages.
            instruction (str): _description_
        """
        if not self.open_custom_instruction_tab():
            return False

        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, self.markers.cust_txt_xq))
        )
        text_areas = self.find_or_fail(
            By.XPATH, self.markers.cust_txt_xq, return_type="all"
        )
        text_area = text_areas[{"extra_information": 0, "modulation": 1}[mode]]

        text_area.send_keys(Keys.CONTROL + "a")
        time.sleep(0.1)
        text_area.send_keys(Keys.DELETE)
        time.sleep(0.1)
        text_area.send_keys(instruction)
        time.sleep(0.1)
        text_area.send_keys(" ")
        self.logger.info("Custom instruction-%s has provided", mode)

        save_button = self.find_or_fail(By.XPATH, self.markers.cust_save_xq)
        save_button.click()
        return True
