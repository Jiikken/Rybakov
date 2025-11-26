from src.services.handlers.ls_messages.models.posts import PostsModel


class CommandsInLS(PostsModel):
    def __init__(self):
        self.commands_for_posts = {
            "#шишки": {
                "handler": self.handle_enter_post_in_ls
            }
        }