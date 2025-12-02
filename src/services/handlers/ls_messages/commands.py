from src.services.handlers.posts.ls.models.processing_posts import CommandsForPostsInLS


class CommandsInLS(CommandsForPostsInLS):
    def __init__(self):
        self.commands_for_posts_admin = {
            "#шишки": {
                "handler": self.enter_post_ls
            }
        }