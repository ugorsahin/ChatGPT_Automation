"""Storage of the xpath, class and id identifiers"""

from easydict import EasyDict

markers = EasyDict(
    {
        "ChatGPT": {
            "login_xq"      : "//button[@data-testid='login-button']",
            "email_xq"     : "//input[contains(@class, 'email-input') or @id='username']",
            "pwd_iq"        : "password",
            "continue_xq"   : "//button[text()='Continue']",
            "tutorial_xq"   : "//div[contains(text(), 'Okay, let’s go')]",
            "button_tq"     : "button",
            "done_xq"       : "//button[//div[text()='Done']]",
            "menu_xq"       : "//button[@data-testid='profile-button']",
            "custom_xq"     : "//div[contains(text(), 'Custom')]",
            "cust_toggle_xq": "//button[@role='switch']",
            "cust_txt_xq"   : "//textarea[@type='button']",
            "cust_save_xq"  : "//div[contains(text(), 'Save')]",
            "cust_cancel_xq": "//div[contains(text(), 'Cancel')]",
            "cust_tut_xq"   : "//div[text()='OK']",
            "chatbox_xq"    : "//div[@data-message-author-role='assistant']",
            "wait_xq"       : "//button[contains(@data-testid, 'stop-button')]",
            "reset_xq"      : "//a[//span[text()='New chat']]",
            "reset_cq"      : "truncate",
            "regen_1_xq"      : "//button[div/span[contains(text(), '4o')]]",
            "regen_2_xq"      : "//div[@role='menuitem']",
            "textarea_tq"   : "textarea",
            "send_btn_xq"   : "//button[@data-testid='send-button']",
            "textarea_xq"   : "//div[@contenteditable='true']",
            "file_input_xq" : "//input[@type='file']",
            "prompt_wait_xq": "//span[@data-state='closed']/button[@aria-label='Send prompt']",
            "gpt_xq"        : "//span[text()='{}']"
        },
        "Claude": {
            "file_types"    : [
                "pdf", "doc", "docx", "rtf", "epub", "odt", "odp", "pptx",
                "txt", "py", "ipynb", "js", "jsx", "html", "css", "java",
                "cs", "php", "c", "cpp", "cxx", "h", "hpp", "rs", "R",
                "Rmd", "swift", "go", "rb", "kt", "kts", "ts", "tsx",
                "m", "scala", "rs", "dart", "lua", "pl", "pm", "t",
                "sh", "bash", "zsh", "csv", "log", "ini", "config",
                "json", "yaml", "yml", "toml", "lua", "sql", "bat",
                "md", "coffee", "tex", "latex", "jpg", "jpeg",
                "png", "gif", "webp"
            ],
            "start_btn_xq"  : '//div[text()="Start Chat"]',
            "textarea_cq"   : "ProseMirror",
            "send_button_xq": '//button[@aria-label="Send Message"]',
            "chatarea_xq"   : '//div[contains(@class, "grid-cols-1")]/div[@class="contents"]',
            "regen_xq"      : "//button[text()='Retry']",
        },
        "Copilot": {
            "file_types"    : ["gif", "jpg", "jpeg", "png", "webp"],
            "textarea_xq"   : "//textarea[@id='userInput']",
            "answer_xq"     : "//div[@data-content='ai-message']/div",
            "img_upload_xq" : "//input[@type='file']",
            "thumbnail_xq"  : "//img[@aria-label='Uploaded image']",
            "dismiss_xq"    : "//button[@aria-label='Remove image']",
            "home_xq"       : "//button[@data-testid='home-button']",
            "history_xq"    : "//button[@aria-label='View history']",
            "new_chat_xq"   : "//button[@aria-label='Start new chat']",
            "submit_xq"     : "//button[contains(@class, 'rounded-submitButton')]",
            "location_xq"   : "//button[@title='Maybe later']"
        },
        "Gemini": {
            "file_types"    : ["jpg", "jpeg", "png", "webp"],
            "textarea_xq"   : '//div[@role="textbox"]',
            "wait_xq"       : '//rect',
            "chatbox_tq"    : "message-content",
            "new_chat_xq"   : '//expandable-button[contains(@aria-label, "New chat")]',
            "hist_off_xq"   : '//button[@data-test-id="bard-activity-disabled-button"]',
            "chat_conf_xq"  : '//button[@data-test-id="confirm-button"]',
            "regen_1_xq"    : "//span[@class='generate-drafts-button']",
            "regen_2_cq"    : "regenerate-button",
            "modify_xq"     : "//button[@aria-label='Modify response']",
            "mod_opt_xq"    : "//button[@role='menuitem'][not(contains(@style, 'none'))]",
            "img_upload_xq" : "//input[@name='Filedata']",
            "img_btn_xq"    : "//mat-icon[@data-mat-icon-name='add_photo_alternate']",
            "img_loaded_xq" : "//img[@aria-label='Image preview']",
            "got_it_xq"     : "//button[@data-test-id='got-it-button']"
        },
        "LeChat" : {
            "username_xq"   : "//div[@data-testid='node/input/identifier']//input",
            "password_xq"   : "//div[@data-testid='node/input/password']//input",
            "textarea_xq"   : "//div/textarea",
            "stop_gen_xq"   : "//button[@aria-label='Stop generation']",
            "chatbox_xq"    : "//*[contains(@class,'prose')]",
            "regen_xq"      : "//button[@aria-label='Rewrite']",
            "model_xq"      : "//button/span[@class='truncate']",
            "model_op_xq"   : "//div[contains(@class, 'w-full')]/div[contains(@class, 'text-sm')]"
        },
        "HuggingChat": {
            "login_xq"      : "//form[@action='/chat/login']",
            "username_xq"   : "//input[@name='username']",
            "password_xq"   : "//input[@name='password']",
            "a_login_xq"    : "//button[contains(text(), 'Login')]",
            "textarea_xq"   : "//textarea",
            "stop_gen_xq"   : "//button[contains(text(),'Stop generating')]",
            "chatbox_xq"    : "//div[@role='presentation']",
            "search_xq"     : "//div[@aria-label='web search toggle']",
            "model_xq"      : "//div[div/div/text()='Current Model']//a",
            "settings_xq"   : "//h2[text()='Settings']",
            "model_li_xq"   : "//div/a/div[@class='mr-auto truncate']",
            "model_a_xq"    : "//div[h2/text()='Settings']//button",
            "model_act_xq"  : "//button[@name='Activate model']"
        },
        "Pi": {
            "textarea_xq"   : "//textarea[@role='textbox']",
            "sendkeys_xq"   : "//button[@aria-label='Submit text']",
            "wait_xq"       : "//button[@disabled]",
            "chatbox_xq"    : "//div[@class='flex items-center']",
            "model_1_xq"    : "//div[contains(@class, 'shadow-input')]//button",
            "model_2_xq"    : "//button[contains(@class, 't-body-s')]",
            "model_v_xq"    : "//div[contains(text(), 'Switched to')]"
        }
    }
)
