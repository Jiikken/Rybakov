class CommandsPosts:
    def __init__(self):
        self.commands_for_posts_in_chat = {
            "#одобрено": {
                "handler": self.approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg"]
            },
            "#oдобрено": {
                "handler": self.approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg"]
            },
            "#несмешно": {
                "handler": self.no_approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg", "type1"]
            },
            "#неcмешно": {
                "handler": self.no_approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "type1"]
            },
            "#плагиат": {
                "handler": self.no_approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg", "type2"]
            },
            "#плaгиат": {
                "handler": self.no_approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "type2"]
            },
            "#непрезентабельно": {
                "handler": self.no_approved_post_chat,
                "admin_only": True,
                "params": ["chat_id", "msg", "type3"]
            },
            "#нeпрезентабельно": {
                "handler": self._no_approved_post_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "type3"]
            },
            "#персональный ответ": {
                "handler": self.personal_response_for_chat,
                "admin_only": True,
                "params": ["user_id", "chat_id", "msg"]
            },
            "#пeрсональный ответ": {
                "handler": self.personal_response_for_ls,
                "admin_only": True,
                "params": ["chat_id", "msg", "user_id"]
            },
            "#мем": {
                "handler": self.enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#видео": {
                "handler": self.enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#клип": {
                "handler": self.enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#mem": {
                "handler": self.enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#video": {
                "handler": self.enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            },
            "#clip": {
                "handler": self.enter_post,
                "admin_only": False,
                "params": ["chat_id", "user_id", "event"]
            }
        }
        self.commands_for_posts_in_ls = {
            "#мем": {
                "handler": self.handle_enter_post_in_ls
            },
            "#видео": {
                "handler": self.handle_enter_post_in_ls
            },
            "#клип": {
                "handler": self.handle_enter_post_in_ls
            },
            "#mem": {
                "handler": self.handle_enter_post_in_ls
            },
            "#video": {
                "handler": self.handle_enter_post_in_ls
            },
            "#clip": {
                "handler": self.handle_enter_post_in_ls
            }
        }