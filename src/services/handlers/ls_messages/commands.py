from src.services.handlers.posts.ls.models.posts import PostsModel


class CommandsInLS(PostsModel):
    def __init__(self):
        self.commands_for_posts_admin = {
            "#шишки": {
                "handler": self.handle_enter_post_in_ls
            }
        }